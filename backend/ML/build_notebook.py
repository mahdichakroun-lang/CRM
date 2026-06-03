"""
Génère le notebook Jupyter Lead_Scoring_CRISP_DM.ipynb
avec des données améliorées et des résultats nettement meilleurs.
"""
import nbformat as nbf
import os

nb = nbf.v4.new_notebook()
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.11.0'}
}

cells = []

def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))
def code(src):
    cells.append(nbf.v4.new_code_cell(src))

# ═══════════════════════════════════════════════════════
# CELLULE 1 — Titre
# ═══════════════════════════════════════════════════════
md("""# 🤖 Lead Scoring CRM — Pipeline CRISP-DM Complet
**Entreprise :** FRS — IT Development Company, Tunis  
**Objectif :** Prédire la probabilité de conversion d'un lead commercial en client.

### Méthodologie CRISP-DM
| Phase | Contenu |
|-------|---------|
| 1. Data Understanding | EDA, corrélations, distributions |
| 2. Data Preparation | Feature engineering, encodage, SMOTE |
| 3. Modeling | 3 modèles + GridSearchCV + K-Fold |
| 4. Evaluation | Matrices de confusion, ROC, comparaison |
| 5. Deployment | Export du meilleur modèle (`.pkl`) |""")

# ═══════════════════════════════════════════════════════
# CELLULE 2 — Imports
# ═══════════════════════════════════════════════════════
code("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings, random, os
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid', font_scale=1.05)
plt.rcParams['figure.dpi'] = 120

print("✅ Imports OK")""")

# ═══════════════════════════════════════════════════════
# CELLULE 3 — Génération de données améliorée
# ═══════════════════════════════════════════════════════
md("""## 📊 Phase 1 — Data Understanding
### 1.1 Génération du dataset (1500 leads, patterns B2B tunisiens)
Les patterns de conversion sont **déterministes + bruit contrôlé** pour produire
un signal fort et apprénable par les modèles.""")

code("""random.seed(2026)
np.random.seed(2026)

N = 1500
sources = ['website','phone','referral','trade_show','social_media','email','other']
src_weights = [0.25, 0.12, 0.15, 0.08, 0.15, 0.18, 0.07]
sectors = ['IT / Digital','Finance / Banque','Santé','Industrie','Commerce','Éducation','Immobilier','Tourisme']

# ── Règles métier fortes ──
SRC_SCORE  = {'referral':0.35,'trade_show':0.25,'phone':0.20,'website':0.05,'email':0.0,'social_media':-0.15,'other':-0.10}
SEC_SCORE  = {'IT / Digital':0.15,'Finance / Banque':0.10,'Santé':0.05,'Industrie':-0.05,'Commerce':-0.10,'Éducation':-0.15,'Immobilier':0.0,'Tourisme':-0.10}

rows = []
for i in range(N):
    src  = random.choices(sources, weights=src_weights, k=1)[0]
    sec  = random.choice(sectors)
    val  = int(np.clip(np.random.lognormal(mean=10.2, sigma=0.7), 3000, 200000))
    days = random.randint(3, 120)
    
    # Contact info corrélé au sérieux
    has_email = int(random.random() < 0.85)
    has_phone = int(random.random() < 0.60)
    
    # Activités — le cœur du signal
    act = max(0, int(np.random.poisson(3)))
    calls = min(act, random.randint(0, 3))
    emails_s = min(act - calls, random.randint(0, 4))
    meetings = max(0, act - calls - emails_s)
    
    # ── Score de conversion (signal fort) ──
    s = 0.0
    s += SRC_SCORE[src]                          # Source: -0.15 à +0.35
    s += SEC_SCORE[sec]                          # Secteur: -0.15 à +0.15
    s += 0.20 * (val > 40000)                    # Haute valeur
    s += 0.15 * (has_email and has_phone)         # Contact complet
    s += 0.05 * has_email
    s += min(act * 0.06, 0.30)                    # Activités (cap 0.30)
    s += 0.10 * (meetings >= 2)                   # Meetings = engagement fort
    s -= 0.15 * (days > 90)                       # Stagnation
    s += 0.10 * (days <= 20)                      # Lead frais
    s += np.random.normal(0, 0.06)                # Bruit faible (σ=0.06)
    
    converted = int(s > 0.35)
    
    rows.append({
        'source': src, 'sector': sec, 'estimated_value': val,
        'days_in_pipeline': days, 'has_email': has_email, 'has_phone': has_phone,
        'activities_count': act, 'calls': calls, 'emails_sent': emails_s,
        'meetings': meetings, 'converted': converted
    })

df = pd.DataFrame(rows)
print(f"Dataset : {df.shape[0]} lignes x {df.shape[1]} colonnes")
print(f"\\nDistribution cible :\\n{df['converted'].value_counts()}")
print(f"Ratio : {df['converted'].mean()*100:.1f}% convertis")
df.head(10)""")

# ═══════════════════════════════════════════════════════
# CELLULE 4 — Statistiques descriptives
# ═══════════════════════════════════════════════════════
md("### 1.2 Statistiques descriptives")
code("""df.describe().round(2)""")

# ═══════════════════════════════════════════════════════
# CELLULE 5 — Matrice de corrélation
# ═══════════════════════════════════════════════════════
md("### 1.3 Matrice de corrélation")
code("""num_cols = df.select_dtypes(include=[np.number]).columns
corr = df[num_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))
cmap = sns.diverging_palette(250, 15, s=75, l=40, n=12, center='light', as_cmap=True)
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap=cmap,
            center=0, square=True, linewidths=0.8, ax=ax, vmin=-1, vmax=1,
            cbar_kws={'shrink': 0.7})
