"""
FloraCare AI – Model Evaluation Script
Computes accuracy, precision, recall, F1 and saves evaluation_report.json.

Usage:
    python ml_model/evaluation.py
    python ml_model/evaluation.py --model-path ml_model/best_model.pth

Requires:
    - Trained model at MODEL_PATH (run train.py first)
    - Oxford 102 Flowers test set (downloaded automatically)

Output:
    ml_model/evaluation_report.json
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime

import numpy as np
import torch
from torch.utils.data import DataLoader
import torchvision.datasets as datasets
import torchvision.transforms as T
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    top_k_accuracy_score,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_model.config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    MODEL_PATH,
    EVALUATION_REPORT_PATH,
    DATA_DIR,
    OXFORD_FLOWER_LABELS,
)
from ml_model.model import load_model, ModelNotAvailableError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

VAL_TRANSFORM = T.Compose([
    T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


def evaluate(model_path: str, data_root: str) -> dict:
    """
    Evaluate the model on the Oxford 102 Flowers test split.
    Returns the evaluation report as a dict.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ── Load model ─────────────────────────────────────────────────────────────
    try:
        model = load_model(model_path)
    except ModelNotAvailableError as exc:
        logger.error(str(exc))
        report = {
            "error": "Model not trained yet",
            "message": str(exc),
            "available": False,
            "evaluated_at": datetime.utcnow().isoformat(),
        }
        with open(EVALUATION_REPORT_PATH, "w") as f:
            json.dump(report, f, indent=2)
        return report

    # ── Load test dataset ───────────────────────────────────────────────────────
    flowers_dir = os.path.join(data_root, "flowers102")
    logger.info("Loading test split from '%s' ...", flowers_dir)
    test_ds = datasets.Flowers102(
        root=flowers_dir, split="test", transform=VAL_TRANSFORM, download=True
    )
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False, num_workers=4)
    logger.info("Test samples: %d", len(test_ds))

    # ── Collect predictions ─────────────────────────────────────────────────────
    all_labels: list[int] = []
    all_preds:  list[int] = []
    all_probs:  list[np.ndarray] = []

    model.eval()
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()
            preds = probs.argmax(axis=1)
            all_probs.append(probs)
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.numpy().tolist())

    all_probs_arr = np.vstack(all_probs)

    # ── Metrics ─────────────────────────────────────────────────────────────────
    accuracy    = float(accuracy_score(all_labels, all_preds))
    top5_acc    = float(top_k_accuracy_score(all_labels, all_probs_arr, k=5))

    cr = classification_report(
        all_labels, all_preds,
        target_names=OXFORD_FLOWER_LABELS,
        output_dict=True,
        zero_division=0,
    )

    precision_macro = float(cr["macro avg"]["precision"])
    recall_macro    = float(cr["macro avg"]["recall"])
    f1_macro        = float(cr["macro avg"]["f1-score"])

    # ── Confusion matrix (top-20 classes by frequency) ─────────────────────────
    cm = confusion_matrix(all_labels, all_preds)
    # Pick top 20 most frequent true classes
    class_counts = np.bincount(all_labels, minlength=102)
    top20_idxs   = class_counts.argsort()[-20:][::-1].tolist()
    cm_top20     = cm[np.ix_(top20_idxs, top20_idxs)].tolist()
    top20_labels = [OXFORD_FLOWER_LABELS[i] for i in top20_idxs]

    # ── Build report ────────────────────────────────────────────────────────────
    report = {
        "available": True,
        "evaluated_at": datetime.utcnow().isoformat(),
        "num_test_samples": len(all_labels),
        "accuracy": round(accuracy, 4),
        "top5_accuracy": round(top5_acc, 4),
        "precision_macro": round(precision_macro, 4),
        "recall_macro": round(recall_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "per_class_report": {
            k: {
                "precision": round(v["precision"], 3),
                "recall":    round(v["recall"], 3),
                "f1_score":  round(v["f1-score"], 3),
                "support":   int(v["support"]),
            }
            for k, v in cr.items()
            if k not in ("accuracy", "macro avg", "weighted avg")
        },
        "confusion_matrix_top20": {
            "labels": top20_labels,
            "matrix": cm_top20,
        },
    }

    with open(EVALUATION_REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("=" * 50)
    logger.info("Evaluation Results")
    logger.info("  Accuracy:         %.2f%%", accuracy * 100)
    logger.info("  Top-5 Accuracy:   %.2f%%", top5_acc * 100)
    logger.info("  Precision (macro):%.2f%%", precision_macro * 100)
    logger.info("  Recall (macro):   %.2f%%", recall_macro * 100)
    logger.info("  F1 (macro):       %.2f%%", f1_macro * 100)
    logger.info("Report saved to: %s", EVALUATION_REPORT_PATH)
    logger.info("=" * 50)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate FloraCare AI model")
    parser.add_argument("--model-path", type=str, default=MODEL_PATH)
    parser.add_argument("--data-dir",   type=str, default=DATA_DIR)
    args = parser.parse_args()
    evaluate(args.model_path, args.data_dir)


if __name__ == "__main__":
    main()
