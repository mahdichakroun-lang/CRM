"""
CRISP-DM — Phase 1 : Data Understanding (Exploration des Données)
══════════════════════════════════════════════════════════════════
Objectif : Comprendre la structure, la distribution et les corrélations
           du dataset avant toute transformation.

Sorties  : Figures dans ml/outputs/figures/
           - correlation_matrix.png
           - distribution_features.png
           - conversion_by_source.png
           - conversion_by_sector.png
           - descriptive_stats.csv
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "leads_dataset.csv")
FIG_DIR = os.path.join(BASE_DIR, "outputs", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ── Style ──
sns.set_theme(style="whitegrid", font_scale=0.95)
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
    'font.family': 'sans-serif',
})


def load_data():
    """Charge le dataset brut."""
    df = pd.read_csv(DATA_PATH)
    print(f"{'='*60}")
    print(f"  PHASE 1 — DATA UNDERSTANDING (EDA)")
    print(f"{'='*60}")
    print(f"\n[INFO] Dataset charge : {df.shape[0]} lignes x {df.shape[1]} colonnes")
    return df


def descriptive_statistics(df):
    """Statistiques descriptives completes."""
    print(f"\n{'─'*40}")
    print(f"  1.1 Statistiques Descriptives")
    print(f"{'─'*40}")

    # Types de colonnes
    print(f"\n  Types des colonnes :")
    for col in df.columns:
        print(f"    {col:25s} : {df[col].dtype}  |  {df[col].nunique():4d} uniques  |  {df[col].isnull().sum()} nulls")

    # Stats numériques
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    desc = df[num_cols].describe().T
    desc['median'] = df[num_cols].median()
    desc['skew'] = df[num_cols].skew()
    desc['kurtosis'] = df[num_cols].kurtosis()

    print(f"\n  Statistiques numeriques :")
    print(desc.to_string())

    # Sauvegarde
    desc.to_csv(os.path.join(FIG_DIR, "descriptive_stats.csv"))
    print(f"\n  [SAVE] descriptive_stats.csv")

    return num_cols


def missing_values_analysis(df):
    """Analyse des valeurs manquantes."""
    print(f"\n{'─'*40}")
    print(f"  1.2 Analyse des Valeurs Manquantes")
    print(f"{'─'*40}")

    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({'count': missing, 'pct': missing_pct})
    missing_df = missing_df[missing_df['count'] > 0].sort_values('count', ascending=False)

    if missing_df.empty:
        print("  Aucune valeur manquante dans le dataset !")
    else:
        print(missing_df.to_string())

    # Vérification des champs vides (string vide != NaN)
    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        empty_count = (df[col] == '').sum()
        if empty_count > 0:
            print(f"  {col:25s} : {empty_count} chaines vides ({empty_count/len(df)*100:.1f}%)")


def target_distribution(df):
    """Distribution de la variable cible."""
    print(f"\n{'─'*40}")
    print(f"  1.3 Distribution de la Variable Cible")
    print(f"{'─'*40}")

    counts = df['converted'].value_counts()
    print(f"  Non converti (0) : {counts.get(0, 0):4d}  ({counts.get(0, 0)/len(df)*100:.1f}%)")
    print(f"  Converti     (1) : {counts.get(1, 0):4d}  ({counts.get(1, 0)/len(df)*100:.1f}%)")
    print(f"  Ratio            : 1:{counts.get(0,0)/max(1,counts.get(1,0)):.2f}")

    # Vérification de déséquilibre
    minority_pct = counts.min() / len(df) * 100
    if minority_pct < 20:
        print(f"  [WARN] Dataset desequilibre ({minority_pct:.1f}% classe minoritaire)")
    else:
        print(f"  [OK] Equilibre acceptable ({minority_pct:.1f}% classe minoritaire)")


def correlation_matrix(df, num_cols):
    """Matrice de corrélation avec heatmap."""
    print(f"\n{'─'*40}")
    print(f"  1.4 Matrice de Correlation")
    print(f"{'─'*40}")

    # Sélection des colonnes numériques pertinentes
    corr_cols = [c for c in num_cols if c not in ['lead_id', 'confidence_score']]
    corr = df[corr_cols].corr()

    # Corrélations avec la cible
    target_corr = corr['converted'].drop('converted').sort_values(ascending=False)
    print(f"\n  Correlations avec 'converted' :")
    for feat, val in target_corr.items():
        bar = '█' * int(abs(val) * 30)
        sign = '+' if val > 0 else '-'
        print(f"    {feat:25s} : {sign}{abs(val):.3f}  {bar}")

    # Heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(250, 15, s=75, l=40, n=12, center="light", as_cmap=True)
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap=cmap,
                center=0, square=True, linewidths=0.8,
                cbar_kws={'shrink': 0.7, 'label': 'Coefficient de correlation'},
                ax=ax, vmin=-1, vmax=1)
    ax.set_title('Matrice de Correlation — Features du Lead Scoring', fontsize=13, fontweight='bold', pad=15)
    plt.savefig(os.path.join(FIG_DIR, "correlation_matrix.png"))
    plt.close()
    print(f"\n  [SAVE] correlation_matrix.png")


def feature_distributions(df):
    """Distribution des features numériques."""
    print(f"\n{'─'*40}")
    print(f"  1.5 Distribution des Features")
    print(f"{'─'*40}")

    plot_cols = ['estimated_value', 'days_in_pipeline', 'activities_count', 'calls', 'emails_sent', 'meetings']

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle('Distribution des Features Numeriques', fontsize=14, fontweight='bold', y=1.01)

    for i, col in enumerate(plot_cols):
        ax = axes[i // 3][i % 3]
        # Histogramme par classe
        df[df['converted'] == 0][col].hist(bins=25, alpha=0.6, color='#ef4444', label='Non converti', ax=ax, density=True)
        df[df['converted'] == 1][col].hist(bins=25, alpha=0.6, color='#22c55e', label='Converti', ax=ax, density=True)
        ax.set_title(col, fontsize=11, fontweight='semibold')
        ax.set_xlabel('')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "distribution_features.png"))
    plt.close()
    print(f"  [SAVE] distribution_features.png")


def conversion_by_category(df):
    """Taux de conversion par source et par secteur."""
    print(f"\n{'─'*40}")
    print(f"  1.6 Taux de Conversion par Categorie")
    print(f"{'─'*40}")

    # ── Par Source ──
    source_stats = df.groupby('source').agg(
        total=('converted', 'count'),
        converted=('converted', 'sum')
    ).assign(rate=lambda x: (x['converted'] / x['total'] * 100).round(1))
    source_stats = source_stats.sort_values('rate', ascending=True)

    print(f"\n  Conversion par source :")
    for src, row in source_stats.iterrows():
        bar = '█' * int(row['rate'] / 2)
        print(f"    {src:15s} : {row['total']:3.0f} leads -> {row['converted']:3.0f} convertis ({row['rate']:.0f}%)  {bar}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Bar chart source
    colors_src = ['#ef4444' if r < 30 else '#f59e0b' if r < 50 else '#22c55e' for r in source_stats['rate']]
    axes[0].barh(source_stats.index, source_stats['rate'], color=colors_src, edgecolor='white', linewidth=0.5)
    axes[0].set_xlabel('Taux de conversion (%)')
    axes[0].set_title('Taux de Conversion par Source', fontsize=12, fontweight='bold')
    for i, (_, row) in enumerate(source_stats.iterrows()):
        axes[0].text(row['rate'] + 1, i, f"{row['rate']:.0f}%", va='center', fontsize=9, fontweight='bold')
    axes[0].set_xlim(0, max(source_stats['rate']) + 10)
    axes[0].grid(axis='x', alpha=0.3)

    # ── Par Secteur ──
    sector_stats = df.groupby('sector').agg(
        total=('converted', 'count'),
        converted=('converted', 'sum')
    ).assign(rate=lambda x: (x['converted'] / x['total'] * 100).round(1))
    sector_stats = sector_stats.sort_values('rate', ascending=True)

    print(f"\n  Conversion par secteur :")
    for sec, row in sector_stats.iterrows():
        bar = '█' * int(row['rate'] / 2)
        print(f"    {sec:25s} : {row['total']:3.0f} leads -> {row['converted']:3.0f} convertis ({row['rate']:.0f}%)  {bar}")

    colors_sec = ['#ef4444' if r < 30 else '#f59e0b' if r < 50 else '#22c55e' for r in sector_stats['rate']]
    axes[1].barh(sector_stats.index, sector_stats['rate'], color=colors_sec, edgecolor='white', linewidth=0.5)
    axes[1].set_xlabel('Taux de conversion (%)')
    axes[1].set_title('Taux de Conversion par Secteur', fontsize=12, fontweight='bold')
    for i, (_, row) in enumerate(sector_stats.iterrows()):
        axes[1].text(row['rate'] + 1, i, f"{row['rate']:.0f}%", va='center', fontsize=9, fontweight='bold')
    axes[1].set_xlim(0, max(sector_stats['rate']) + 10)
    axes[1].grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "conversion_by_category.png"))
    plt.close()
    print(f"\n  [SAVE] conversion_by_category.png")


def boxplot_analysis(df):
    """Boxplots pour détecter les outliers."""
    print(f"\n{'─'*40}")
    print(f"  1.7 Analyse des Outliers (Boxplots)")
    print(f"{'─'*40}")

    plot_cols = ['estimated_value', 'days_in_pipeline', 'activities_count']

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle('Boxplots par Classe de Conversion', fontsize=13, fontweight='bold', y=1.02)

    for i, col in enumerate(plot_cols):
        sns.boxplot(data=df, x='converted', y=col, ax=axes[i],
                    palette=['#ef4444', '#22c55e'], width=0.5,
                    flierprops={'markersize': 3, 'alpha': 0.5})
        axes[i].set_title(col, fontsize=11, fontweight='semibold')
        axes[i].set_xticklabels(['Non converti', 'Converti'])
        axes[i].grid(axis='y', alpha=0.3)

        # Détection outliers IQR
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum()
        print(f"  {col:25s} : {outliers} outliers detectes (IQR method)")

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "boxplots_outliers.png"))
    plt.close()
    print(f"\n  [SAVE] boxplots_outliers.png")


def run_eda():
    """Execute toute l'analyse exploratoire."""
    df = load_data()
    num_cols = descriptive_statistics(df)
    missing_values_analysis(df)
    target_distribution(df)
    correlation_matrix(df, num_cols)
    feature_distributions(df)
    conversion_by_category(df)
    boxplot_analysis(df)

    print(f"\n{'='*60}")
    print(f"  PHASE 1 TERMINEE — {len(os.listdir(FIG_DIR))} fichiers generes")
    print(f"  Dossier : {FIG_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    run_eda()
