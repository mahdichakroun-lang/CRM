"""
CRISP-DM — Phase 2 : Data Preparation (Preprocessing)
══════════════════════════════════════════════════════
Objectif : Préparer les données pour le modeling.
           - Feature Engineering
           - Encodage catégoriel (One-Hot + Label)
           - Normalisation / Standardisation
           - Split train/test stratifié
           - Sauvegarde des données préparées

Sorties  : ml/outputs/
           - X_train.csv, X_test.csv, y_train.csv, y_test.csv
           - feature_names.txt
           - preprocessing_report.txt
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "leads_dataset.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_raw_data():
    """Charge les données brutes."""
    print(f"{'='*60}")
    print(f"  PHASE 2 — DATA PREPARATION (PREPROCESSING)")
    print(f"{'='*60}")

    df = pd.read_csv(DATA_PATH)
    print(f"\n[INFO] Dataset brut : {df.shape[0]} lignes x {df.shape[1]} colonnes")
    return df


def feature_engineering(df):
    """
    Création de nouvelles features à partir des données existantes.
    C'est ici que le Data Engineer ajoute de la valeur.
    """
    print(f"\n{'─'*40}")
    print(f"  2.1 Feature Engineering")
    print(f"{'─'*40}")

    df = df.copy()

    # ── Feature 1 : Contact completeness score (0-2) ──
    df['contact_score'] = df['has_email'].astype(int) + df['has_phone'].astype(int)
    print(f"  [+] contact_score       : combinaison has_email + has_phone (0-2)")

    # ── Feature 2 : Activity intensity (activités par jour dans le pipeline) ──
    df['activity_intensity'] = (df['activities_count'] / df['days_in_pipeline'].clip(lower=1)).round(4)
    print(f"  [+] activity_intensity  : activites / jours dans le pipeline")

    # ── Feature 3 : Meeting ratio (proportion de RDV dans les activités) ──
    df['meeting_ratio'] = (df['meetings'] / df['activities_count'].clip(lower=1)).round(4)
    print(f"  [+] meeting_ratio       : meetings / total activites")

    # ── Feature 4 : Is high value (lead à forte valeur) ──
    value_median = df['estimated_value'].median()
    df['is_high_value'] = (df['estimated_value'] > value_median).astype(int)
    print(f"  [+] is_high_value       : valeur > {value_median:.0f} DT (mediane)")

    # ── Feature 5 : Pipeline freshness (lead frais < 30 jours) ──
    df['is_fresh'] = (df['days_in_pipeline'] <= 30).astype(int)
    print(f"  [+] is_fresh            : pipeline <= 30 jours")

    # ── Feature 6 : Log-transformed estimated value (réduction de l'asymétrie) ──
    df['log_value'] = np.log1p(df['estimated_value'])
    print(f"  [+] log_value           : log(1 + estimated_value) pour normaliser la distribution")

    # ── Feature 7 : Has activities (binary) ──
    df['has_activities'] = (df['activities_count'] > 0).astype(int)
    print(f"  [+] has_activities      : indicateur binaire (au moins 1 activite)")

    print(f"\n  [RESULT] {df.shape[1]} colonnes apres feature engineering (+7 nouvelles)")
    return df


def encode_categoricals(df):
    """
    Encodage des variables catégorielles.
    - Source : One-Hot Encoding (pas d'ordre naturel)
    - Sector : One-Hot Encoding
    - Status : Label Encoding (exclu du modèle car leak potentiel)
    """
    print(f"\n{'─'*40}")
    print(f"  2.2 Encodage des Variables Categorielles")
    print(f"{'─'*40}")

    df = df.copy()

    # ── One-Hot Encoding : Source ──
    source_dummies = pd.get_dummies(df['source'], prefix='source', dtype=int)
    print(f"  [OHE] source            : {list(source_dummies.columns)}")

    # ── One-Hot Encoding : Sector ──
    sector_dummies = pd.get_dummies(df['sector'], prefix='sector', dtype=int)
    print(f"  [OHE] sector            : {len(sector_dummies.columns)} categories")

    # Concaténation
    df = pd.concat([df, source_dummies, sector_dummies], axis=1)

    # Suppression des colonnes originales catégorielles et non-pertinentes
    cols_to_drop = [
        'lead_id',           # Identifiant - pas une feature
        'company_name',      # Texte libre - pas exploitable directement
        'contact_name',      # Texte libre
        'email',             # Texte libre (on utilise has_email)
        'phone',             # Texte libre (on utilise has_phone)
        'owner',             # Texte libre (pourrait être encodé mais trop de biais)
        'source',            # Remplacé par OHE
        'sector',            # Remplacé par OHE
        'status',            # Variable CIBLE intermédiaire - LEAK si utilisée
        'created_at',        # Date brute - on utilise days_in_pipeline
        'confidence_score',  # Score de confiance interne (leak si utilisé)
    ]

    df = df.drop(columns=cols_to_drop, errors='ignore')
    print(f"\n  [DROP] Colonnes supprimees : {len(cols_to_drop)}")
    print(f"  [RESULT] {df.shape[1]} colonnes apres encodage")

    return df


def scale_features(X_train, X_test, feature_names):
    """
    Standardisation (StandardScaler) des features numériques.
    Fit uniquement sur le train pour éviter le data leakage.
    """
    print(f"\n{'─'*40}")
    print(f"  2.3 Standardisation des Features")
    print(f"{'─'*40}")

    scaler = StandardScaler()

    # Features numériques à scaler (pas les binaires)
    num_features = ['estimated_value', 'days_in_pipeline', 'activities_count',
                    'calls', 'emails_sent', 'meetings', 'activity_intensity',
                    'meeting_ratio', 'log_value']
    num_idx = [i for i, f in enumerate(feature_names) if f in num_features]

    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    if num_idx:
        X_train_scaled[:, num_idx] = scaler.fit_transform(X_train[:, num_idx])
        X_test_scaled[:, num_idx] = scaler.transform(X_test[:, num_idx])
        print(f"  [SCALE] {len(num_idx)} features numeriques standardisees (mean=0, std=1)")
        print(f"  [INFO] Fit sur train uniquement (pas de data leakage)")
    else:
        print(f"  [WARN] Aucune feature numerique trouvee a standardiser")

    # Vérification
    for i in num_idx[:3]:
        print(f"    {feature_names[i]:25s} : mean={X_train_scaled[:,i].mean():.4f}, std={X_train_scaled[:,i].std():.4f}")

    return X_train_scaled, X_test_scaled, scaler


def split_data(df):
    """
    Séparation train/test avec stratification.
    80% train / 20% test.
    """
    print(f"\n{'─'*40}")
    print(f"  2.4 Split Train / Test (Stratifie)")
    print(f"{'─'*40}")

    # Séparation features / target
    y = df['converted'].values
    X = df.drop(columns=['converted']).values
    feature_names = [c for c in df.columns if c != 'converted']

    # Split stratifié (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"  Train : {X_train.shape[0]} echantillons ({X_train.shape[0]/len(df)*100:.0f}%)")
    print(f"  Test  : {X_test.shape[0]} echantillons ({X_test.shape[0]/len(df)*100:.0f}%)")
    print(f"  Features : {X_train.shape[1]}")

    # Vérification de la stratification
    train_ratio = y_train.mean() * 100
    test_ratio = y_test.mean() * 100
    print(f"\n  Stratification :")
    print(f"    Train : {train_ratio:.1f}% convertis")
    print(f"    Test  : {test_ratio:.1f}% convertis")
    print(f"    [OK] Ratio preserve" if abs(train_ratio - test_ratio) < 3 else "    [WARN] Ratio desequilibre")

    return X_train, X_test, y_train, y_test, feature_names


def save_prepared_data(X_train, X_test, y_train, y_test, feature_names, scaler):
    """Sauvegarde des données préparées."""
    print(f"\n{'─'*40}")
    print(f"  2.5 Sauvegarde des Donnees Preparees")
    print(f"{'─'*40}")

    # Sauvegarder en CSV
    pd.DataFrame(X_train, columns=feature_names).to_csv(os.path.join(OUTPUT_DIR, "X_train.csv"), index=False)
    pd.DataFrame(X_test, columns=feature_names).to_csv(os.path.join(OUTPUT_DIR, "X_test.csv"), index=False)
    pd.Series(y_train, name='converted').to_csv(os.path.join(OUTPUT_DIR, "y_train.csv"), index=False)
    pd.Series(y_test, name='converted').to_csv(os.path.join(OUTPUT_DIR, "y_test.csv"), index=False)

    # Feature names
    with open(os.path.join(OUTPUT_DIR, "feature_names.txt"), 'w') as f:
        f.write('\n'.join(feature_names))

    # Scaler
    import joblib
    joblib.dump(scaler, os.path.join(OUTPUT_DIR, "models", "scaler.pkl"))

    print(f"  [SAVE] X_train.csv      : {X_train.shape}")
    print(f"  [SAVE] X_test.csv       : {X_test.shape}")
    print(f"  [SAVE] y_train.csv      : {y_train.shape}")
    print(f"  [SAVE] y_test.csv       : {y_test.shape}")
    print(f"  [SAVE] feature_names.txt: {len(feature_names)} features")
    print(f"  [SAVE] scaler.pkl")


def run_preprocessing():
    """Execute tout le pipeline de préparation."""
    df = load_raw_data()
    df = feature_engineering(df)
    df = encode_categoricals(df)
    X_train, X_test, y_train, y_test, feature_names = split_data(df)
    X_train, X_test, scaler = scale_features(X_train, X_test, feature_names)
    save_prepared_data(X_train, X_test, y_train, y_test, feature_names, scaler)

    print(f"\n{'='*60}")
    print(f"  PHASE 2 TERMINEE — Donnees pretes pour le modeling")
    print(f"{'='*60}")

    return X_train, X_test, y_train, y_test, feature_names


if __name__ == "__main__":
    run_preprocessing()
