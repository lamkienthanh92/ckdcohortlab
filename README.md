# CKD Cohort Lab

**English** · [Tiếng Việt](README.vi.md) · [日本語](README.ja.md) · [中文](README.zh.md) · [Français](README.fr.md)

**Check a kidney dataset before you analyse it, then decide who really needs a laboratory albuminuria test.**

CKD Cohort Lab is a browser tool and a set of Python scripts that accompany the manuscript
*"One value or a distribution? Routine urine dipsticks to target albuminuria testing for kidney failure risk"*
(submitted). The study used 129 outpatients with chronic kidney disease (CKD) G3–G5 at Lanh Binh Thang General Hospital, Ho Chi Minh City, Vietnam.

- **Live tool:** https://ckdco.netlify.app – [English](https://ckdco.netlify.app/?lang=en) · [Tiếng Việt](https://ckdco.netlify.app/?lang=vi) · [日本語](https://ckdco.netlify.app/?lang=ja) · [中文](https://ckdco.netlify.app/?lang=zh) · [Français](https://ckdco.netlify.app/?lang=fr)
- **Source code:** https://github.com/lamkienthanh92/ckdcohortlab
- **Archive and citation:** https://doi.org/10.5281/zenodo.24189503 (version 1.2.0; the Zenodo page lists all versions)

> Research and teaching tool, not a medical device. The kidney failure risk equation (KFRE) has not been validated in Vietnamese patients.

## What the browser tool does

The interface is available in English, Vietnamese, Japanese, Chinese and French. Choose the language in the top bar, or add `?lang=en`, `vi`, `ja`, `zh` or `fr` to the address; English is the default; the choice is remembered in the browser.


1. **Load data** – an Excel (.xlsx, .xls, .ods) or CSV file, one row per patient. A second file (for example urinalysis results) can be joined by patient ID. Common column names are matched automatically and the matching can be changed by hand; a unit column named "Unit <column>" (for example "Unit PRO") is read row by row.
2. **Check the distribution** – every column is summarised before anything is calculated: completeness, distributions, values stored by Excel as dates, values out of range, duplicate IDs, entered ACR against albumin ÷ creatinine, and entered eGFR against CKD-EPI 2021. A cleaned CSV can be downloaded.
3. **Results** – KFRE (4-variable, non-North American calibration), KDIGO 2024 categories, dipstick accuracy against ACR (overall and by analyser), and the distribution-based triage:
   - laboratory ACR is skipped only when the whole prediction interval of the KFRE lies on one side of a threshold (5-year ≥3% and >5%; 2-year >10% and >40%);
   - comparison with converting the dipstick into one predicted ACR value;
   - choice of 80/90/95/99% intervals, with or without an analyser term;
   - validation by random 70/30 splits and across analysers;
   - direct test costs with editable prices;
   - population vs individual agreement of 5-year KFRE;
   - urine albumin results outside the 99% interval, to double-check specimen identity.

**Privacy:** files are read in the browser only. Nothing is uploaded or stored on a server; closing the page clears the data. Remove names and other identifiers before loading.

Try it with `examples/example_synthetic.csv` (140 synthetic patients, not real data).

## Reproducing the manuscript analyses

```bash
cd analysis
pip install -r requirements.txt
python triage_analysis.py --data ../examples/example_synthetic.csv --out results
python make_figures.py   --data ../examples/example_synthetic.csv --out figures
```

On the study dataset the scripts reproduce the published numbers (for example: laboratory ACR needed in 66 of 129 patients with the 90% interval, 2 patients with a wrong decision, 25 with one predicted value). The study dataset is not included; see *Data* below. Input format and options are described in `analysis/README.md`.

## Method in brief

Log ACR is predicted by ordinary least squares from age, sex, eGFR and diabetes (clinical model), plus dipstick protein grade, specific gravity and analyser (strip model), using leave-one-out cross-validation. The prediction interval is the predicted value ± z·s·√(1 + x′(X′X)⁻¹x). Because KFRE increases with ACR, the KFRE is calculated at both ends of the interval; a threshold decision is made without laboratory ACR only when both ends fall on the same side.

## Repository

| Path | Content |
|---|---|
| `index.html` | The browser tool (single file; no build step) |
| `vendor/` | React 18.3.1 and SheetJS 0.18.5, bundled so the tool works without external script hosts |
| `examples/` | Synthetic example data and the script that generated it |
| `analysis/` | Python scripts that reproduce the manuscript tables and figures |
| `netlify.toml` | Netlify settings (static site, no build) |
| `CITATION.cff`, `.zenodo.json` | Citation metadata for GitHub and Zenodo |

## Data

No patient data are included. The de-identified study dataset is available from the corresponding author on reasonable request, subject to approval by the Institutional Review Board of Lanh Binh Thang General Hospital.

## Citation

If you use the tool or the code, please cite the archived release and the manuscript:

> Nguyen ATT, Pham TA, Phan HD, Phan TC, Lam TH, Huynh NH, Tran HNT, Lam TK, Le CV. CKD Cohort Lab: browser tool and analysis code for distribution-based albuminuria triage (version 1.3.0). Zenodo; 2026. https://doi.org/10.5281/zenodo.24189503

Citation metadata are in `CITATION.cff`.

## Licence

Code: MIT (see `LICENSE`). Third-party components keep their own licences (see `ATTRIBUTION.md`).
