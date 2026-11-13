# Analysis scripts

`triage_analysis.py` computes every number in the manuscript from one CSV file; `make_figures.py` draws Figures 1–3 and Supplementary Figure S1.

## Input

One row per patient, header in the first row. Column names are case-insensitive.

| Column | Required | Accepted values |
|---|---|---|
| `id` | yes | any text |
| `age` | yes | years |
| `sex` | yes | F / M (also female / male) |
| `diabetes` | yes | 1 / 0 (also yes / no) |
| `egfr` | yes | mL/min/1.73 m²; rows with eGFR ≥60 are excluded |
| `acr_mg_g` | yes | urine albumin-to-creatinine ratio, mg/g |
| `dipstick_protein` | yes | Negative / Trace / 1+ / 2+ / 3+, or 0, 15, 30, 100, 300 (mg/dL), or 0.15, 0.3, 1, 3 (g/L) |
| `specific_gravity` | recommended | e.g. 1.015 |
| `analyser` | optional | analyser name; an analyser term is used when ≥2 analysers have ≥10 patients each |
| `urine_albumin_mg_L` | optional | enables the plausibility check of individual results |

The cleaned CSV downloaded from the browser tool is accepted as is. Row order is used for the enrolment-order split, so sort the file by enrolment date or study number.

## Options

```
python triage_analysis.py --data FILE.csv --out results \
    [--interval 90%] [--splits 2000] [--seed 2026] \
    [--acr-price 61200] [--strip-price 28600] [--strip-bought]
```

Prices default to Lanh Binh Thang General Hospital, 2025–2026 (VND). By default the dipstick is assumed to be done routinely and is not charged; add `--strip-bought` to charge it.

## Output

- `results/results.json` – all results: strip accuracy, models, decisions at 50–99% intervals, random splits, enrolment-order and cross-analyser validation, population vs individual agreement, plausibility flags, costs.
- `results/strategies.csv` – laboratory ACR needed, wrong decisions and cost for each strategy.
- `figures/Fig1–Fig3, FigS1` – PDF, PNG (200 dpi) and TIFF (600 dpi).

Tested with Python 3.12, NumPy 1.26–2.x, pandas 2.x, SciPy 1.11+, Matplotlib 3.8+.
