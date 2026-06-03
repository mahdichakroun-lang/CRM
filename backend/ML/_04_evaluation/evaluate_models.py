"""
CRISP-DM — Phase 4 : Evaluation (Evaluation des Modeles)
═══════════════════════════════════════════════════════
Objectif : Evaluer les modeles sur le test set (jamais vu).
           - Matrice de confusion pour chaque modele
           - Courbes ROC comparatives
           - Classification Report detaille
           - Feature Importance (top 15)
           - Choix du modele final

Sorties  : ml/outputs/figures/
           - confusion_matrices.png
           - roc_curves.png
           - feature_importance.png
           - classification_reports.txt
"""

import os
import warnings
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, accuracy_score, precision_score,
    recall_score, f1_score, roc_auc_score
)

warnings.filterwarnings('ignore')

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
MODEL_DIR = os.path.join(OUTPUT_DIR, "models")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")


def load_test_data_and_models():
    """Charge les données test et les modèles entraînés."""
    print(f"{'='*60}")
    print(f"  PHASE 4 — EVALUATION (TEST SET)")
    print(f"{'='*60}")

    X_test = pd.read_csv(os.path.join(OUTPUT_DIR, "X_test.csv")).values
    y_test = pd.read_csv(os.path.join(OUTPUT_DIR, "y_test.csv")).values.ravel()

    with open(os.path.join(OUTPUT_DIR, "feature_names.txt")) as f:
        feature_names = f.read().strip().split('\n')

    # Charger les modèles
    models = {}
    model_files = {
        'Logistic Regression (L2)': 'logistic_regression_l2.pkl',
        'Random Forest': 'random_forest.pkl',
        'Gradient Boosting': 'gradient_boosting.pkl',
    }

    for name, filename in model_files.items():
        path = os.path.join(MODEL_DIR, filename)
        if os.path.exists(path):
            models[name] = joblib.load(path)
            print(f"  [LOAD] {filename}")
        else:
            print(f"  [WARN] {filename} non trouve")

    print(f"\n  Test set : {X_test.shape[0]} echantillons")
    print(f"  Modeles  : {len(models)}")

    return X_test, y_test, models, feature_names


def confusion_matrices(models, X_test, y_test):
    """Matrice de confusion pour chaque modèle."""
    print(f"\n{'─'*40}")
    print(f"  4.1 Matrices de Confusion")
    print(f"{'─'*40}")

    n_models = len(models)
    fig, axes = plt.subplots(1, n_models, figsize=(6 * n_models, 5))
    if n_models == 1:
        axes = [axes]

    fig.suptitle('Matrices de Confusion — Evaluation sur le Test Set',
                 fontsize=14, fontweight='bold', y=1.03)

    for i, (name, model) in enumerate(models.items()):
        y_pred = model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)

        # Pourcentages
        cm_pct = cm.astype('float') / cm.sum(axis=1, keepdims=True) * 100

        # Annotations combinées (count + %)
        annot = np.array([
            [f"{cm[r][c]}\n({cm_pct[r][c]:.1f}%)" for c in range(2)]
            for r in range(2)
        ])

        sns.heatmap(cm, annot=annot, fmt='', cmap='Blues',
                    xticklabels=['Non converti', 'Converti'],
                    yticklabels=['Non converti', 'Converti'],
                    ax=axes[i], cbar=False, linewidths=2, linecolor='white',
                    annot_kws={'size': 12, 'fontweight': 'bold'})

        axes[i].set_title(name, fontsize=11, fontweight='bold', pad=10)
        axes[i].set_ylabel('Reel' if i == 0 else '')
        axes[i].set_xlabel('Predit')

        # Métriques sous la matrice
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        axes[i].text(1, 2.6, f"Acc={acc:.3f}  F1={f1:.3f}",
                     ha='center', fontsize=10, style='italic',
                     color='#555555')

        print(f"\n  [{name}]")
        print(f"    TP={cm[1][1]:3d}  FP={cm[0][1]:3d}")
        print(f"    FN={cm[1][0]:3d}  TN={cm[0][0]:3d}")
        print(f"    Accuracy  = {acc:.4f}")
        print(f"    Precision = {precision_score(y_test, y_pred):.4f}")
        print(f"    Recall    = {recall_score(y_test, y_pred):.4f}")
        print(f"    F1-Score  = {f1:.4f}")

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "confusion_matrices.png"))
    plt.close()
    print(f"\n  [SAVE] confusion_matrices.png")


