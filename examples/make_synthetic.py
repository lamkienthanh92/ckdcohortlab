"""Generate the synthetic example dataset (not real patients)."""
import numpy as np, pandas as pd
rng = np.random.default_rng(7); n = 140
age = np.clip(rng.normal(67, 11, n), 30, 92).round()
female = rng.random(n) < 0.55; dm = rng.random(n) < 0.5; htn = rng.random(n) < 0.85
egfr = rng.uniform(8, 59, n).round(1)
analyser = np.where(rng.random(n) < 0.6, "Analyser A", "Analyser B")
log_acr = 4.3 + 0.6 * dm - 0.035 * (egfr - 35) + rng.normal(0, 1.6, n)
acr = np.exp(log_acr).clip(1, 6000).round(1)
sg = np.where(analyser == "Analyser A", rng.uniform(1.004, 1.026, n).round(3), (rng.uniform(1.005, 1.025, n) / 0.005).round() * 0.005)
ucr = (20 + (sg - 1.003) * 4500 * rng.uniform(0.8, 1.2, n)).round(1)
alb = (acr * ucr / 100).round(1)
latent = np.log(alb) + rng.normal(0, 0.6, n) + np.where(analyser == "Analyser B", 0.4, 0)
cuts = np.log([60, 150, 500, 1500]); labels = np.array(["Negative", "Trace", "1+", "2+", "3+"])
grade = labels[np.digitize(latent, cuts)]
pd.DataFrame(dict(id=[f"SYN{i:03d}" for i in range(1, n + 1)], age=age.astype(int), sex=np.where(female, "F", "M"),
                  diabetes=dm.astype(int), hypertension=htn.astype(int), egfr=egfr, urine_albumin_mg_L=alb,
                  urine_creatinine_mg_dL=ucr, acr_mg_g=acr, dipstick_protein=grade, specific_gravity=sg.round(3),
                  analyser=analyser)).to_csv("example_synthetic.csv", index=False)
print("written example_synthetic.csv")
