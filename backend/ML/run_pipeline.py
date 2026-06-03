"""
CRISP-DM — Pipeline Complet Lead Scoring
═════════════════════════════════════════
Execute toutes les phases du pipeline CRISP-DM :
  Phase 1 : Data Understanding  (EDA)
  Phase 2 : Data Preparation    (Preprocessing)
  Phase 3 : Modeling            (Train + CV)
  Phase 4 : Evaluation          (Test + Comparaison)

Usage : python run_pipeline.py
"""

import os
import sys
import time

# Ajouter le dossier ml au path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def main():
    start_total = time.time()

    print()
    print("╔" + "═" * 58 + "╗")
    print("║   CRISP-DM Pipeline — Lead Scoring CRM                  ║")
    print("║   FRS — IT Development Company                          ║")
    print("╚" + "═" * 58 + "╝")
    print()

    # ── Phase 1 : Data Understanding ──
    print("\n" + "▓" * 60)
    print("  PHASE 1/4 : Data Understanding")
    print("▓" * 60)
    from _01_data_understanding.eda_analysis import run_eda
    run_eda()

    # ── Phase 2 : Data Preparation ──
    print("\n" + "▓" * 60)
    print("  PHASE 2/4 : Data Preparation")
    print("▓" * 60)
    from _02_data_preparation.preprocessing import run_preprocessing
    run_preprocessing()

    # ── Phase 3 : Modeling ──
    print("\n" + "▓" * 60)
    print("  PHASE 3/4 : Modeling")
    print("▓" * 60)
    from _03_modeling.train_models import run_modeling
    run_modeling()

    # ── Phase 4 : Evaluation ──
    print("\n" + "▓" * 60)
    print("  PHASE 4/4 : Evaluation")
    print("▓" * 60)
    from _04_evaluation.evaluate_models import run_evaluation
    run_evaluation()

    # ── Résumé final ──
    elapsed = time.time() - start_total
    print()
    print("╔" + "═" * 58 + "╗")
    print("║   PIPELINE TERMINE AVEC SUCCES                          ║")
    print(f"║   Temps total : {elapsed:.1f}s{' ' * (41 - len(f'{elapsed:.1f}'))}║")
    print("╠" + "═" * 58 + "╣")
    print("║   Fichiers generes :                                    ║")
    print("║   outputs/figures/                                      ║")
    print("║     - correlation_matrix.png                            ║")
    print("║     - distribution_features.png                         ║")
    print("║     - conversion_by_category.png                        ║")
    print("║     - boxplots_outliers.png                             ║")
    print("║     - confusion_matrices.png                            ║")
    print("║     - roc_curves.png                                    ║")
    print("║     - feature_importance.png                            ║")
    print("║   outputs/models/                                       ║")
    print("║     - best_model.pkl                                    ║")
    print("║     - scaler.pkl                                        ║")
    print("╚" + "═" * 58 + "╝")


if __name__ == "__main__":
    main()
