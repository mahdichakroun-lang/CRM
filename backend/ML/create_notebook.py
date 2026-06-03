import nbformat as nbf

nb = nbf.v4.new_notebook()

# ── Cells content ──

markdown_1 = """# 🤖 Lead Scoring CRM — CRISP-DM Pipeline (Version Améliorée)
Ce notebook contient le pipeline complet de bout en bout pour le système de **Lead Scoring**.
Nous avons amélioré les performances avec :
1. **1500 Leads** (Données synthétiques réalistes).
2. **SMOTE** (Oversampling) pour équilibrer la classe minoritaire.
3. **GridSearchCV** pour l'optimisation des hyperparamètres.
4. **Visualisation** avancée (Matrices de confusion et Courbes ROC en belles figures)."""

code_1 = """!pip install -q pandas scikit-learn matplotlib seaborn imbalanced-learn xgboost
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style="whitegrid", font_scale=1.1)
"""

markdown_2 = """## Phase 1 & 2 : Génération de Données et Preprocessing
Nous générons 1500 leads et appliquons le feature engineering."""

code_2 = """# Script de génération (simplifié pour le notebook)
import random
from datetime import datetime, timedelta

def generate_improved_data(n_leads=1500):
    data = []
    base_date = datetime(2025, 1, 15)
    sources = ['website', 'phone', 'referral', 'trade_show', 'social_media', 'email']
    sectors = ['IT / Digital', 'Finance / Banque', 'Santé', 'Industrie', 'Commerce', 'Immobilier']
    
    for i in range(1, n_leads + 1):
        source = random.choice(sources)
        sector = random.choice(sectors)
        
        # Valeur estimée plus haute pour IT et Referral
        base_val = random.randint(5000, 100000)
        if source == 'referral': base_val = int(base_val * 1.5)
        if sector == 'IT / Digital': base_val = int(base_val * 1.2)
        
        days_in_pipeline = random.randint(3, 120)
        has_email = 1 if random.random() > 0.1 else 0
        has_phone = 1 if random.random() > 0.3 else 0
        
        activities_count = random.randint(0, 15)
        meetings = min(activities_count, random.randint(0, 5))
        
        # Logique de conversion plus forte
        score = 0
        if source in ['referral', 'trade_show']: score += 0.3
        if sector in ['IT / Digital', 'Finance / Banque']: score += 0.2
        if has_email and has_phone: score += 0.2
        if activities_count > 5: score += 0.3
        if days_in_pipeline < 30: score += 0.1
        elif days_in_pipeline > 90: score -= 0.2
        
        score += random.gauss(0, 0.1) # Bruit
        converted = 1 if score > 0.6 else 0
        
        data.append({
            'source': source, 'sector': sector, 'estimated_value': base_val,
            'days_in_pipeline': days_in_pipeline, 'has_email': has_email, 
            'has_phone': has_phone, 'activities_count': activities_count,
            'meetings': meetings, 'converted': converted
        })
    return pd.DataFrame(data)

df = generate_improved_data(1500)
print(f"Dataset généré : {df.shape}")
display(df.head())
print("\\nDistribution de la cible :")
print(df['converted'].value_counts(normalize=True).round(2))
"""

code_3 = """# Feature Engineering & Encodage
df['contact_score'] = df['has_email'] + df['has_phone']
df['activity_intensity'] = df['activities_count'] / df['days_in_pipeline'].clip(lower=1)
df['log_value'] = np.log1p(df['estimated_value'])

# One Hot Encoding
df_encoded = pd.get_dummies(df, columns=['source', 'sector'], drop_first=True)

X = df_encoded.drop('converted', axis=1)
y = df_encoded['converted']

print(f"Features après preprocessing : {X.shape[1]}")
"""

markdown_3 = """## Phase 3 : Modélisation avec GridSearchCV & SMOTE"""

code_4 = """from sklearn.model_selection import train_test_split, GridSearchCV
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# SMOTE pour équilibrer les classes d'entraînement
smote = SMOTE(random_state=42)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
print(f"Train set après SMOTE : {y_train_sm.value_counts().to_dict()}")

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_sm)
X_test_scaled = scaler.transform(X_test)
"""

