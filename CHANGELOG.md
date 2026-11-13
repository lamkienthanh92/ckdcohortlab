# Changelog

## 1.3.0 – 2026-11-13
- Interface in five languages: English, Vietnamese, Japanese, Chinese and French, English by default; another language is chosen in the top bar or with `?lang=` in the address, and the choice is remembered.
- README in the same five languages.
- User data (file names, column names) are never translated.

## 1.2.0 – 2026-11-13
First public release, accompanying the manuscript on distribution-based albuminuria triage.
- Load Excel or CSV files; join a second file by patient ID; read unit columns row by row; recognise the analyser column.
- Distribution check before calculation: completeness, distributions, Excel date values, out-of-range values, duplicate IDs, ACR and eGFR cross-checks; cleaned CSV download.
- Results: KFRE and KDIGO 2024 categories; dipstick accuracy overall and by analyser; one predicted value versus predictive distribution; 80–99% intervals; random-split and cross-analyser validation; direct test costs; population versus individual agreement; plausibility flags.
- Python scripts that reproduce the manuscript tables and figures; synthetic example dataset.
