"""Regenere TOUTES les figures avec le nouveau setup 3 modeles."""
import pandas as pd, numpy as np, warnings, random, os, joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid', font_scale=1.05)
plt.rcParams['figure.dpi'] = 150

FIG = 'outputs/figures'
MDL = 'outputs/models'
os.makedirs(FIG, exist_ok=True)
os.makedirs(MDL, exist_ok=True)

# ═══════════════════════════════════════
# 1. GENERATION DONNÉES
# ═══════════════════════════════════════
random.seed(2026); np.random.seed(2026)
N=1500
sources=['website','phone','referral','trade_show','social_media','email','other']
src_w=[0.25,0.12,0.15,0.08,0.15,0.18,0.07]
sectors=['IT / Digital','Finance / Banque','Santé','Industrie','Commerce','Éducation','Immobilier','Tourisme']
SRC_SCORE={'referral':0.35,'trade_show':0.25,'phone':0.20,'website':0.05,'email':0.0,'social_media':-0.15,'other':-0.10}
SEC_SCORE={'IT / Digital':0.15,'Finance / Banque':0.10,'Santé':0.05,'Industrie':-0.05,'Commerce':-0.10,'Éducation':-0.15,'Immobilier':0.0,'Tourisme':-0.10}
rows=[]
for i in range(N):
    src=random.choices(sources,weights=src_w,k=1)[0];sec=random.choice(sectors)
    val=int(np.clip(np.random.lognormal(10.2,0.7),3000,200000));days=random.randint(3,120)
    he=int(random.random()<0.85);hp=int(random.random()<0.60)
    act=max(0,int(np.random.poisson(3)));ca=min(act,random.randint(0,3));em=min(act-ca,random.randint(0,4));mt=max(0,act-ca-em)
    s=SRC_SCORE[src]+SEC_SCORE[sec]+0.20*(val>40000)+0.15*(he and hp)+0.05*he+min(act*0.06,0.30)+0.10*(mt>=2)-0.15*(days>90)+0.10*(days<=20)+np.random.normal(0,0.06)
    rows.append({'source':src,'sector':sec,'estimated_value':val,'days_in_pipeline':days,'has_email':he,'has_phone':hp,'activities_count':act,'calls':ca,'emails_sent':em,'meetings':mt,'converted':int(s>0.35)})
df=pd.DataFrame(rows)
print(f"[1/8] Dataset: {df.shape}, {df['converted'].mean()*100:.1f}% convertis")

# ═══════════════════════════════════════
# 2. FIGURE — Matrice de corrélation
# ═══════════════════════════════════════
num_cols = df.select_dtypes(include=[np.number]).columns
corr = df[num_cols].corr()
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))
cmap = sns.diverging_palette(250, 15, s=75, l=40, n=12, center='light', as_cmap=True)
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap=cmap, center=0, square=True,
            linewidths=0.8, ax=ax, vmin=-1, vmax=1, cbar_kws={'shrink':0.7, 'label':'Coefficient'})