code_5 = """# Modèles et Tuning
models = {
    'Logistic Regression': (LogisticRegression(max_iter=1000, random_state=42), 
                           {'C': [0.1, 1, 10]}),
    'Random Forest': (RandomForestClassifier(random_state=42), 
                     {'n_estimators': [100, 200], 'max_depth': [5, 10]}),
    'XGBoost': (XGBClassifier(random_state=42, eval_metric='logloss'), 
               {'n_estimators': [100, 200], 'max_depth': [3, 6], 'learning_rate': [0.01, 0.1]})
}

best_models = {}

for name, (model, params) in models.items():
    print(f"Tuning {name}...")
    grid = GridSearchCV(model, params, cv=5, scoring='f1', n_jobs=-1)
    grid.fit(X_train_scaled, y_train_sm)
    best_models[name] = grid.best_estimator_
    print(f"Best params: {grid.best_params_} | CV F1-Score: {grid.best_score_:.4f}\\n")
"""

markdown_4 = """## Phase 4 : Évaluation et Matrices de Confusion en Figures"""

code_6 = """from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve

# Matrices de confusion
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Matrices de Confusion par Modèle', fontsize=16, fontweight='bold', y=1.05)

for i, (name, model) in enumerate(best_models.items()):
    y_pred = model.predict(X_test_scaled)
    cm = confusion_matrix(y_test, y_pred)
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[i], 
                xticklabels=['Non Converti', 'Converti'], 
                yticklabels=['Non Converti', 'Converti'],
                annot_kws={'size': 14, 'weight': 'bold'})
    axes[i].set_title(name, fontsize=14, pad=10)
    axes[i].set_ylabel('Valeur Réelle')
    axes[i].set_xlabel('Prédiction')
    
    print(f"\\n{'='*40}\\n{name}\\n{'='*40}")
    print(classification_report(y_test, y_pred))

plt.tight_layout()
plt.show()
"""

code_7 = """# Courbes ROC
plt.figure(figsize=(10, 8))

for name, model in best_models.items():
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test_scaled)[:, 1]
    else:
        y_prob = model.decision_function(X_test_scaled)
        
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc_val = roc_auc_score(y_test, y_prob)
    
    plt.plot(fpr, tpr, lw=2, label=f'{name} (AUC = {auc_val:.3f})')

plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Taux de Faux Positifs')
plt.ylabel('Taux de Vrais Positifs')
plt.title('Courbes ROC Comparatives', fontsize=16, fontweight='bold')
plt.legend(loc="lower right", fontsize=12)
plt.grid(alpha=0.3)
plt.show()
"""

code_8 = """# Feature Importance (Random Forest)
rf_model = best_models['Random Forest']
importances = rf_model.feature_importances_
indices = np.argsort(importances)[-10:] # Top 10

plt.figure(figsize=(10, 6))
plt.title('Top 10 Features Importantes (Random Forest)', fontsize=14, fontweight='bold')
plt.barh(range(len(indices)), importances[indices], color='#22c55e', align='center')
plt.yticks(range(len(indices)), [X.columns[i] for i in indices])
plt.xlabel('Importance Relative')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.show()
"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(markdown_1),
    nbf.v4.new_code_cell(code_1),
    nbf.v4.new_markdown_cell(markdown_2),
    nbf.v4.new_code_cell(code_2),
    nbf.v4.new_code_cell(code_3),
    nbf.v4.new_markdown_cell(markdown_3),
    nbf.v4.new_code_cell(code_4),
    nbf.v4.new_code_cell(code_5),
    nbf.v4.new_markdown_cell(markdown_4),
    nbf.v4.new_code_cell(code_6),
    nbf.v4.new_code_cell(code_7),
    nbf.v4.new_code_cell(code_8)
]

with open('c:/Users/Lenovo/Desktop/crm/backend/ml/Lead_Scoring_CRISP_DM.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Notebook créé avec succès.")
