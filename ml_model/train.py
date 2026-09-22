"""
FloraCare AI – Training Script
Fine-tunes MobileNetV2 on the Oxford 102 Flowers dataset.

Usage:
    python ml_model/train.py
    python ml_model/train.py --epochs 30 --batch-size 32 --lr 0.001
    python ml_model/train.py --data-dir /path/to/data

The Oxford 102 Flowers dataset is automatically downloaded via torchvision.
Training takes approximately 30–120 minutes on a GPU or 3–8 hours on CPU.

Output:
    ml_model/best_model.pth      – best checkpoint (by val accuracy)
    ml_model/training_log.json   – per-epoch metrics
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.datasets as datasets
import torchvision.transforms as T
from tqdm import tqdm

# Ensure ml_model package is importable when run as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_model.config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    NUM_CLASSES,
    BATCH_SIZE,
    LEARNING_RATE,
    FINETUNE_LR,
    NUM_EPOCHS,
    PHASE1_EPOCHS,
    PATIENCE,
    MODEL_PATH,
    TRAINING_LOG_PATH,
    DATA_DIR,
)
from ml_model.model import build_model, freeze_base, unfreeze_top_layers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Data transforms ─────────────────────────────────────────────────────────────
TRAIN_TRANSFORM = T.Compose([
    T.RandomResizedCrop(IMAGE_SIZE, scale=(0.7, 1.0)),
    T.RandomHorizontalFlip(),
    T.RandomVerticalFlip(p=0.1),
    T.RandomRotation(30),
    T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

VAL_TRANSFORM = T.Compose([
    T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


def load_datasets(data_root: str) -> tuple[DataLoader, DataLoader]:
    """
    Download and load Oxford Flowers102 train and val splits.
    Dataset is downloaded automatically to data_root/flowers102/.
    """
    flowers_dir = os.path.join(data_root, "flowers102")
    os.makedirs(flowers_dir, exist_ok=True)

    logger.info("Loading Oxford 102 Flowers dataset from '%s' ...", flowers_dir)
    logger.info("(Dataset will be downloaded automatically if not already present)")

    train_ds = datasets.Flowers102(
        root=flowers_dir, split="train", transform=TRAIN_TRANSFORM, download=True
    )
    val_ds = datasets.Flowers102(
        root=flowers_dir, split="val", transform=VAL_TRANSFORM, download=True
    )

    logger.info("Train samples: %d | Val samples: %d", len(train_ds), len(val_ds))

    train_loader = DataLoader(
        train_ds, batch_size=BATCH_SIZE, shuffle=True,
        num_workers=0, pin_memory=False
    )
    val_loader = DataLoader(
        val_ds, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=0, pin_memory=False
    )
    return train_loader, val_loader


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> tuple[float, float]:
    """Return (avg_loss, top1_accuracy) on the given dataloader."""
    model.eval()
    criterion = nn.CrossEntropyLoss()
    total_loss, correct, total = 0.0, 0, 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += images.size(0)

    return total_loss / total, correct / total


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: optim.Optimizer,
    device: torch.device,
    epoch: int,
) -> tuple[float, float]:
    """Train for one epoch. Returns (avg_loss, top1_accuracy)."""
    model.train()
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    total_loss, correct, total = 0.0, 0, 0

    pbar = tqdm(loader, desc=f"Epoch {epoch}", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += images.size(0)
        pbar.set_postfix(loss=f"{loss.item():.4f}")

    return total_loss / total, correct / total


def train(args: argparse.Namespace) -> None:
    """Full training procedure with two-phase fine-tuning."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Training device: %s", device)
    if device.type == "cpu":
        logger.warning(
            "⚠️  No GPU detected. Training on CPU will be slow (estimated 3–8 hours). "
            "Consider using a machine with a CUDA-capable GPU."
        )

    train_loader, val_loader = load_datasets(args.data_dir)

    model = build_model(NUM_CLASSES)
    model = freeze_base(model)   # Phase 1: train classifier only
    model.to(device)

    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr,
        weight_decay=1e-4,
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    log: list[dict] = []
    best_val_acc = 0.0
    patience_counter = 0

    logger.info("=" * 60)
    logger.info("Phase 1: Training classifier head (base frozen)")
    logger.info("=" * 60)

    for epoch in range(1, args.epochs + 1):
        # Switch to phase 2 at PHASE1_EPOCHS
        if epoch == PHASE1_EPOCHS + 1:
            logger.info("=" * 60)
            logger.info("Phase 2: Unfreezing top feature blocks (fine-tuning)")
            logger.info("=" * 60)
            model = unfreeze_top_layers(model, num_blocks=4)
            # Lower learning rate for fine-tuning
            optimizer = optim.Adam(
                filter(lambda p: p.requires_grad, model.parameters()),
                lr=FINETUNE_LR,
                weight_decay=1e-4,
            )
            scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs - PHASE1_EPOCHS)

        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, device, epoch)
        val_loss, val_acc = evaluate(model, val_loader, device)
        scheduler.step()
        elapsed = time.time() - t0

        logger.info(
            "Epoch %3d/%d | Train Loss %.4f Acc %.2f%% | "
            "Val Loss %.4f Acc %.2f%% | %.1fs",
            epoch, args.epochs,
            train_loss, train_acc * 100,
            val_loss, val_acc * 100,
            elapsed,
        )

        entry = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 4),
            "elapsed_s": round(elapsed, 1),
        }
        log.append(entry)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            torch.save(model.state_dict(), MODEL_PATH)
            logger.info("  ✅ Saved best model (val_acc=%.2f%%)", val_acc * 100)
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                logger.info("  ⏹  Early stopping triggered after %d epochs without improvement.", PATIENCE)
                break

        # Save log after every epoch
        with open(TRAINING_LOG_PATH, "w") as f:
            json.dump({"epochs": log, "best_val_acc": round(best_val_acc, 4)}, f, indent=2)

    logger.info("=" * 60)
    logger.info("Training complete! Best validation accuracy: %.2f%%", best_val_acc * 100)
    logger.info("Model saved to: %s", MODEL_PATH)
    logger.info("Training log:   %s", TRAINING_LOG_PATH)
    logger.info("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train FloraCare AI flower identifier")
    parser.add_argument("--epochs",     type=int,   default=NUM_EPOCHS,     help="Number of training epochs")
    parser.add_argument("--batch-size", type=int,   default=BATCH_SIZE,     help="Batch size")
    parser.add_argument("--lr",         type=float, default=LEARNING_RATE,  help="Initial learning rate")
    parser.add_argument("--data-dir",   type=str,   default=DATA_DIR,       help="Directory to download dataset to")
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
