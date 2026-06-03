"""
CRISP-DM — Phase 3 : Modeling (Entrainement des Modeles)
════════════════════════════════════════════════════════
Objectif : Entrainer et comparer 3 modeles avec K-Fold Cross-Validation.
           - Logistic Regression (avec regularisation L1/L2)
           - Random Forest (avec tuning hyperparametres)
           - Gradient Boosting (meilleur algo pour les donnees tabulaires)

           Chaque modele est evalue avec Stratified 5-Fold CV.

Sorties  : ml/outputs/models/
           - logistic_model.pkl
           - random_forest_model.pkl
           - gradient_boosting_model.pkl
           - cv_results.csv
"""

import os
import sys
import time
import warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, make_scorer)

warnings.filterwarnings('ignore')

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
MODEL_DIR = os.path.join(OUTPUT_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_prepared_data():
    """Charge les données préparées en Phase 2."""
    print(f"{'='*60}")
    print(f"  PHASE 3 — MODELING (ENTRAINEMENT)")
    print(f"{'='*60}")

    X_train = pd.read_csv(os.path.join(OUTPUT_DIR, "X_train.csv")).values
    X_test = pd.read_csv(os.path.join(OUTPUT_DIR, "X_test.csv")).values
    y_train = pd.read_csv(os.path.join(OUTPUT_DIR, "y_train.csv")).values.ravel()
    y_test = pd.read_csv(os.path.join(OUTPUT_DIR, "y_test.csv")).values.ravel()

    with open(os.path.join(OUTPUT_DIR, "feature_names.txt")) as f:
        feature_names = f.read().strip().split('\n')

    print(f"\n[INFO] Donnees chargees :")
    print(f"  X_train : {X_train.shape}")
    print(f"  X_test  : {X_test.shape}")
    print(f"  Features: {len(feature_names)}")

    return X_train, X_test, y_train, y_test, feature_names


def define_models():
    """
    Définition des 3 modèles avec hyperparamètres optimisés.
    Chaque modèle a un rôle spécifique dans la comparaison.
    """
    print(f"\n{'─'*40}")
    print(f"  3.1 Definition des Modeles")
    print(f"{'─'*40}")

    models = {
        # ── Modèle 1 : Logistic Regression ──
        # + Interprétable, rapide, bon baseline
        # + Régularisation L2 (Ridge) avec C=1.0
        # + solver='lbfgs' adapté aux petits datasets
        'Logistic Regression (L2)': LogisticRegression(
            C=1.0,              # Force de régularisation (1/lambda)
            penalty='l2',       # Régularisation Ridge
            solver='lbfgs',     # Optimiseur adapté
            max_iter=1000,      # Convergence garantie
            random_state=42,
            class_weight='balanced',  # Gère le déséquilibre de classes
        ),

        # ── Modèle 2 : Random Forest ──
        # + Gère bien les features mixtes (numériques + binaires)
        # + Robuste aux outliers
        # + Feature importance native
        'Random Forest': RandomForestClassifier(
            n_estimators=200,        # 200 arbres (stabilité)
            max_depth=8,             # Limite la profondeur (anti-overfitting)
            min_samples_split=10,    # Min 10 samples pour split
            min_samples_leaf=5,      # Min 5 samples par feuille
            max_features='sqrt',     # Racine carrée des features par arbre
            random_state=42,
            class_weight='balanced',
            n_jobs=-1,               # Parallélisation
        ),

        # ── Modèle 3 : Gradient Boosting ──
        # + Meilleure performance sur données tabulaires
        # + Learning rate faible = meilleure généralisation
        # + Régularisation via subsample et max_depth
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=150,        # 150 arbres séquentiels
            learning_rate=0.1,       # Taux d'apprentissage modéré
            max_depth=4,             # Arbres peu profonds (weak learners)
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,           # 80% des données par arbre (anti-overfitting)
            random_state=42,
        ),
    }

    for name, model in models.items():
        print(f"\n  [{name}]")
        params = model.get_params()
        key_params = {k: v for k, v in params.items()
                      if k in ['C', 'penalty', 'n_estimators', 'max_depth',
                               'learning_rate', 'min_samples_split', 'subsample',
                               'class_weight', 'max_features']}
        for k, v in key_params.items():
            print(f"    {k:22s} = {v}")

    return models