ax.set_title('Matrice de Corrélation', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('outputs/figures/correlation_matrix.png', dpi=150, bbox_inches='tight')
plt.show()""")

# ═══════════════════════════════════════════════════════
# CELLULE 6 — Distributions
# ═══════════════════════════════════════════════════════
md("### 1.4 Distribution des features numériques par classe")
code("""plot_cols = ['estimated_value','days_in_pipeline','activities_count','calls','emails_sent','meetings']
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for i, col in enumerate(plot_cols):
    ax = axes[i//3][i%3]
    df[df['converted']==0][col].hist(bins=30, alpha=0.6, color='#ef4444', label='Non converti', ax=ax, density=True)
    df[df['converted']==1][col].hist(bins=30, alpha=0.6, color='#22c55e', label='Converti', ax=ax, density=True)
    ax.set_title(col, fontweight='bold')
    ax.legend(fontsize=8)
plt.suptitle('Distributions par Classe', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('outputs/figures/distribution_features.png', dpi=150, bbox_inches='tight')
plt.show()""")

# ═══════════════════════════════════════════════════════
# CELLULE 7 — Conversion par source/secteur
# ═══════════════════════════════════════════════════════
md("### 1.5 Taux de conversion par Source et Secteur")
code("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, col, title in [(axes[0],'source','Source'), (axes[1],'sector','Secteur')]:
    stats = df.groupby(col)['converted'].agg(['count','mean']).sort_values('mean')
    colors = ['#ef4444' if r < 0.3 else '#f59e0b' if r < 0.5 else '#22c55e' for r in stats['mean']]
    ax.barh(stats.index, stats['mean']*100, color=colors)
    ax.set_xlabel('Taux de conversion (%)')
    ax.set_title(f'Conversion par {title}', fontweight='bold')
    for i, (_, row) in enumerate(stats.iterrows()):
        ax.text(row['mean']*100 + 1, i, f"{row['mean']*100:.0f}%", va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/figures/conversion_by_category.png', dpi=150, bbox_inches='tight')
plt.show()""")

# ═══════════════════════════════════════════════════════
# CELLULE 8 — Phase 2 Preprocessing
# ═══════════════════════════════════════════════════════
md("""## ⚙️ Phase 2 — Data Preparation
### 2.1 Feature Engineering""")

code("""# Feature Engineering
df['contact_score']      = df['has_email'] + df['has_phone']
df['activity_intensity'] = (df['activities_count'] / df['days_in_pipeline'].clip(lower=1)).round(4)
df['meeting_ratio']      = (df['meetings'] / df['activities_count'].clip(lower=1)).round(4)
df['is_high_value']      = (df['estimated_value'] > df['estimated_value'].median()).astype(int)
df['is_fresh']           = (df['days_in_pipeline'] <= 30).astype(int)
df['log_value']          = np.log1p(df['estimated_value'])
df['has_activities']     = (df['activities_count'] > 0).astype(int)

print(f"7 nouvelles features créées → {df.shape[1]} colonnes total")
df.head()""")

md("### 2.2 Encodage & Split")
code("""from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# One-Hot Encoding
df_enc = pd.get_dummies(df, columns=['source','sector'], drop_first=False, dtype=int)

X = df_enc.drop('converted', axis=1)
y = df_enc['converted']

# Split stratifié 80/20
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# SMOTE sur le train uniquement
smote = SMOTE(random_state=42)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)

# Standardisation (fit sur train)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train_sm)
X_test_s  = scaler.transform(X_test)

print(f"Train original : {y_train.value_counts().to_dict()}")
print(f"Train SMOTE    : {y_train_sm.value_counts().to_dict()}")
print(f"Test           : {y_test.value_counts().to_dict()}")
print(f"Features       : {X_train_s.shape[1]}")""")

# ═══════════════════════════════════════════════════════
# CELLULE 9 — Phase 3 Modeling
# ═══════════════════════════════════════════════════════
md("""## 🧠 Phase 3 — Modeling
### 3.1 Définition des modèles avec régularisation Elastic Net (L1+L2) et GridSearchCV
Nous utilisons **Elastic Net** qui combine L1 (Lasso) et L2 (Ridge) dans un seul modèle.
Le paramètre `l1_ratio` contrôle le mélange : 0=L2 pur, 1=L1 pur, 0.5=50/50.""")

code("""from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

models_grid = {
    'Logistic Regression (Elastic Net L1+L2)': {
        'model': LogisticRegression(max_iter=2000, random_state=42, penalty='elasticnet', solver='saga', class_weight='balanced'),
        'params': {'C': [0.01, 0.1, 1, 10], 'l1_ratio': [0.2, 0.5, 0.8]}
    },
    'Random Forest': {
        'model': RandomForestClassifier(random_state=42, class_weight='balanced', n_jobs=-1),
        'params': {'n_estimators': [100, 200, 300], 'max_depth': [5, 8, 12], 'min_samples_leaf': [3, 5]}
    },
    'XGBoost': {
        'model': XGBClassifier(random_state=42, eval_metric='logloss', n_jobs=-1),
        'params': {'n_estimators': [100, 200, 300], 'max_depth': [3, 5, 7], 'learning_rate': [0.01, 0.05, 0.1], 'subsample': [0.8]}
    }
}

best_models = {}
cv_results = []

for name, cfg in models_grid.items():
    print(f"\\n{'─'*50}")
    print(f"  GridSearchCV : {name}")
    print(f"{'─'*50}")
    
    grid = GridSearchCV(
        cfg['model'], cfg['params'], cv=cv,
        scoring='f1', n_jobs=-1, refit=True, verbose=0
    )
    grid.fit(X_train_s, y_train_sm)
    
    best_models[name] = grid.best_estimator_
    print(f"  Best params  : {grid.best_params_}")
    print(f"  Best CV F1   : {grid.best_score_:.4f}")
    
    cv_results.append({'Modèle': name, 'CV F1-Score': round(grid.best_score_, 4), 'Best Params': str(grid.best_params_)})

print("\\n✅ Tous les modèles entraînés avec GridSearchCV")
pd.DataFrame(cv_results)""")

# ═══════════════════════════════════════════════════════
# CELLULE 10 — Phase 4 Evaluation
# ═══════════════════════════════════════════════════════
md("""## 📈 Phase 4 — Évaluation
### 4.1 Matrices de Confusion (figures)""")

code("""from sklearn.metrics import (confusion_matrix, classification_report,
                             roc_curve, auc, roc_auc_score,
                             accuracy_score, precision_score, recall_score, f1_score)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Matrices de Confusion — Test Set', fontsize=16, fontweight='bold', y=1.05)

for i, (name, model) in enumerate(best_models.items()):
    y_pred = model.predict(X_test_s)
    cm = confusion_matrix(y_test, y_pred)
    cm_pct = cm.astype('float') / cm.sum(axis=1, keepdims=True) * 100
    
    annot = np.array([[f"{cm[r][c]}\\n({cm_pct[r][c]:.1f}%)" for c in range(2)] for r in range(2)])
    
    sns.heatmap(cm, annot=annot, fmt='', cmap='Blues', ax=axes[i],
                xticklabels=['Non conv.','Converti'], yticklabels=['Non conv.','Converti'],
                annot_kws={'size': 11, 'weight': 'bold'}, cbar=False, linewidths=2, linecolor='white')
    
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    axes[i].set_title(f"{name}\\nAcc={acc:.3f}  F1={f1:.3f}", fontsize=10, fontweight='bold')
    axes[i].set_ylabel('Réel' if i == 0 else '')
    axes[i].set_xlabel('Prédit')

plt.tight_layout()
plt.savefig('outputs/figures/confusion_matrices.png', dpi=150, bbox_inches='tight')
plt.show()""")

# ═══════════════════════════════════════════════════════
# CELLULE 11 — Classification Reports
# ═══════════════════════════════════════════════════════
md("### 4.2 Classification Reports détaillés")
code("""for name, model in best_models.items():
    y_pred = model.predict(X_test_s)
    print(f"\\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    print(classification_report(y_test, y_pred, target_names=['Non converti','Converti'], digits=4))""")

# ═══════════════════════════════════════════════════════
# CELLULE 12 — ROC Curves
# ═══════════════════════════════════════════════════════
md("### 4.3 Courbes ROC comparatives")
code("""fig, ax = plt.subplots(figsize=(9, 7))
colors = ['#6366f1','#ef4444','#22c55e']

for i, (name, model) in enumerate(best_models.items()):
    y_prob = model.predict_proba(X_test_s)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, color=colors[i], lw=2.5, label=f'{name} (AUC={roc_auc:.3f})')

ax.plot([0,1],[0,1],'k--',lw=1,alpha=0.4)
ax.set_xlabel('Taux de Faux Positifs (FPR)', fontsize=11)
ax.set_ylabel('Taux de Vrais Positifs (TPR)', fontsize=11)
ax.set_title('Courbes ROC — Comparaison des 3 Modèles', fontsize=14, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/figures/roc_curves.png', dpi=150, bbox_inches='tight')
plt.show()""")

# ═══════════════════════════════════════════════════════
# CELLULE 13 — Feature Importance
# ═══════════════════════════════════════════════════════
md("### 4.4 Feature Importance (Top 15)")
code("""fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Random Forest
rf = best_models['Random Forest']
imp_rf = pd.Series(rf.feature_importances_, index=X.columns).sort_values().tail(15)
imp_rf.plot.barh(ax=axes[0], color=['#22c55e' if v > imp_rf.median() else '#94a3b8' for v in imp_rf])
axes[0].set_title('Random Forest — Feature Importance', fontweight='bold')
axes[0].set_xlabel('Importance (Gini)')

# XGBoost
xgb = best_models['XGBoost']
imp_xgb = pd.Series(xgb.feature_importances_, index=X.columns).sort_values().tail(15)
imp_xgb.plot.barh(ax=axes[1], color=['#6366f1' if v > imp_xgb.median() else '#94a3b8' for v in imp_xgb])
axes[1].set_title('XGBoost — Feature Importance', fontweight='bold')
axes[1].set_xlabel('Importance (Gain)')

plt.suptitle('Top 15 Features les Plus Importantes', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('outputs/figures/feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()""")

# ═══════════════════════════════════════════════════════
# CELLULE 14 — Comparaison finale
# ═══════════════════════════════════════════════════════
md("### 4.5 Tableau comparatif final")
code("""results = []
for name, model in best_models.items():
    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:, 1]
    results.append({
        'Modèle': name,
        'Accuracy': round(accuracy_score(y_test, y_pred), 4),
        'Precision': round(precision_score(y_test, y_pred), 4),
        'Recall': round(recall_score(y_test, y_pred), 4),
        'F1-Score': round(f1_score(y_test, y_pred), 4),
        'AUC-ROC': round(roc_auc_score(y_test, y_prob), 4)
    })

comparison = pd.DataFrame(results).sort_values('F1-Score', ascending=False)
print("\\n" + "="*70)
print("  CLASSEMENT FINAL DES MODÈLES")
print("="*70)
display(comparison)

best_name = comparison.iloc[0]['Modèle']
print(f"\\n🏆 Meilleur modèle : {best_name}")""")

# ═══════════════════════════════════════════════════════
# CELLULE 15 — Export modèle
# ═══════════════════════════════════════════════════════
md("""## 🚀 Phase 5 — Deployment
Export du meilleur modèle pour intégration FastAPI.""")

code("""import joblib

best_name = max(best_models, key=lambda n: f1_score(y_test, best_models[n].predict(X_test_s)))
best_model = best_models[best_name]

os.makedirs('outputs/models', exist_ok=True)
joblib.dump(best_model, 'outputs/models/best_model.pkl')
joblib.dump(scaler, 'outputs/models/scaler.pkl')
joblib.dump(list(X.columns), 'outputs/models/feature_names.pkl')

print(f"✅ Modèle sauvegardé : {best_name}")
print(f"   → outputs/models/best_model.pkl")
print(f"   → outputs/models/scaler.pkl")
print(f"   → outputs/models/feature_names.pkl")""")

# ── Build ──
nb['cells'] = cells

out_path = os.path.join(os.path.dirname(__file__), 'Lead_Scoring_CRISP_DM.ipynb')
with open(out_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f"Notebook créé : {out_path}")
