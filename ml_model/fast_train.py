"""
FloraCare AI – Optimized High-Performance MobileNetV2 Fine-Tuning
Trained on Oxford 102 Flowers dataset using feature caching + top-layer fine-tuning.
Saves:
  - ml_model/best_model.pth
  - ml_model/training_log.json
  - ml_model/evaluation_report.json
"""
import os
import sys
import time
import json
import logging
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import torchvision.datasets as datasets
import torchvision.transforms as T
import torchvision.models as models
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_model.config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    NUM_CLASSES,
    DROPOUT_RATE,
    MODEL_PATH,
    TRAINING_LOG_PATH,
    EVALUATION_REPORT_PATH,
    DATA_DIR,
    OXFORD_FLOWER_LABELS,
)
from ml_model.model import build_model, unfreeze_top_layers
from ml_model.predict import clear_model_cache

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fast_train")

VAL_TRANSFORM = T.Compose([
    T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

TRAIN_TRANSFORM = T.Compose([
    T.RandomResizedCrop(IMAGE_SIZE, scale=(0.8, 1.0)),
    T.RandomHorizontalFlip(),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


def extract_features(feature_extractor: nn.Module, loader: DataLoader, device: torch.device):
    """Pass images through frozen backbone to extract 1280-dim feature vectors."""
    features_list = []
    labels_list = []
    feature_extractor.eval()
    with torch.no_grad():
        for images, targets in loader:
            images = images.to(device)
            feats = feature_extractor(images)  # (B, 1280, 1, 1)
            feats = torch.flatten(feats, 1)     # (B, 1280)
            features_list.append(feats.cpu())
            labels_list.append(targets)
    all_feats = torch.cat(features_list, dim=0)
    all_labels = torch.cat(labels_list, dim=0)
    return all_feats, all_labels


def run_training(data_root: str = DATA_DIR, epochs: int = 30):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"🌿 Starting FloraCare AI Training on device: {device}")

    flowers_dir = os.path.join(data_root, "flowers102")
    os.makedirs(flowers_dir, exist_ok=True)

    logger.info(f"Loading Oxford 102 Flowers dataset from '{flowers_dir}' ...")
    train_ds = datasets.Flowers102(root=flowers_dir, split="train", transform=VAL_TRANSFORM, download=True)
    val_ds   = datasets.Flowers102(root=flowers_dir, split="val",   transform=VAL_TRANSFORM, download=True)

    logger.info(f"Train samples: {len(train_ds)} | Val samples: {len(val_ds)}")

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=False, num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=64, shuffle=False, num_workers=0)

    # 1. Build Base Model
    base_model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    feature_backbone = nn.Sequential(base_model.features, nn.AdaptiveAvgPool2d((1, 1))).to(device)

    # 2. Extract features
    logger.info("Extracting feature representations from MobileNetV2 backbone...")
    t0 = time.time()
    train_feats, train_labels = extract_features(feature_backbone, train_loader, device)
    val_feats,   val_labels   = extract_features(feature_backbone, val_loader,   device)
    logger.info(f"Features extracted in {time.time() - t0:.1f}s. Train shape: {train_feats.shape}, Val shape: {val_feats.shape}")

    feat_train_ds = TensorDataset(train_feats, train_labels)
    feat_train_loader = DataLoader(feat_train_ds, batch_size=32, shuffle=True)

    # 3. Train Classifier Head
    classifier = nn.Sequential(
        nn.Dropout(p=DROPOUT_RATE),
        nn.Linear(1280, NUM_CLASSES),
    ).to(device)

    optimizer = optim.AdamW(classifier.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)

    training_log = []
    best_acc = 0.0
    best_classifier_weights = None

    logger.info("Training custom Oxford 102 classification head...")
    for epoch in range(1, epochs + 1):
        classifier.train()
        total_loss, correct, total = 0.0, 0, 0
        ep_start = time.time()

        for x_batch, y_batch in feat_train_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            out = classifier(x_batch)
            loss = criterion(out, y_batch)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * x_batch.size(0)
            _, preds = out.max(1)
            correct += preds.eq(y_batch).sum().item()
            total += x_batch.size(0)

        train_loss = total_loss / total
        train_acc  = correct / total
        scheduler.step()

        # Validate
        classifier.eval()
        with torch.no_grad():
            val_out = classifier(val_feats.to(device))
            v_loss = criterion(val_out, val_labels.to(device)).item()
            _, v_preds = val_out.max(1)
            val_acc = (v_preds.cpu() == val_labels).float().mean().item()

        elapsed = time.time() - ep_start
        logger.info(
            f"Epoch {epoch:2d}/{epochs} | Train Loss: {train_loss:.4f} Acc: {train_acc*100:.1f}% | "
            f"Val Loss: {v_loss:.4f} Acc: {val_acc*100:.1f}% | {elapsed:.2f}s"
        )

        entry = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(v_loss, 4),
            "val_acc": round(val_acc, 4),
            "elapsed_s": round(elapsed, 2)
        }
        training_log.append(entry)

        if val_acc > best_acc:
            best_acc = val_acc
            best_classifier_weights = classifier.state_dict()

    # 4. Assemble complete MobileNetV2 model
    full_model = build_model(NUM_CLASSES)
    if best_classifier_weights:
        full_model.classifier.load_state_dict(best_classifier_weights)
    full_model.to(device)

    # 5. Fine-tune top 2 convolutional blocks
    logger.info("Fine-tuning top convolutional feature blocks...")
    full_model = unfreeze_top_layers(full_model, num_blocks=2)
    ft_optimizer = optim.AdamW(filter(lambda p: p.requires_grad, full_model.parameters()), lr=1e-4, weight_decay=1e-4)

    ft_train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=0)
    for ft_epoch in range(1, 4):
        full_model.train()
        ft_loss, ft_corr, ft_tot = 0.0, 0, 0
        ft_start = time.time()
        for imgs, lbls in ft_train_loader:
            imgs, lbls = imgs.to(device), lbls.to(device)
            ft_optimizer.zero_grad()
            out = full_model(imgs)
            loss = criterion(out, lbls)
            loss.backward()
            ft_optimizer.step()
            ft_loss += loss.item() * imgs.size(0)
            _, p = out.max(1)
            ft_corr += p.eq(lbls).sum().item()
            ft_tot += imgs.size(0)

        # Validate
        full_model.eval()
        with torch.no_grad():
            val_corr = 0
            for v_imgs, v_lbls in val_loader:
                v_imgs, v_lbls = v_imgs.to(device), v_lbls.to(device)
                v_out = full_model(v_imgs)
                _, vp = v_out.max(1)
                val_corr += vp.eq(v_lbls).sum().item()
            ft_val_acc = val_corr / len(val_ds)

        ft_elapsed = time.time() - ft_start
        logger.info(f"Fine-Tune Epoch {ft_epoch}/3 | Loss: {ft_loss/ft_tot:.4f} Acc: {ft_corr/ft_tot*100:.1f}% | Val Acc: {ft_val_acc*100:.1f}% | {ft_elapsed:.1f}s")
        if ft_val_acc > best_acc:
            best_acc = ft_val_acc

    # 6. Save model checkpoint
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    torch.save(full_model.state_dict(), MODEL_PATH)
    logger.info(f"✅ Saved trained model to {MODEL_PATH} (val_acc={best_acc*100:.2f}%)")

    # 7. Save training log
    with open(TRAINING_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "model_architecture": "MobileNetV2",
            "dataset": "Oxford 102 Flowers",
            "epochs": training_log,
            "best_val_accuracy": round(best_acc, 4),
            "completed_at": datetime.utcnow().isoformat()
        }, f, indent=2)

    # 8. Compute Full Evaluation Metrics on Validation set
    logger.info("Computing full evaluation metrics (Accuracy, Precision, Recall, F1)...")
    full_model.eval()
    all_preds = []
    all_targets = []
    all_probs = []

    with torch.no_grad():
        for imgs, lbls in val_loader:
            imgs = imgs.to(device)
            out = full_model(imgs)
            probs = torch.softmax(out, dim=1)
            _, p = out.max(1)
            all_preds.extend(p.cpu().tolist())
            all_targets.extend(lbls.tolist())
            all_probs.extend(probs.cpu().tolist())

    top1_acc = accuracy_score(all_targets, all_preds)
    # top-5 accuracy
    top5_correct = 0
    for prob_row, true_label in zip(all_probs, all_targets):
        top5_idx = np.argsort(prob_row)[-5:]
        if true_label in top5_idx:
            top5_correct += 1
    top5_acc = top5_correct / len(all_targets)

    prec, rec, f1, _ = precision_recall_fscore_support(all_targets, all_preds, average="weighted", zero_division=0)
    macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(all_targets, all_preds, average="macro", zero_division=0)

    # Per-class summary
    cls_report = classification_report(all_targets, all_preds, output_dict=True, zero_division=0)

    eval_report = {
        "available": True,
        "evaluated_at": datetime.utcnow().isoformat(),
        "model_architecture": "MobileNetV2 (Oxford 102 Flowers)",
        "dataset": "Oxford 102 Flowers (Validation Set)",
        "total_test_samples": len(all_targets),
        "num_classes": NUM_CLASSES,
        "top1_accuracy": round(float(top1_acc), 4),
        "top5_accuracy": round(float(top5_acc), 4),
        "weighted_precision": round(float(prec), 4),
        "weighted_recall": round(float(rec), 4),
        "weighted_f1_score": round(float(f1), 4),
        "macro_precision": round(float(macro_prec), 4),
        "macro_recall": round(float(macro_rec), 4),
        "macro_f1_score": round(float(macro_f1), 4),
        "top_performing_classes": [
            {
                "class_id": int(k) + 1,
                "label": OXFORD_FLOWER_LABELS[int(k)] if int(k) < len(OXFORD_FLOWER_LABELS) else f"class_{k}",
                "f1_score": round(v.get("f1-score", 0), 3),
                "support": v.get("support", 0)
            }
            for k, v in cls_report.items()
            if k.isdigit() and v.get("f1-score", 0) >= 0.70
        ][:15],
        "message": f"Real model evaluation complete: Top-1 Accuracy {top1_acc*100:.1f}%, Top-5 Accuracy {top5_acc*100:.1f}%, Weighted F1 {f1*100:.1f}%."
    }

    with open(EVALUATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)

    logger.info(f"📊 Evaluation Report Saved! Top-1 Acc: {top1_acc*100:.1f}%, Top-5 Acc: {top5_acc*100:.1f}%, F1: {f1*100:.1f}%")

    # Clear model cache in predict module so reload occurs
    clear_model_cache()
    logger.info("🎉 All training and evaluation steps successfully completed!")
    return eval_report


if __name__ == "__main__":
    run_training()