def roc_curves(models, X_test, y_test):
    """Courbes ROC comparatives."""
    print(f"\n{'─'*40}")
    print(f"  4.2 Courbes ROC Comparatives")
    print(f"{'─'*40}")

    fig, ax = plt.subplots(figsize=(8, 7))
    colors = ['#6366f1', '#ef4444', '#22c55e']

    for i, (name, model) in enumerate(models.items()):
        if hasattr(model, 'predict_proba'):
            y_prob = model.predict_proba(X_test)[:, 1]
        else:
            y_prob = model.decision_function(X_test)

        fpr, tpr, thresholds = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

        ax.plot(fpr, tpr, color=colors[i], lw=2.5,
                label=f'{name} (AUC = {roc_auc:.4f})')

        print(f"  {name:30s} : AUC = {roc_auc:.4f}")

        # Trouver le seuil optimal (Youden's J)
        j_scores = tpr - fpr
        best_idx = np.argmax(j_scores)
        best_threshold = thresholds[best_idx]
        ax.scatter(fpr[best_idx], tpr[best_idx], s=80, color=colors[i],
                   edgecolors='white', linewidth=2, zorder=5)
        print(f"    Seuil optimal (Youden) : {best_threshold:.3f}")

    # Ligne diagonale (random classifier)
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.4, label='Random (AUC = 0.500)')

    ax.set_xlabel('Taux de Faux Positifs (FPR)', fontsize=11)
    ax.set_ylabel('Taux de Vrais Positifs (TPR)', fontsize=11)
    ax.set_title('Courbes ROC — Comparaison des 3 Modeles', fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(alpha=0.3)
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "roc_curves.png"))
    plt.close()
    print(f"\n  [SAVE] roc_curves.png")


def classification_reports(models, X_test, y_test):
    """Classification report détaillé pour chaque modèle."""
    print(f"\n{'─'*40}")
    print(f"  4.3 Classification Reports")
    print(f"{'─'*40}")

    report_path = os.path.join(OUTPUT_DIR, "classification_reports.txt")

    with open(report_path, 'w', encoding='utf-8') as f:
        for name, model in models.items():
            y_pred = model.predict(X_test)
            report = classification_report(
                y_test, y_pred,
                target_names=['Non converti', 'Converti'],
                digits=4
            )
            f.write(f"\n{'='*50}\n")
            f.write(f"  {name}\n")
            f.write(f"{'='*50}\n")
            f.write(report)
            f.write("\n")

            print(f"\n  [{name}]")
            print(report)

    print(f"  [SAVE] classification_reports.txt")


