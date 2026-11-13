# Publishing: GitHub, Netlify and a Zenodo DOI

Before anything else, confirm the author list, order, affiliations and ORCID iDs in `.zenodo.json` and `CITATION.cff` (and the copyright line in `LICENSE`). A Zenodo record cannot be deleted after publication.

## 1. GitHub
1. Create a public repository, for example `ckd-cohort-lab`, without README, licence or .gitignore (they are included).
2. Upload the contents of this folder (not the folder itself): drag the files into "Add file → Upload files", or:
   ```bash
   cd ckd-cohort-lab
   git init
   git add .
   git commit -m "CKD Cohort Lab v1.2.0"
   git branch -M main
   git remote add origin https://github.com/YOUR-USER/ckd-cohort-lab.git
   git push -u origin main
   ```
3. In `CITATION.cff`, replace `YOUR-USER` in `repository-code` with your account name.

## 2. Netlify
1. Sign in at https://app.netlify.com with GitHub → "Add new site → Import an existing project → GitHub" → choose the repository.
2. Leave the build command empty; the publish directory is `.` (set in `netlify.toml`). Deploy.
3. Rename the site under "Site configuration → Change site name" (for example `ckdcohortlab`), then put the address in `README.md` and `CITATION.cff`.

Without GitHub: drag this folder onto https://app.netlify.com/drop.

## 3. Zenodo DOI

### Route A: GitHub integration (recommended)
1. Sign in at https://zenodo.org with GitHub (https://sandbox.zenodo.org for a test run; sandbox DOIs are not real).
2. In your Zenodo account settings, open GitHub and switch the repository **on**.
3. On GitHub: "Releases → Draft a new release", tag `v1.2.0`, title `CKD Cohort Lab v1.2.0`, publish.
4. Zenodo archives the release and mints a DOI from `.zenodo.json`. Check the record.
5. Replace `10.5281/zenodo.XXXXXXX` in `README.md` and `CITATION.cff` with the DOI, and commit. Zenodo also gives a concept DOI for all versions.

### Route B: manual upload
1. https://zenodo.org → "+" → New upload. Answer "No" to the DOI question and press **Get a DOI now!**, then **Save draft**.
2. Put the reserved DOI into `README.md` and `CITATION.cff`, zip the folder as `ckd-cohort-lab-v1.2.0.zip` and upload it.
3. Fill in the form from `.zenodo.json`: resource type *Software*; title; creators and affiliations; description; licence *MIT License* (remove the default CC BY 4.0); version 1.2.0; keywords. Publish.

## 4. After the DOI exists
- Manuscript reference for the code and tool: update the DOI, and make its author list match the creators chosen here.
- Code availability statement: "The browser tool is available at https://ckdcohortlab.netlify.app and the code at https://github.com/YOUR-USER/ckd-cohort-lab, archived at https://doi.org/10.5281/zenodo.XXXXXXX."