ax.set_title('Matrice de Corrélation — Features du Lead Scoring', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{FIG}/correlation_matrix.png', bbox_inches='tight')
plt.close()
print("[2/8] correlation_matrix.png")

# ═══════════════════════════════════════
# 3. FIGURE — Distributions par classe
# ═══════════════════════════════════════
plot_cols = ['estimated_value','days_in_pipeline','activities_count','calls','emails_sent','meetings']
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for i, col in enumerate(plot_cols):
    ax = axes[i//3][i%3]
    df[df['converted']==0][col].hist(bins=30, alpha=0.6, color='#ef4444', label='Non converti', ax=ax, density=True)
    df[df['converted']==1][col].hist(bins=30, alpha=0.6, color='#22c55e', label='Converti', ax=ax, density=True)
    ax.set_title(col, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
plt.suptitle('Distribution des Features par Classe de Conversion', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{FIG}/distribution_features.png', bbox_inches='tight')
plt.close()
print("[3/8] distribution_features.png")

# ═══════════════════════════════════════
# 4. FIGURE — Conversion par catégorie
# ═══════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, col, title in [(axes[0],'source','Source'), (axes[1],'sector','Secteur')]:
    stats = df.groupby(col)['converted'].agg(['count','mean']).sort_values('mean')
    colors = ['#ef4444' if r < 0.3 else '#f59e0b' if r < 0.5 else '#22c55e' for r in stats['mean']]
    ax.barh(stats.index, stats['mean']*100, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_xlabel('Taux de conversion (%)')
    ax.set_title(f'Taux de Conversion par {title}', fontsize=12, fontweight='bold')
    for i, (_, row) in enumerate(stats.iterrows()):
        ax.text(row['mean']*100 + 1, i, f"{row['mean']*100:.0f}%", va='center', fontsize=9, fontweight='bold')
    ax.set_xlim(0, max(stats['mean'])*100 + 15)
    ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{FIG}/conversion_by_category.png', bbox_inches='tight')
plt.close()
print("[4/8] conversion_by_category.png")

# ═══════════════════════════════════════
# 5. FIGURE — Boxplots outliers
# ═══════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle('Boxplots par Classe de Conversion', fontsize=13, fontweight='bold', y=1.02)
for i, col in enumerate(['estimated_value','days_in_pipeline','activities_count']):
    sns.boxplot(data=df, x='converted', y=col, ax=axes[i], hue='converted',
                palette=['#ef4444','#22c55e'], width=0.5, legend=False,
                flierprops={'markersize':3,'alpha':0.5})
    axes[i].set_title(col, fontweight='semibold')
    axes[i].set_xticks([0,1]); axes[i].set_xticklabels(['Non converti','Converti'])
    axes[i].grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{FIG}/boxplots_outliers.png', bbox_inches='tight')
plt.close()
print("[5/8] boxplots_outliers.png")

# ═══════════════════════════════════════
# 6. PREPROCESSING + MODELING
# ═══════════════════════════════════════
df['contact_score']=df['has_email']+df['has_phone']
df['activity_intensity']=(df['activities_count']/df['days_in_pipeline'].clip(lower=1)).round(4)
df['meeting_ratio']=(df['meetings']/df['activities_count'].clip(lower=1)).round(4)
df['is_high_value']=(df['estimated_value']>df['estimated_value'].median()).astype(int)
df['is_fresh']=(df['days_in_pipeline']<=30).astype(int)
df['log_value']=np.log1p(df['estimated_value'])
df['has_activities']=(df['activities_count']>0).astype(int)
df_enc=pd.get_dummies(df,columns=['source','sector'],drop_first=False,dtype=int)
X=df_enc.drop('converted',axis=1);y=df_enc['converted']

from sklearn.model_selection import train_test_split,GridSearchCV,StratifiedKFold
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (confusion_matrix,classification_report,roc_curve,auc,
                             roc_auc_score,accuracy_score,precision_score,recall_score,f1_score)

X_tr,X_te,y_tr,y_te=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
X_tr_sm,y_tr_sm=SMOTE(random_state=42).fit_resample(X_tr,y_tr)
sc=StandardScaler();X_tr_s=sc.fit_transform(X_tr_sm);X_te_s=sc.transform(X_te)
cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=42)

configs={
    'Elastic Net (L1+L2)':(LogisticRegression(max_iter=2000,random_state=42,penalty='elasticnet',solver='saga',class_weight='balanced'),{'C':[0.01,0.1,1,10],'l1_ratio':[0.2,0.5,0.8]}),
    'Random Forest':(RandomForestClassifier(random_state=42,class_weight='balanced',n_jobs=-1),{'n_estimators':[100,200,300],'max_depth':[5,8,12],'min_samples_leaf':[3,5]}),
    'XGBoost':(XGBClassifier(random_state=42,eval_metric='logloss',n_jobs=-1),{'n_estimators':[100,200,300],'max_depth':[3,5,7],'learning_rate':[0.01,0.05,0.1],'subsample':[0.8]}),
}
best={}
for name,(model,params) in configs.items():
    g=GridSearchCV(model,params,cv=cv,scoring='f1',n_jobs=-1,refit=True)
    g.fit(X_tr_s,y_tr_sm)
    best[name]=g.best_estimator_
    print(f"  {name:25s} CV F1={g.best_score_:.4f} | {g.best_params_}")

# ═══════════════════════════════════════
# 6. FIGURE — Matrices de confusion (3 modèles)
# ═══════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
fig.suptitle('Matrices de Confusion — Évaluation sur le Test Set', fontsize=15, fontweight='bold', y=1.05)
for i, (name, model) in enumerate(best.items()):
    yp = model.predict(X_te_s)
    cm = confusion_matrix(y_te, yp)
    cm_pct = cm.astype('float') / cm.sum(axis=1, keepdims=True) * 100
    annot = np.array([[f"{cm[r][c]}\n({cm_pct[r][c]:.1f}%)" for c in range(2)] for r in range(2)])
    sns.heatmap(cm, annot=annot, fmt='', cmap='Blues', ax=axes[i],
                xticklabels=['Non converti','Converti'], yticklabels=['Non converti','Converti'],
                annot_kws={'size':12,'weight':'bold'}, cbar=False, linewidths=2, linecolor='white')
    f1v = f1_score(y_te, yp); accv = accuracy_score(y_te, yp)
    axes[i].set_title(f"{name}\nAcc={accv:.3f}  F1={f1v:.3f}", fontsize=11, fontweight='bold', pad=10)
    axes[i].set_ylabel('Réel' if i == 0 else '')
    axes[i].set_xlabel('Prédit')
plt.tight_layout()
plt.savefig(f'{FIG}/confusion_matrices.png', bbox_inches='tight')
plt.close()
print("[6/8] confusion_matrices.png")

# ═══════════════════════════════════════
# 7. FIGURE — Courbes ROC (3 modèles)
# ═══════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 7))
colors = ['#6366f1','#ef4444','#22c55e']
for i, (name, model) in enumerate(best.items()):
    ypr = model.predict_proba(X_te_s)[:,1]
    fpr,tpr,thr = roc_curve(y_te, ypr)
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, color=colors[i], lw=2.5, label=f'{name} (AUC={roc_auc:.3f})')
    j_idx = np.argmax(tpr - fpr)
    ax.scatter(fpr[j_idx], tpr[j_idx], s=80, color=colors[i], edgecolors='white', linewidth=2, zorder=5)
ax.plot([0,1],[0,1],'k--',lw=1,alpha=0.4,label='Random (AUC=0.500)')
ax.set_xlabel('Taux de Faux Positifs (FPR)', fontsize=11)
ax.set_ylabel('Taux de Vrais Positifs (TPR)', fontsize=11)
ax.set_title('Courbes ROC — Comparaison des 3 Modèles', fontsize=14, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.grid(alpha=0.3); ax.set_xlim([-0.02,1.02]); ax.set_ylim([-0.02,1.02])
plt.tight_layout()
plt.savefig(f'{FIG}/roc_curves.png', bbox_inches='tight')
plt.close()
print("[7/8] roc_curves.png")

# ═══════════════════════════════════════
# 8. FIGURE — Feature Importance (3 modèles)
# ═══════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.suptitle('Importance des Features — Top 15', fontsize=14, fontweight='bold', y=1.02)

# Elastic Net coefficients
lr = best['Elastic Net (L1+L2)']
coefs = pd.Series(np.abs(lr.coef_[0]), index=X.columns).sort_values().tail(15)
clr = ['#6366f1' if v > coefs.median() else '#94a3b8' for v in coefs]
axes[0].barh(coefs.index, coefs.values, color=clr, edgecolor='white', linewidth=0.5)
axes[0].set_title('Elastic Net (L1+L2)\n(|Coefficients|)', fontweight='bold')
axes[0].set_xlabel('Importance (abs coef)')
axes[0].grid(axis='x', alpha=0.3)

# Random Forest
rf = best['Random Forest']
imp_rf = pd.Series(rf.feature_importances_, index=X.columns).sort_values().tail(15)
clr2 = ['#22c55e' if v > imp_rf.median() else '#94a3b8' for v in imp_rf]
axes[1].barh(imp_rf.index, imp_rf.values, color=clr2, edgecolor='white', linewidth=0.5)
axes[1].set_title('Random Forest\n(Gini Importance)', fontweight='bold')
axes[1].set_xlabel('Importance (Gini)')
axes[1].grid(axis='x', alpha=0.3)

# XGBoost
xgb = best['XGBoost']
imp_xgb = pd.Series(xgb.feature_importances_, index=X.columns).sort_values().tail(15)
clr3 = ['#ef4444' if v > imp_xgb.median() else '#94a3b8' for v in imp_xgb]
axes[2].barh(imp_xgb.index, imp_xgb.values, color=clr3, edgecolor='white', linewidth=0.5)
axes[2].set_title('XGBoost\n(Gain Importance)', fontweight='bold')
axes[2].set_xlabel('Importance (Gain)')
axes[2].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{FIG}/feature_importance.png', bbox_inches='tight')
plt.close()
print("[8/8] feature_importance.png")

# ═══════════════════════════════════════
# SAVE MODELS
# ═══════════════════════════════════════
best_name = max(best, key=lambda n: f1_score(y_te, best[n].predict(X_te_s)))
joblib.dump(best[best_name], f'{MDL}/best_model.pkl')
joblib.dump(sc, f'{MDL}/scaler.pkl')
joblib.dump(list(X.columns), f'{MDL}/feature_names.pkl')

# Classification reports
with open(f'outputs/classification_reports.txt', 'w', encoding='utf-8') as f:
    for name, model in best.items():
        yp = model.predict(X_te_s)
        f.write(f"\n{'='*50}\n  {name}\n{'='*50}\n")
        f.write(classification_report(y_te, yp, target_names=['Non converti','Converti'], digits=4))

# Comparison CSV
comp = []
for name, model in best.items():
    yp=model.predict(X_te_s);ypr=model.predict_proba(X_te_s)[:,1]
    comp.append({'Modele':name,'Accuracy':round(accuracy_score(y_te,yp),4),'F1':round(f1_score(y_te,yp),4),'AUC':round(roc_auc_score(y_te,ypr),4)})
pd.DataFrame(comp).to_csv(f'outputs/model_comparison.csv', index=False)

print(f"\n{'='*55}")
print(f"  TOUTES LES FIGURES MISES A JOUR")
print(f"  Meilleur modele: {best_name}")
print(f"{'='*55}")
