"""Distribution-based triage of laboratory albuminuria testing for KFRE decisions.

Reproduces the analyses of the companion manuscript from one CSV file:
strip accuracy, leave-one-out prediction of log ACR, the prediction-interval
decision rule at four KDIGO 2024 / NICE thresholds, validation (random 70/30
splits, enrolment order, cross-analyser), population vs individual agreement,
plausibility flags and direct test costs.

Usage:
    python triage_analysis.py --data ../examples/example_synthetic.csv --out results

Input columns (case-insensitive; see analysis/README.md for accepted values):
    id, age, sex, diabetes, egfr, acr_mg_g, dipstick_protein, specific_gravity,
    analyser (optional), urine_albumin_mg_L (optional, for plausibility flags)
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

GRADES = [0, 15, 30, 100, 300]                      # mg/dL: negative, trace, 1+, 2+, 3+
GRADE_LABEL = {0: "Negative", 15: "Trace", 30: "1+", 100: "2+", 300: "3+"}
THRESHOLDS = [("5-year >=3%", 0.9365, 0.03, True), ("5-year >5%", 0.9365, 0.05, False),
              ("2-year >10%", 0.9832, 0.10, False), ("2-year >40%", 0.9832, 0.40, False)]
Z = {"50%": 0.674, "80%": 1.282, "90%": 1.645, "95%": 1.960, "99%": 2.576}


# ---------------------------------------------------------------- input
def _col(df, *names):
    low = {c.lower(): c for c in df.columns}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    return None


def _grade(v):
    """Dipstick protein as a grade in mg/dL (0, 15, 30, 100, 300)."""
    if pd.isna(v):
        return np.nan
    s = str(v).strip().lower()
    words = {"negative": 0, "neg": 0, "-": 0, "trace": 15, "+-": 15,
             "1+": 30, "2+": 100, "3+": 300, "4+": 300}
    if s in words:
        return words[s]
    try:
        x = float(s)
    except ValueError:
        return np.nan
    if 0 < x <= 5:                                   # g/L (0.15, 0.3, 1, 3) -> mg/dL
        x *= 100
    return min(GRADES, key=lambda g: abs(g - x))


def _yesno(series, yes, no):
    s = series.astype(str).str.strip().str.lower()
    return s.map(lambda v: 1 if v in yes else (0 if v in no else np.nan))


def load(path):
    raw = pd.read_csv(path)
    c = lambda *n: _col(raw, *n)
    d = pd.DataFrame()
    d["id"] = raw[c("id", "patient_id", "study_id")].astype(str)
    d["age"] = pd.to_numeric(raw[c("age")], errors="coerce")
    d["female"] = _yesno(raw[c("sex", "gender")], ("f", "female", "1"), ("m", "male", "0"))
    d["dm"] = _yesno(raw[c("diabetes", "dm")], ("1", "yes", "true"), ("0", "no", "false"))
    d["egfr"] = pd.to_numeric(raw[c("egfr", "egfr_entered", "egfr_ckdepi2021")], errors="coerce")
    d["acr"] = pd.to_numeric(raw[c("acr_mg_g", "acr", "acr_entered_mg_g", "acr_from_albumin_mg_g")], errors="coerce")
    d["grade"] = raw[c("dipstick_protein", "protein", "pro")].map(_grade)
    sg = c("specific_gravity", "sg")
    d["sg"] = pd.to_numeric(raw[sg], errors="coerce") if sg else np.nan
    an = c("analyser", "analyzer", "device")
    d["analyser"] = raw[an].astype(str).replace({"nan": np.nan, "": np.nan}) if an else np.nan
    ua = c("urine_albumin_mg_l", "urine_albumin")
    d["alb"] = pd.to_numeric(raw[ua], errors="coerce") if ua else np.nan
    keep = d[["age", "female", "dm", "egfr", "acr", "grade"]].notna().all(axis=1) & (d.acr > 0) & (d.egfr < 60)
    if d["sg"].notna().any():
        keep &= d["sg"].notna()
    out = d[keep].reset_index(drop=True)
    print(f"Loaded {len(d)} rows; analysed {len(out)} (eGFR <60 mL/min/1.73 m2, complete data)")
    return out


# ---------------------------------------------------------------- core
def kfre(age, female, egfr, log_acr, s0):
    """Four-variable KFRE, non-North American calibration (s0 = baseline survival)."""
    male = 1 - female
    lp = (-0.2201 * (age / 10 - 7.036) + 0.2467 * (male - 0.5642)
          - 0.5567 * (egfr / 5 - 7.222) + 0.4510 * (log_acr - 5.137))
    return 1 - s0 ** np.exp(lp)


def over(r, t, ge):
    return r >= t if ge else r > t


def design(d, strip=True, analyser=True, levels=None):
    cols = [np.ones(len(d)), d.age.values, 1 - d.female.values, d.egfr.values, d.dm.values]
    if strip:
        cols += [(d.grade.values == g).astype(float) for g in GRADES[1:] if (d.grade == g).sum() >= 2]
        if d.sg.notna().all():
            cols.append(d.sg.values)
        if analyser and levels is not None and len(levels) >= 2:
            cols += [(d.analyser.values == lv).astype(float) for lv in levels[1:]]
    return np.column_stack(cols)


def loo(X, y):
    """Leave-one-out prediction and prediction standard error from OLS."""
    n, p = X.shape
    pred, se = np.zeros(n), np.zeros(n)
    for i in range(n):
        k = np.arange(n) != i
        A = X[k].T @ X[k]
        b = np.linalg.solve(A, X[k].T @ y[k])
        r = y[k] - X[k] @ b
        s2 = r @ r / (k.sum() - p)
        pred[i] = X[i] @ b
        se[i] = np.sqrt(s2 * (1 + X[i] @ np.linalg.solve(A, X[i])))
    return pred, se


def fit_predict(Xtr, ytr, Xte):
    A = Xtr.T @ Xtr + 1e-8 * np.eye(Xtr.shape[1])
    b = np.linalg.solve(A, Xtr.T @ ytr)
    r = ytr - Xtr @ b
    s2 = r @ r / (len(ytr) - Xtr.shape[1])
    pred = Xte @ b
    se = np.sqrt(s2 * (1 + np.einsum("ij,ij->i", Xte, np.linalg.solve(A, Xte.T).T)))
    return pred, se


def decide(d, idx, pred, se, z):
    """Decision rule. z = 0 means one predicted value used without laboratory ACR."""
    y = np.log(d.acr.values[idx])
    a, f, e = d.age.values[idx], d.female.values[idx], d.egfr.values[idx]
    und = np.zeros(len(idx), bool)
    err = np.zeros(len(idx), bool)
    per = []
    for lab, s0, t, ge in THRESHOLDS:
        truth = over(kfre(a, f, e, y, s0), t, ge)
        if z == 0:
            c = over(kfre(a, f, e, pred, s0), t, ge)
            err |= c != truth
            per.append(dict(threshold=lab, decided=len(idx), correct=int((c == truth).sum()), need_acr=0))
            continue
        lo = over(kfre(a, f, e, pred - z * se, s0), t, ge)
        hi = over(kfre(a, f, e, pred + z * se, s0), t, ge)
        dd = lo | ~hi
        und |= ~dd
        err |= dd & (lo != truth)
        per.append(dict(threshold=lab, decided=int(dd.sum()), correct=int((dd & (lo == truth)).sum()),
                        need_acr=int((~dd).sum())))
    return dict(need=int(und.sum()), wrong=int(err.sum()), wrong_ids=list(d.id.values[idx][err]), per_threshold=per)


def wilson(k, n, z=1.96):
    if n == 0:
        return [np.nan] * 3
    p = k / n
    dd = 1 + z * z / n
    c = (p + z * z / (2 * n)) / dd
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return [p, max(0, c - h), min(1, c + h)]


def auc(score, truth):
    """Mann-Whitney AUC with Hanley-McNeil 95% CI."""
    pos, neg = score[truth], score[~truth]
    if len(pos) == 0 or len(neg) == 0:
        return [np.nan] * 3
    A = np.mean([(a > b) + 0.5 * (a == b) for a in pos for b in neg])
    q1, q2 = A / (2 - A), 2 * A * A / (1 + A)
    se = np.sqrt((A * (1 - A) + (len(pos) - 1) * (q1 - A * A) + (len(neg) - 1) * (q2 - A * A)) / (len(pos) * len(neg)))
    return [A, A - 1.96 * se, min(1, A + 1.96 * se)]


# ---------------------------------------------------------------- analysis
def run(d, interval="90%", splits=2000, seed=2026, acr_price=61200, strip_price=28600, strip_routine=True):
    n = len(d)
    y = np.log(d.acr.values)
    idx = np.arange(n)
    z = Z[interval]
    levels = sorted(d.analyser.dropna().unique()) if d.analyser.notna().all() else None
    use_an = bool(levels) and len(levels) >= 2 and min((d.analyser == lv).sum() for lv in levels) >= 10
    R = {"n": n, "interval": interval}

    # strip against ACR
    acc = []
    for cut, cl in [(15, ">= trace"), (30, ">= 1+"), (100, ">= 2+"), (300, "3+")]:
        for t in (30, 300):
            p = d.grade.values >= cut
            q = d.acr.values >= t
            acc.append(dict(strip=cl, target=f"ACR >={t}", sensitivity=wilson((p & q).sum(), q.sum()),
                            specificity=wilson((~p & ~q).sum(), (~q).sum()), ppv=wilson((p & q).sum(), p.sum()),
                            npv=wilson((~p & ~q).sum(), (~p).sum())))
    R["strip"] = dict(spearman=float(stats.spearmanr(d.grade, d.acr).statistic),
                      auc30=auc(d.grade.values, d.acr.values >= 30), auc300=auc(d.grade.values, d.acr.values >= 300),
                      accuracy=acc,
                      median_acr_by_grade={GRADE_LABEL[g]: float(d.acr[d.grade == g].median()) for g in GRADES if (d.grade == g).any()})

    # prediction models and decisions
    Xc = design(d, strip=False)
    Xs = design(d, analyser=use_an, levels=levels)
    pc, sc = loo(Xc, y)
    ps, ss = loo(Xs, y)
    r2 = lambda p: float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    cov = lambda p, s: float(np.mean(np.abs(y - p) <= 1.645 * s))
    R["models"] = {}
    for name, p, s in [("clinical", pc, sc), ("strip", ps, ss)]:
        R["models"][name] = dict(loo_r2=r2(p), coverage90=cov(p, s),
                                 by_interval={k: decide(d, idx, p, s, v) for k, v in Z.items()},
                                 single_value=decide(d, idx, p, s, 0))

    # validation: random 70/30 splits
    rng = np.random.default_rng(seed)
    res = []
    k = int(round(0.7 * n))
    for _ in range(splits):
        perm = rng.permutation(n)
        tr, te = perm[:k], perm[k:]
        try:
            p, s = fit_predict(Xs[tr], y[tr], Xs[te])
        except np.linalg.LinAlgError:
            continue
        dd = decide(d, te, p, s, z)
        res.append([1 - dd["need"] / len(te), dd["wrong"], decide(d, te, p, s, 0)["wrong"],
                    float(np.mean(np.abs(y[te] - p) <= 1.645 * s))])
    res = np.array(res)
    R["random_splits"] = dict(
        n=len(res), test_size=n - k, avoided_median=float(np.median(res[:, 0])),
        avoided_2_5=float(np.percentile(res[:, 0], 2.5)), avoided_97_5=float(np.percentile(res[:, 0], 97.5)),
        wrong_median=float(np.median(res[:, 1])), share_0_wrong=float(np.mean(res[:, 1] == 0)),
        share_le1_wrong=float(np.mean(res[:, 1] <= 1)), single_value_wrong_median=float(np.median(res[:, 2])),
        coverage90_median=float(np.median(res[:, 3])),
        wrong_distribution=np.bincount(res[:, 1].astype(int)).tolist(),
        single_value_wrong_distribution=np.bincount(res[:, 2].astype(int)).tolist())

    # validation: enrolment order (row order of the file)
    p, s = fit_predict(Xs[:k], y[:k], Xs[k:])
    dd = decide(d, np.arange(k, n), p, s, z)
    R["enrolment_order"] = dict(test_size=n - k, avoided=1 - dd["need"] / (n - k), wrong=dd["wrong"],
                                single_value_wrong=decide(d, np.arange(k, n), p, s, 0)["wrong"])

    # validation: across analysers (model without the analyser term)
    if use_an:
        Xn = design(d, analyser=False)
        R["cross_analyser"] = []
        for a in levels:
            for b in levels:
                if a == b:
                    continue
                tr = np.where(d.analyser == a)[0]
                te = np.where(d.analyser == b)[0]
                p, s = fit_predict(Xn[tr], y[tr], Xn[te])
                dd = decide(d, te, p, s, z)
                R["cross_analyser"].append(dict(fitted_on=a, tested_on=b, n=len(te), avoided=1 - dd["need"] / len(te),
                                                wrong=dd["wrong"], single_value_wrong=decide(d, te, p, s, 0)["wrong"],
                                                coverage90=float(np.mean(np.abs(y[te] - p) <= 1.645 * s))))

    # population distribution vs individual agreement (5-year KFRE)
    r5 = kfre(d.age.values, d.female.values, d.egfr.values, y, 0.9365)
    r5s = kfre(d.age.values, d.female.values, d.egfr.values, ps, 0.9365)
    lr = np.log10(r5s / r5)
    band = lambda v: np.where(v < 0.03, 0, np.where(v <= 0.05, 1, 2))
    R["population_vs_individual"] = dict(
        ks_p=float(stats.ks_2samp(r5s, r5).pvalue), median_measured=float(np.median(r5)), median_strip=float(np.median(r5s)),
        loa_ratio=[float(10 ** (lr.mean() - 1.96 * lr.std(ddof=1))), float(10 ** (lr.mean() + 1.96 * lr.std(ddof=1)))],
        band_changes=int((band(r5s) != band(r5)).sum()))

    # plausibility of individual urine albumin results
    if d.alb.notna().all() and (d.alb > 0).all():
        la = np.log(d.alb.values)
        pa, sa = loo(Xs, la)
        zq = (la - pa) / sa
        R["plausibility_flags"] = [dict(id=d.id[i], strip=GRADE_LABEL[d.grade[i]], analyser=d.analyser[i],
                                        albumin_mg_L=float(d.alb[i]), expected_low=float(np.exp(pa[i] - 2.576 * sa[i])),
                                        expected_high=float(np.exp(pa[i] + 2.576 * sa[i])), z=float(zq[i]))
                                   for i in np.where(np.abs(zq) > 2.576)[0]]

    # direct test costs per 100 patients
    sp = 0 if strip_routine else strip_price
    cost = lambda need, uses_strip: (need * acr_price + (n * sp if uses_strip else 0)) / n * 100
    M = R["models"]
    R["cost_per_100"] = {"acr_for_all": cost(n, False),
                         "clinical_distribution": cost(M["clinical"]["by_interval"][interval]["need"], False),
                         "strip_distribution": cost(M["strip"]["by_interval"][interval]["need"], True),
                         "strip_single_value": cost(0, True)}
    R["inputs"] = dict(acr_price=acr_price, strip_price=strip_price, strip_routine=strip_routine,
                       analyser_term=bool(use_an), analysers=levels)
    return R, dict(pred_clin=pc, se_clin=sc, pred_strip=ps, se_strip=ss)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="CSV file, one row per patient")
    ap.add_argument("--out", default="results", help="output folder")
    ap.add_argument("--interval", default="90%", choices=list(Z))
    ap.add_argument("--splits", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--acr-price", type=float, default=61200, help="price of one laboratory ACR")
    ap.add_argument("--strip-price", type=float, default=28600, help="price of one dipstick urinalysis")
    ap.add_argument("--strip-bought", action="store_true", help="charge the strip (default: done routinely)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = load(a.data)
    R, _ = run(d, a.interval, a.splits, a.seed, a.acr_price, a.strip_price, not a.strip_bought)
    with open(os.path.join(a.out, "results.json"), "w") as f:
        json.dump(R, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    s, c, iv, n = R["models"]["strip"], R["models"]["clinical"], R["interval"], R["n"]
    strip_cost = 0 if not a.strip_bought else a.strip_price * 100
    rows = [("Laboratory ACR for every patient", n, 0, R["cost_per_100"]["acr_for_all"]),
            ("One predicted value, strip", 0, s["single_value"]["wrong"], R["cost_per_100"]["strip_single_value"]),
            (f"Distribution, clinical data, {iv} interval", c["by_interval"][iv]["need"], c["by_interval"][iv]["wrong"],
             R["cost_per_100"]["clinical_distribution"])]
    rows += [(f"Distribution, strip, {k} interval", v["need"], v["wrong"], v["need"] * a.acr_price / n * 100 + strip_cost)
             for k, v in s["by_interval"].items()]
    pd.DataFrame(rows, columns=["strategy", "laboratory_acr_needed", "patients_with_wrong_decision",
                                "cost_per_100_patients"]).to_csv(os.path.join(a.out, "strategies.csv"), index=False)
    st, rs = R["strip"], R["random_splits"]
    print(f"\nStrip vs ACR: rho {st['spearman']:.2f}; AUC ACR>=30 {st['auc30'][0]:.2f}, ACR>=300 {st['auc300'][0]:.2f}")
    print(f"Leave-one-out R2: clinical {c['loo_r2']:.2f}, strip {s['loo_r2']:.2f}; 90% interval coverage {s['coverage90']:.0%}")
    print(f"{iv} interval, strip model: laboratory ACR needed {s['by_interval'][iv]['need']} of {n}, "
          f"wrong decisions {s['by_interval'][iv]['wrong']}; one predicted value: wrong {s['single_value']['wrong']}")
    print(f"Random 70/30 splits: ACR avoided {rs['avoided_median']:.0%} ({rs['avoided_2_5']:.0%}-{rs['avoided_97_5']:.0%}), "
          f"wrong median {rs['wrong_median']:.0f}, at most one wrong in {rs['share_le1_wrong']:.0%} of splits")
    print(f"Cost per 100 patients: ACR for all {R['cost_per_100']['acr_for_all']:,.0f}; "
          f"strip distribution {R['cost_per_100']['strip_distribution']:,.0f}")
    print(f"\nSaved {a.out}/results.json and {a.out}/strategies.csv")


if __name__ == "__main__":
    main()