def feature_importance(models, feature_names):
    """Feature importance pour les modèles basés sur les arbres."""
    print(f"\n{'─'*40}")
    print(f"  4.4 Feature Importance (Top 15)")
    print(f"{'─'*40}")

    # Modèles avec feature_importances_
    tree_models = {name: m for name, m in models.items()
                   if hasattr(m, 'feature_importances_')}

    if not tree_models:
        print("  Aucun modele a base d'arbres trouve")
        return

    # Ajout de Logistic Regression coefficients si disponible
    lr_models = {name: m for name, m in models.items()
                 if hasattr(m, 'coef_')}

    n_plots = len(tree_models) + len(lr_models)
    fig, axes = plt.subplots(1, n_plots, figsize=(7 * n_plots, 8))
    if n_plots == 1:
        axes = [axes]

    fig.suptitle('Importance des Features — Top 15',
                 fontsize=14, fontweight='bold', y=1.02)

    plot_idx = 0

    # LR coefficients
    for name, model in lr_models.items():
        coefs = np.abs(model.coef_[0])
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': coefs
        }).sort_values('importance', ascending=True).tail(15)

        colors = ['#6366f1' if imp > importance_df['importance'].median() else '#94a3b8'
                  for imp in importance_df['importance']]

        axes[plot_idx].barh(importance_df['feature'], importance_df['importance'],
                            color=colors, edgecolor='white', linewidth=0.5)
        axes[plot_idx].set_title(f'{name}\n(|Coefficients|)', fontsize=11, fontweight='bold')
        axes[plot_idx].set_xlabel('Importance (abs coef)')
        axes[plot_idx].grid(axis='x', alpha=0.3)

        print(f"\n  [{name}] Top 5 features :")
        for _, row in importance_df.tail(5).iterrows():
            print(f"    {row['feature']:30s} : {row['importance']:.4f}")

        plot_idx += 1

    # Tree-based importances
    for name, model in tree_models.items():
        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=True).tail(15)

        colors = ['#22c55e' if imp > importance_df['importance'].median() else '#94a3b8'
                  for imp in importance_df['importance']]

        axes[plot_idx].barh(importance_df['feature'], importance_df['importance'],
                            color=colors, edgecolor='white', linewidth=0.5)
        axes[plot_idx].set_title(f'{name}\n(Feature Importance)', fontsize=11, fontweight='bold')
        axes[plot_idx].set_xlabel('Importance (Gini)')
        axes[plot_idx].grid(axis='x', alpha=0.3)

        print(f"\n  [{name}] Top 5 features :")
        for _, row in importance_df.tail(5).iterrows():
            print(f"    {row['feature']:30s} : {row['importance']:.4f}")

        plot_idx += 1

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "feature_importance.png"))
    plt.close()
    print(f"\n  [SAVE] feature_importance.png")


def final_model_selection(models, X_test, y_test):
    """Selection du meilleur modele et sauvegarde."""
    print(f"\n{'─'*40}")
    print(f"  4.5 Selection du Modele Final")
    print(f"{'─'*40}")

    best_name = None
    best_f1 = 0

    summary = []
    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc_val = roc_auc_score(y_test, y_prob) if y_prob is not None else 0

        summary.append({
            'Modele': name, 'Accuracy': acc, 'Precision': prec,
            'Recall': rec, 'F1': f1, 'AUC-ROC': auc_val
        })

        if f1 > best_f1:
            best_f1 = f1
            best_name = name

    summary_df = pd.DataFrame(summary).sort_values('F1', ascending=False)
    print(f"\n  Classement final (par F1-Score) :")
    print(f"  {'─'*72}")
    for _, row in summary_df.iterrows():
        marker = " <<< BEST" if row['Modele'] == best_name else ""
        print(f"  {row['Modele']:30s} | Acc={row['Accuracy']:.4f} | F1={row['F1']:.4f} | AUC={row['AUC-ROC']:.4f}{marker}")

    # Sauvegarder le meilleur modèle
    best_model = models[best_name]
    joblib.dump(best_model, os.path.join(MODEL_DIR, "best_model.pkl"))
    with open(os.path.join(MODEL_DIR, "best_model_name.txt"), 'w') as f:
        f.write(best_name)

    print(f"\n  [BEST] {best_name} selectionne (F1={best_f1:.4f})")
    print(f"  [SAVE] best_model.pkl")

    summary_df.to_csv(os.path.join(OUTPUT_DIR, "final_comparison.csv"), index=False)

    return best_name


def run_evaluation():
    """Execute toute l'évaluation."""
    X_test, y_test, models, feature_names = load_test_data_and_models()
    confusion_matrices(models, X_test, y_test)
    roc_curves(models, X_test, y_test)
    classification_reports(models, X_test, y_test)
    feature_importance(models, feature_names)
    best = final_model_selection(models, X_test, y_test)

    print(f"\n{'='*60}")
    print(f"  PHASE 4 TERMINEE — Modele final : {best}")
    print(f"{'='*60}")


if __name__ == "__main__":
    run_evaluation()
