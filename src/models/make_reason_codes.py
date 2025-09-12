# src/models/make_reason_codes.py
import json, pickle, sys
from pathlib import Path
import pandas as pd
import numpy as np
import lightgbm as lgb
import shap

ROOT = Path(__file__).resolve().parents[2]
feat_p = ROOT/"data"/"features.parquet"
out_p  = ROOT/"data"/"reason_codes.jsonl"
model_pkl = ROOT/"models"/"lgbm.pkl"
model_txt = ROOT/"models"/"lgbm_loss_cost.txt"  # fallback

np.random.seed(42)

df = pd.read_parquet(feat_p).copy()
# Expect these identifier columns; adjust if named slightly different in your features:
id_cols = [c for c in ["user_id","month"] if c in df.columns]
assert "user_id" in id_cols, "user_id column missing in features.parquet"
if "month" not in id_cols:
    # create a stable month if only one month present
    df["month"] = pd.Timestamp("2024-01-01")
    id_cols = ["user_id","month"]

# Normalize month to 'YYYY-MM' string for joining with pricing later
df["month_key"] = pd.to_datetime(df["month"]).dt.to_period("M").astype(str)

# Select model features: all numeric, drop ids/targets if present
drop_cols = set(id_cols + ["month_key","freq","sev_mean","loss_cost","frequency","severity_mean"])
X = df.select_dtypes(include=[np.number]).drop(columns=list(drop_cols & set(df.columns)), errors="ignore")
feature_names = X.columns.tolist()

# Load LightGBM model (try sklearn API, then Booster text)
model = None
try:
    with open(model_pkl, "rb") as f:
        m = pickle.load(f)
    model = getattr(m, "booster_", m)  # works for LGBMRegressor or Booster
except Exception:
    if model_pkl.exists():
        raise
if model is None and model_txt.exists():
    model = lgb.Booster(model_file=str(model_txt))
assert model is not None, "LightGBM model not found."

# SHAP
explainer = shap.TreeExplainer(model)
shap_vals = explainer.shap_values(X, check_additivity=False)
# For regression, shap_values is (n_samples, n_features)
if isinstance(shap_vals, list):  # multiclass safeguard
    shap_vals = shap_vals[0]
abs_shap = np.abs(shap_vals)

topk = 5
with open(out_p, "w", encoding="utf-8") as f:
    for i in range(X.shape[0]):
        order = np.argsort(-abs_shap[i])[:topk]
        reasons = [
            {
                "feature": feature_names[j],
                "shap_value": float(shap_vals[i, j]),
                "rank": int(k+1),
            }
            for k, j in enumerate(order)
            if abs_shap[i, j] > 0
        ]
        rec = {
            "user_id": str(df.loc[df.index[i], "user_id"]),
            "month": str(df.loc[df.index[i], "month_key"]),
            "top_reasons": reasons,
        }
        f.write(json.dumps(rec) + "\n")

print(f"Wrote reason codes: {out_p} (rows={X.shape[0]})")