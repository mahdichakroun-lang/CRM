"""Valide le notebook en exécutant la logique ML directement."""
import pandas as pd, numpy as np, warnings, random, os
warnings.filterwarnings('ignore')

os.makedirs('outputs/figures', exist_ok=True)
os.makedirs('outputs/models', exist_ok=True)

# ── 1. Génération données améliorées ──
random.seed(2026); np.random.seed(2026)
N = 1500
sources = ['website','phone','referral','trade_show','social_media','email','other']
src_w = [0.25,0.12,0.15,0.08,0.15,0.18,0.07]
sectors = ['IT / Digital','Finance / Banque','Santé','Industrie','Commerce','Éducation','Immobilier','Tourisme']
SRC_SCORE = {'referral':0.35,'trade_show':0.25,'phone':0.20,'website':0.05,'email':0.0,'social_media':-0.15,'other':-0.10}
SEC_SCORE = {'IT / Digital':0.15,'Finance / Banque':0.10,'Santé':0.05,'Industrie':-0.05,'Commerce':-0.10,'Éducation':-0.15,'Immobilier':0.0,'Tourisme':-0.10}

rows = []
for i in range(N):
    src = random.choices(sources, weights=src_w, k=1)[0]
    sec = random.choice(sectors)
    val = int(np.clip(np.random.lognormal(10.2, 0.7), 3000, 200000))
    days = random.randint(3, 120)
    has_email = int(random.random() < 0.85)
    has_phone = int(random.random() < 0.60)
    act = max(0, int(np.random.poisson(3)))
    calls = min(act, random.randint(0, 3))
    emails_s = min(act - calls, random.randint(0, 4))
    meetings = max(0, act - calls - emails_s)
    
    s = SRC_SCORE[src] + SEC_SCORE[sec]
    s += 0.20 * (val > 40000)
    s += 0.15 * (has_email and has_phone)
    s += 0.05 * has_email
    s += min(act * 0.06, 0.30)
    s += 0.10 * (meetings >= 2)
    s -= 0.15 * (days > 90)
    s += 0.10 * (days <= 20)
    s += np.random.normal(0, 0.06)
    rows.append({'source':src,'sector':sec,'estimated_value':val,'days_in_pipeline':days,
                 'has_email':has_email,'has_phone':has_phone,'activities_count':act,
                 'calls':calls,'emails_sent':emails_s,'meetings':meetings,'converted':int(s>0.35)})

df = pd.DataFrame(rows)
print(f"Dataset: {df.shape}, Conversion: {df['converted'].mean()*100:.1f}%")

# ── 2. Feature Engineering ──
df['contact_score'] = df['has_email'] + df['has_phone']
df['activity_intensity'] = (df['activities_count'] / df['days_in_pipeline'].clip(lower=1)).round(4)
df['meeting_ratio'] = (df['meetings'] / df['activities_count'].clip(lower=1)).round(4)
df['is_high_value'] = (df['estimated_value'] > df['estimated_value'].median()).astype(int)
df['is_fresh'] = (df['days_in_pipeline'] <= 30).astype(int)
df['log_value'] = np.log1p(df['estimated_value'])
df['has_activities'] = (df['activities_count'] > 0).astype(int)

df_enc = pd.get_dummies(df, columns=['source','sector'], drop_first=False, dtype=int)
X = df_enc.drop('converted', axis=1); y = df_enc['converted']

# ── 3. Split + SMOTE + Scale ──
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train_sm, y_train_sm = SMOTE(random_state=42).fit_resample(X_train, y_train)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train_sm)
X_test_s = scaler.transform(X_test)

# ── 4. Modèles ──
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, f1_score, accuracy_score, roc_auc_score

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
configs = {
    'LR (L1)': (LogisticRegression(max_iter=2000, random_state=42, penalty='l1', solver='saga', class_weight='balanced'), {'C':[0.01,0.1,1,10]}),
    'LR (L2)': (LogisticRegression(max_iter=2000, random_state=42, penalty='l2', solver='lbfgs', class_weight='balanced'), {'C':[0.01,0.1,1,10]}),
    'RF':      (RandomForestClassifier(random_state=42, class_weight='balanced', n_jobs=-1), {'n_estimators':[100,200,300],'max_depth':[5,8,12],'min_samples_leaf':[3,5]}),
    'XGB':     (XGBClassifier(random_state=42, eval_metric='logloss', n_jobs=-1), {'n_estimators':[100,200,300],'max_depth':[3,5,7],'learning_rate':[0.01,0.05,0.1],'subsample':[0.8]}),
}

best = {}
for name, (model, params) in configs.items():
    g = GridSearchCV(model, params, cv=cv, scoring='f1', n_jobs=-1, refit=True)
    g.fit(X_train_s, y_train_sm)
    best[name] = g.best_estimator_
    print(f"{name:8s} | CV F1={g.best_score_:.4f} | {g.best_params_}")

# ── 5. Évaluation test set ──
print("\n" + "="*70)
for name, model in best.items():
    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:,1]
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc_val = roc_auc_score(y_test, y_prob)
    print(f"{name:8s} | Acc={acc:.4f} | F1={f1:.4f} | AUC={auc_val:.4f}")
    print(classification_report(y_test, y_pred, target_names=['Non conv.','Converti'], digits=4))