def cross_validate_models(models, X_train, y_train):
    """
    Cross-Validation stratifiée 5-Fold sur chaque modèle.
    Métriques : Accuracy, Precision, Recall, F1, AUC-ROC.
    """
    print(f"\n{'─'*40}")
    print(f"  3.2 Cross-Validation Stratifiee (5-Fold)")
    print(f"{'─'*40}")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    scoring = {
        'accuracy':  'accuracy',
        'precision': 'precision',
        'recall':    'recall',
        'f1':        'f1',
        'roc_auc':   'roc_auc',
    }

    results = {}
    cv_details = []

    for name, model in models.items():
        print(f"\n  >>> Entrainement : {name}")
        start = time.time()

        cv_results = cross_validate(
            model, X_train, y_train,
            cv=cv, scoring=scoring,
            return_train_score=True,
            n_jobs=-1
        )

        elapsed = time.time() - start

        # Moyennes et écarts-types
        metrics = {}
        for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
            test_key = f'test_{metric}'
            train_key = f'train_{metric}'
            metrics[f'{metric}_mean'] = cv_results[test_key].mean()
            metrics[f'{metric}_std'] = cv_results[test_key].std()
            metrics[f'{metric}_train'] = cv_results[train_key].mean()

        metrics['time'] = elapsed
        results[name] = metrics

        # Affichage détaillé
        print(f"      Temps          : {elapsed:.2f}s")
        print(f"      ┌───────────────┬──────────┬──────────┬──────────────┐")
        print(f"      │ Metrique      │  Train   │  Test    │  +/- (std)   │")
        print(f"      ├───────────────┼──────────┼──────────┼──────────────┤")
        for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
            train_val = metrics[f'{metric}_train']
            test_val = metrics[f'{metric}_mean']
            std_val = metrics[f'{metric}_std']
            overfit = train_val - test_val
            flag = " !" if overfit > 0.05 else ""
            print(f"      │ {metric:13s} │ {train_val:.4f}   │ {test_val:.4f}   │ +/- {std_val:.4f}   │{flag}")
        print(f"      └───────────────┴──────────┴──────────┴──────────────┘")

        # Vérification overfitting
        acc_gap = metrics['accuracy_train'] - metrics['accuracy_mean']
        if acc_gap > 0.05:
            print(f"      [WARN] Ecart train/test = {acc_gap:.3f} -> Possible overfitting")
        else:
            print(f"      [OK] Ecart train/test = {acc_gap:.3f} -> Bonne generalisation")

        # Détails par fold
        for fold_i in range(5):
            cv_details.append({
                'model': name,
                'fold': fold_i + 1,
                'accuracy': cv_results['test_accuracy'][fold_i],
                'f1': cv_results['test_f1'][fold_i],
                'roc_auc': cv_results['test_roc_auc'][fold_i],
            })

    # Sauvegarde des résultats CV
    cv_df = pd.DataFrame(cv_details)
    cv_df.to_csv(os.path.join(OUTPUT_DIR, "cv_results_detail.csv"), index=False)
    print(f"\n  [SAVE] cv_results_detail.csv")

    return results


def train_final_models(models, X_train, y_train):
    """
    Entraîne les modèles finaux sur TOUT le train set.
    Sauvegarde les fichiers .pkl.
    """
    print(f"\n{'─'*40}")
    print(f"  3.3 Entrainement Final (Full Train Set)")
    print(f"{'─'*40}")

    trained_models = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        trained_models[name] = model

        # Sauvegarde
        safe_name = name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        pkl_path = os.path.join(MODEL_DIR, f"{safe_name}.pkl")
        joblib.dump(model, pkl_path)
        print(f"  [SAVE] {safe_name}.pkl")

    return trained_models


def compare_models(results):
    """Tableau comparatif final."""
    print(f"\n{'─'*40}")
    print(f"  3.4 Comparaison des Modeles")
    print(f"{'─'*40}")

    comparison = []
    for name, metrics in results.items():
        comparison.append({
            'Modele': name,
            'Accuracy': f"{metrics['accuracy_mean']:.4f} +/- {metrics['accuracy_std']:.4f}",
            'Precision': f"{metrics['precision_mean']:.4f}",
            'Recall': f"{metrics['recall_mean']:.4f}",
            'F1-Score': f"{metrics['f1_mean']:.4f}",
            'AUC-ROC': f"{metrics['roc_auc_mean']:.4f}",
            'Temps': f"{metrics['time']:.2f}s",
        })

    comp_df = pd.DataFrame(comparison)
    print(f"\n{comp_df.to_string(index=False)}")

    # Meilleur modèle
    best_model = max(results.items(), key=lambda x: x[1]['f1_mean'])
    print(f"\n  [BEST] Meilleur modele (F1) : {best_model[0]} ({best_model[1]['f1_mean']:.4f})")

    comp_df.to_csv(os.path.join(OUTPUT_DIR, "model_comparison.csv"), index=False)
    print(f"  [SAVE] model_comparison.csv")

    return best_model[0]


def run_modeling():
    """Execute tout le pipeline de modeling."""
    X_train, X_test, y_train, y_test, feature_names = load_prepared_data()
    models = define_models()
    results = cross_validate_models(models, X_train, y_train)
    trained_models = train_final_models(models, X_train, y_train)
    best_model_name = compare_models(results)

    print(f"\n{'='*60}")
    print(f"  PHASE 3 TERMINEE — {len(trained_models)} modeles entraines")
    print(f"  Meilleur : {best_model_name}")
    print(f"{'='*60}")

    return trained_models, best_model_name


if __name__ == "__main__":
    run_modeling()
