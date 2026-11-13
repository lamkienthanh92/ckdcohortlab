"""Figures 1-3 and Supplementary Figure S1 of the companion manuscript.

Usage:
    python make_figures.py --data ../examples/example_synthetic.csv --out figures
Writes PDF, PNG (200 dpi) and TIFF (600 dpi, LZW) for each figure.
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

import triage_analysis as ta

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.linewidth": 0.7, "legend.fontsize": 6.6, "xtick.labelsize": 7.3, "ytick.labelsize": 7.3})
BLUE, ORANGE, RED, GREY, INK, LIGHT = "#2350B8", "#D9822B", "#C0392B", "#8A97A8", "#142030", "#A5B9E6"
W = 174 / 25.4
NUM = FuncFormatter(lambda v, p: f"{v:g}")
PCT = FuncFormatter(lambda v, p: f"{v:g}%")


def panel(ax, letter, x=-0.16):
    ax.text(x, 1.04, letter, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom")


def save(fig, out, name):
    for ext, kw in [("pdf", {}), ("png", {"dpi": 200}), ("tif", {"dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}})]:
        fig.savefig(os.path.join(out, f"{name}.{ext}"), **kw)
    plt.close(fig)


def roc_points(score, truth):
    cuts = sorted(set(score), reverse=True)
    P, N = truth.sum(), (~truth).sum()
    return np.array([[0, 0]] + [[((score >= c) & ~truth).sum() / N, ((score >= c) & truth).sum() / P] for c in cuts] + [[1, 1]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="figures")
    ap.add_argument("--splits", type=int, default=2000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = ta.load(a.data)
    R, P = ta.run(d, splits=a.splits)
    n = len(d)
    y = np.log(d.acr.values)
    levels = R["inputs"]["analysers"] or []
    colours = [BLUE, ORANGE, "#1E7F55", "#7A4FB0"]

    # ---------------- Figure 1: strip and ACR
    fig, axs = plt.subplots(2, 2, figsize=(W, 5.9))
    ax = axs[0, 0]
    rng = np.random.default_rng(3)
    groups = levels if levels and R["inputs"]["analyser_term"] else ["All"]
    offs = np.linspace(-0.18, 0.18, len(groups)) if len(groups) > 1 else [0]
    for j, g in enumerate(ta.GRADES):
        for k, lv in enumerate(groups):
            m = (d.grade.values == g) & ((d.analyser.values == lv) if lv != "All" else True)
            v = d.acr.values[m]
            ax.scatter(j + offs[k] + rng.uniform(-0.08, 0.08, m.sum()), v, s=9, color=colours[k % 4], alpha=0.75, lw=0)
            if m.sum():
                ax.plot([j + offs[k] - 0.12, j + offs[k] + 0.12], [np.median(v)] * 2, color=INK, lw=1.6)
    for t in (30, 300):
        ax.axhline(t, color=GREY, ls="--", lw=0.7)
    ax.set_yscale("log"); ax.yaxis.set_major_formatter(NUM)
    ax.set_xticks(range(5)); ax.set_xticklabels([ta.GRADE_LABEL[g] for g in ta.GRADES])
    ax.set_xlabel("Strip protein grade"); ax.set_ylabel("Urine ACR (mg/g)")
    for k, lv in enumerate(groups):
        ax.scatter([], [], s=12, color=colours[k % 4], label=f"{lv} (n = {int((d.analyser == lv).sum()) if lv != 'All' else n})")
    ax.legend(frameon=False, loc="upper left"); panel(ax, "a")
    ax = axs[0, 1]
    for t, col in [(30, BLUE), (300, RED)]:
        pts = roc_points(d.grade.values, d.acr.values >= t)
        A = R["strip"]["auc30" if t == 30 else "auc300"]
        ax.plot(pts[:, 0], pts[:, 1], "-o", color=col, ms=3, lw=1.5, label=f"ACR ≥{t} mg/g: AUC {A[0]:.2f} ({A[1]:.2f}–{A[2]:.2f})")
    ax.plot([0, 1], [0, 1], ":", color=GREY, lw=0.8)
    ax.set_xlabel("1 − specificity"); ax.set_ylabel("Sensitivity"); ax.legend(frameon=False, loc="lower right")
    ax.set_aspect("equal", adjustable="box"); panel(ax, "b")
    for ax, key, title in [(axs[1, 0], "clin", "Clinical data only"), (axs[1, 1], "strip", "Clinical data + strip")]:
        p = P[f"pred_{key}"]
        ax.scatter(np.exp(p), d.acr.values, s=9, color=GREY if key == "clin" else BLUE, alpha=0.8, lw=0)
        ax.plot([0.5, 5000], [0.5, 5000], "--", color=INK, lw=0.8)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(0.5, 5000); ax.set_ylim(0.4, 6000)
        ax.xaxis.set_major_formatter(NUM); ax.yaxis.set_major_formatter(NUM)
        r2 = R["models"]["clinical" if key == "clin" else "strip"]["loo_r2"]
        ax.set_title(f"{title}   R² = {r2:.2f}", loc="left", fontsize=8)
        ax.set_xlabel("Predicted ACR, leave-one-out (mg/g)"); ax.set_ylabel("Measured ACR (mg/g)")
    panel(axs[1, 0], "c"); panel(axs[1, 1], "d")
    fig.tight_layout(); save(fig, a.out, "Fig1")

    # ---------------- Figure 2: one value vs distribution
    r5 = ta.kfre(d.age.values, d.female.values, d.egfr.values, y, 0.9365) * 100
    r5s = ta.kfre(d.age.values, d.female.values, d.egfr.values, P["pred_strip"], 0.9365) * 100
    band = lambda v: np.where(v < 3, 0, np.where(v <= 5, 1, 2))
    ch = band(r5) != band(r5s)
    fig = plt.figure(figsize=(W, 5.6))
    outer = fig.add_gridspec(2, 2, width_ratios=[1.12, 1], wspace=0.42, hspace=0.55, left=0.08, right=0.98, top=0.95, bottom=0.1)
    sub = outer[:, 0].subgridspec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4], wspace=0.05, hspace=0.05)
    ax = fig.add_subplot(sub[1, 0]); axt = fig.add_subplot(sub[0, 0], sharex=ax); axr = fig.add_subplot(sub[1, 1], sharey=ax)
    lo, hi = 0.02, 100
    for t in (3, 5):
        ax.axvline(t, color=GREY, lw=0.6, ls=":"); ax.axhline(t, color=GREY, lw=0.6, ls=":")
    ax.plot([lo, hi], [lo, hi], "--", color=INK, lw=1)
    ax.scatter(r5[~ch], r5s[~ch], s=11, color=BLUE, alpha=0.7, lw=0, label="Same 5-year band")
    ax.scatter(r5[ch], r5s[ch], s=20, color=RED, lw=0, label=f"Different band (n = {ch.sum()})")
    q = np.linspace(0.01, 0.99, 99)
    ax.plot(np.quantile(r5, q), np.quantile(r5s, q), color=ORANGE, lw=2.2, label="Quantile–quantile line")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.xaxis.set_major_formatter(PCT); ax.yaxis.set_major_formatter(PCT)
    ax.set_xlabel("5-year KFRE from measured ACR"); ax.set_ylabel("5-year KFRE from one strip-based value")
    ax.legend(frameon=False, loc="upper left", fontsize=6.3)
    bins = np.logspace(np.log10(lo), np.log10(hi), 30)
    axt.hist(r5, bins=bins, color=INK, alpha=0.75); axr.hist(r5s, bins=bins, orientation="horizontal", color=BLUE, alpha=0.8)
    axt.tick_params(labelbottom=False); axr.tick_params(labelleft=False)
    pv = R["population_vs_individual"]
    ax.text(0.97, 0.03, f"Kolmogorov–Smirnov P = {pv['ks_p']:.2f}\nLimits of agreement ×{pv['loa_ratio'][0]:.2f} to ×{pv['loa_ratio'][1]:.2f}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.2)
    axt.text(-0.2, 1.15, "a", transform=axt.transAxes, fontsize=11, fontweight="bold")
    ax = fig.add_subplot(outer[0, 1])
    for key, col in [("clinical", GREY), ("strip", BLUE)]:
        bi = R["models"][key]["by_interval"]
        xs = [100 * (1 - bi[k]["need"] / n) for k in ta.Z]; ys = [bi[k]["wrong"] for k in ta.Z]
        ax.plot(xs, ys, "-o", color=col, ms=3.5, lw=1.2, label=("Clinical data" if key == "clinical" else "Clinical data + strip") + ", distribution")
        ax.plot([100 if key == "strip" else 96], [R["models"][key]["single_value"]["wrong"]], "s" if key == "strip" else "D",
                color=RED if key == "strip" else "white", markeredgecolor=RED, ms=5, label=("Strip" if key == "strip" else "Clinical data") + ", one value")
        if key == "strip":
            for xx, yy, t in zip(xs, ys, ta.Z):
                ax.annotate(t, (xx, yy), xytext=(3, -10), textcoords="offset points", fontsize=6, color=col)
    ax.set_xlim(0, 104); ax.set_xlabel("Laboratory ACR tests avoided (%)"); ax.set_ylabel("Patients with ≥1\nwrong decision")
    ax.legend(frameon=False, fontsize=6, loc="upper left"); panel(ax, "b")
    ax = fig.add_subplot(outer[1, 1])
    per_s = R["models"]["strip"]["by_interval"]["90%"]["per_threshold"]; per_c = R["models"]["clinical"]["by_interval"]["90%"]["per_threshold"]
    labels = [p["threshold"] for p in per_s] + ["Any of the four"]
    vc = [p["need_acr"] for p in per_c] + [R["models"]["clinical"]["by_interval"]["90%"]["need"]]
    vs = [p["need_acr"] for p in per_s] + [R["models"]["strip"]["by_interval"]["90%"]["need"]]
    xx = np.arange(len(labels))
    ax.bar(xx - 0.19, vc, 0.38, color=LIGHT, label="Clinical data only"); ax.bar(xx + 0.19, vs, 0.38, color=BLUE, label="Clinical data + strip")
    ax.set_xticks(xx); ax.set_xticklabels([l.replace(" ", "\n", 1) for l in labels], fontsize=6.3)
    ax.set_ylabel("Patients needing\nlaboratory ACR"); ax.legend(frameon=False, fontsize=6.2, loc="upper left"); panel(ax, "c")
    save(fig, a.out, "Fig2")

    # ---------------- Figure 3: validation and cost
    fig = plt.figure(figsize=(W, 5.6))
    top, bot = fig.subfigures(2, 1, height_ratios=[1, 0.8])
    ax, ax2 = top.subplots(1, 2, gridspec_kw={"wspace": 0.42})
    S = R["random_splits"]; L = max(len(S["wrong_distribution"]), len(S["single_value_wrong_distribution"]))
    dw = np.pad(S["wrong_distribution"], (0, L - len(S["wrong_distribution"]))); pw = np.pad(S["single_value_wrong_distribution"], (0, L - len(S["single_value_wrong_distribution"])))
    ax.bar(np.arange(L) - 0.2, 100 * dw / S["n"], 0.4, color=BLUE, label="Distribution, 90% interval")
    ax.bar(np.arange(L) + 0.2, 100 * pw / S["n"], 0.4, color=RED, label="One predicted value")
    ax.set_xlabel(f"Patients with ≥1 wrong decision (of {S['test_size']} tested)"); ax.set_ylabel(f"Share of {S['n']:,} splits (%)")
    ax.legend(frameon=False, loc="upper right"); panel(ax, "a")
    schemes = [("All, leave-\none-out", R["models"]["strip"]["by_interval"]["90%"]["wrong"] / n, R["models"]["strip"]["single_value"]["wrong"] / n),
               ("Last 30%\nenrolled", R["enrolment_order"]["wrong"] / R["enrolment_order"]["test_size"], R["enrolment_order"]["single_value_wrong"] / R["enrolment_order"]["test_size"])]
    for c in R.get("cross_analyser", []):
        schemes.append((f"{c['fitted_on']} →\n{c['tested_on']}", c["wrong"] / c["n"], c["single_value_wrong"] / c["n"]))
    xx = np.arange(len(schemes))
    ax2.bar(xx - 0.2, [100 * s[1] for s in schemes], 0.4, color=BLUE, label="Distribution, 90% interval")
    ax2.bar(xx + 0.2, [100 * s[2] for s in schemes], 0.4, color=RED, label="One predicted value")
    ax2.set_xticks(xx); ax2.set_xticklabels([s[0] for s in schemes], fontsize=6.2); ax2.set_ylabel("Patients with ≥1 wrong decision (%)")
    ax2.legend(frameon=False, loc="upper left"); panel(ax2, "b")
    ax = bot.subplots(1, 1); bot.subplots_adjust(left=0.36, right=0.95, bottom=0.22, top=0.85)
    C = R["cost_per_100"]
    strat = [("Laboratory ACR for every patient", C["acr_for_all"]), ("Distribution, clinical data (90%)", C["clinical_distribution"]),
             ("Distribution, clinical data + strip (90%)", C["strip_distribution"]), ("One predicted value from the strip", C["strip_single_value"])]
    yy = np.arange(len(strat))[::-1]
    ax.barh(yy, [v / 1e6 for _, v in strat], 0.55, color=BLUE)
    for yv, (_, v) in zip(yy, strat):
        ax.text(v / 1e6 + 0.05, yv, f"{v / 1e6:.2f}", va="center", fontsize=6.8)
    ax.set_yticks(yy); ax.set_yticklabels([s for s, _ in strat]); ax.set_xlabel("Cost of testing per 100 patients (millions)")
    ax.text(-0.42, 1.06, "c", transform=ax.transAxes, fontsize=11, fontweight="bold")
    save(fig, a.out, "Fig3")

    # ---------------- Figure S1: plausibility
    if "plausibility_flags" in R:
        Xs = ta.design(d, analyser=R["inputs"]["analyser_term"], levels=levels)
        la = np.log(d.alb.values); pa, sa = ta.loo(Xs, la); zq = (la - pa) / sa; f = np.abs(zq) > 2.576
        fig, ax = plt.subplots(figsize=(W * 0.62, 3.2))
        ax.scatter(np.exp(pa)[~f], zq[~f], s=10, color=BLUE, alpha=0.7, lw=0, label="Within the 99% interval")
        ax.scatter(np.exp(pa)[f], zq[f], s=22, color=ORANGE, lw=0, label="Outside the 99% interval")
        for i in np.where(f)[0]:
            ax.annotate(d.id[i], (np.exp(pa[i]), zq[i]), xytext=(4, 3), textcoords="offset points", fontsize=6.2)
        for t in (2.576, -2.576):
            ax.axhline(t, color=GREY, ls="--", lw=0.8)
        ax.set_xscale("log"); ax.xaxis.set_major_formatter(NUM)
        ax.set_xlabel("Predicted urine albumin, leave-one-out (mg/L)"); ax.set_ylabel("Standardised residual")
        ax.legend(frameon=False, fontsize=6.5); fig.tight_layout(); save(fig, a.out, "FigS1")
    print(f"Figures written to {a.out}/")


if __name__ == "__main__":
    main()
