# CKD Cohort Lab

[English](README.md) · [Tiếng Việt](README.vi.md) · [日本語](README.ja.md) · [中文](README.zh.md) · **Français**

**Vérifiez un jeu de données rénales avant de l’analyser, puis déterminez qui a réellement besoin d’un dosage d’albuminurie au laboratoire.**

CKD Cohort Lab est un outil pour navigateur accompagné de scripts Python, associé au manuscrit *« One value or a distribution? Routine urine dipsticks to target albuminuria testing for kidney failure risk »* (soumis). L’étude porte sur 129 patients ambulatoires atteints de maladie rénale chronique (MRC) G3–G5 au Lanh Binh Thang General Hospital, Hô Chi Minh-Ville, Viêt Nam.

- **Outil en ligne :** https://ckdco.netlify.app/?lang=fr
- **Code source :** https://github.com/lamkienthanh92/ckdcohortlab
- **Archive et citation :** https://doi.org/10.5281/zenodo.24189503 (version 1.2.0 ; la page Zenodo liste toutes les versions)

> Outil de recherche et d’enseignement, et non un dispositif médical. L’équation de risque d’insuffisance rénale (KFRE) n’a pas été validée chez des patients vietnamiens.

## Ce que fait l’outil

L’interface est disponible en anglais, vietnamien, japonais, chinois et français. Choisissez la langue dans la barre supérieure, ou ajoutez `?lang=en`, `vi`, `ja`, `zh` ou `fr` à l’adresse ; l’anglais est la langue par défaut et le choix est mémorisé par le navigateur.

1. **Charger les données :** un fichier Excel (.xlsx, .xls, .ods) ou CSV, une ligne par patient. Un second fichier (par exemple les résultats de bandelette urinaire) peut être joint par identifiant patient. Les noms de colonnes courants (en anglais) sont associés automatiquement et modifiables à la main ; une colonne d’unité nommée « Unit <colonne> » (par exemple « Unit PRO ») est lue ligne par ligne.
2. **Vérifier la distribution :** chaque colonne est résumée avant tout calcul : complétude, distribution, valeurs stockées par Excel comme dates, valeurs hors limites, identifiants en double, RAC saisi versus albumine ÷ créatinine, DFGe saisi versus CKD-EPI 2021. Les données nettoyées peuvent être téléchargées en CSV.
3. **Résultats :** KFRE (4 variables, calibration non nord-américaine), catégories KDIGO 2024, précision de la bandelette par rapport au rapport albumine/créatinine (RAC), globalement et par analyseur, et le tri fondé sur la distribution :
   - le RAC de laboratoire n’est omis que si tout l’intervalle de prédiction du KFRE se situe d’un côté du seuil (5 ans ≥3 % et >5 % ; 2 ans >10 % et >40 %) ;
   - comparaison avec la conversion de la bandelette en une valeur unique de RAC ;
   - intervalles de 80/90/95/99 %, avec ou sans terme analyseur ;
   - validation par partitions aléatoires 70/30 et entre analyseurs ;
   - coûts directs des tests, avec prix modifiables ;
   - concordance du KFRE à 5 ans au niveau de la population et du patient ;
   - résultats d’albuminurie hors de l’intervalle à 99 %, pour revérifier l’identité de l’échantillon.

**Confidentialité :** les fichiers sont lus uniquement dans le navigateur. Rien n’est envoyé ni conservé sur un serveur ; fermer la page efface les données. Retirez les noms et autres identifiants avant le chargement.

Essayez avec `examples/example_synthetic.csv` (140 patients synthétiques, pas de données réelles).

## Reproduire les analyses du manuscrit

```bash
cd analysis
pip install -r requirements.txt
python triage_analysis.py --data ../examples/example_synthetic.csv --out results
python make_figures.py   --data ../examples/example_synthetic.csv --out figures
```

Sur les données de l’étude, les scripts reproduisent les chiffres publiés (par exemple : avec l’intervalle à 90 %, RAC de laboratoire nécessaire chez 66 patients sur 129, décision erronée chez 2 patients, contre 25 avec une valeur unique). Les données de l’étude ne sont pas incluses ; voir *Données*. Le format d’entrée et les options sont décrits (en anglais) dans `analysis/README.md`.

## Méthode en bref

Le log du RAC est prédit par moindres carrés à partir de l’âge, du sexe, du DFGe et du diabète (modèle clinique), puis du grade de protéines à la bandelette, de la densité et de l’analyseur (modèle bandelette), en validation croisée leave-one-out. L’intervalle de prédiction vaut valeur prédite ± z·s·√(1 + x′(X′X)⁻¹x). Le KFRE augmentant avec le RAC, il est calculé aux deux bornes de l’intervalle ; un seuil n’est décidé sans RAC de laboratoire que si les deux bornes tombent du même côté.

## Organisation du dépôt

| Chemin | Contenu |
|---|---|
| `index.html` | L’outil pour navigateur (un seul fichier, sans compilation) |
| `vendor/` | React 18.3.1 et SheetJS 0.18.5, inclus pour ne dépendre d’aucun serveur de scripts externe |
| `examples/` | Données d’exemple synthétiques et le script qui les a générées |
| `analysis/` | Scripts Python reproduisant les tableaux et figures du manuscrit |
| `netlify.toml` | Paramètres Netlify (site statique, sans compilation) |
| `CITATION.cff`, `.zenodo.json` | Métadonnées de citation pour GitHub et Zenodo |

## Données

Aucune donnée de patient n’est incluse. Le jeu de données anonymisé est disponible auprès de l’auteur correspondant sur demande raisonnable, sous réserve de l’accord du comité d’éthique du Lanh Binh Thang General Hospital.

## Citation

> Nguyen ATT, Pham TA, Phan HD, Phan TC, Lam TH, Huynh NH, Tran HNT, Lam TK, Le CV. CKD Cohort Lab: browser tool and analysis code for distribution-based albuminuria triage (version 1.3.0). Zenodo; 2026. https://doi.org/10.5281/zenodo.24189503

## Licence

Code : MIT (voir `LICENSE`). Les composants tiers conservent leur propre licence (voir `ATTRIBUTION.md`).
