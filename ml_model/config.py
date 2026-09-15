"""
FloraCare AI – ML Model Configuration
Oxford 102 Flowers dataset configuration and model hyperparameters.
"""
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.pth")
TRAINING_LOG_PATH = os.path.join(BASE_DIR, "training_log.json")
EVALUATION_REPORT_PATH = os.path.join(BASE_DIR, "evaluation_report.json")
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

# ── Image Preprocessing ────────────────────────────────────────────────────────
IMAGE_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

# ── Model ──────────────────────────────────────────────────────────────────────
NUM_CLASSES = 102
DROPOUT_RATE = 0.2

# ── Training ───────────────────────────────────────────────────────────────────
BATCH_SIZE     = 32
LEARNING_RATE  = 1e-3
FINETUNE_LR    = 1e-4   # lower LR for phase-2 fine-tuning
NUM_EPOCHS     = 30
PHASE1_EPOCHS  = 10     # classifier-only training
PATIENCE       = 5      # early-stopping patience

# ── Prediction ─────────────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.25   # below this → low-confidence warning

# ── Oxford 102 Flowers – complete class labels (torchvision Flowers102 order) ──
# torchvision uses 0-indexed labels 0-101 corresponding to Oxford class IDs 1-102
OXFORD_FLOWER_LABELS = [
    "pink primrose",              # 0  (Oxford class 1)
    "hard-leaved pocket orchid",  # 1
    "canterbury bells",           # 2
    "sweet pea",                  # 3
    "english marigold",           # 4
    "tiger lily",                 # 5
    "moon orchid",                # 6
    "bird of paradise",           # 7
    "monkshood",                  # 8
    "globe thistle",              # 9
    "snapdragon",                 # 10
    "colt's foot",                # 11
    "king protea",                # 12
    "spear thistle",              # 13
    "yellow iris",                # 14
    "globe-flower",               # 15
    "purple coneflower",          # 16
    "peruvian lily",              # 17
    "balloon flower",             # 18
    "giant white arum lily",      # 19
    "fire lily",                  # 20
    "pincushion flower",          # 21
    "fritillary",                 # 22
    "red ginger",                 # 23
    "grape hyacinth",             # 24
    "corn poppy",                 # 25
    "prince of wales feathers",   # 26
    "stemless gentian",           # 27
    "artichoke",                  # 28
    "sweet william",              # 29
    "sunflower",                  # 30
    "pelargonium",                # 31
    "garden phlox",               # 32
    "love in the mist",           # 33
    "mexican aster",              # 34
    "alpine sea holly",           # 35
    "ruby-lipped cattleya",       # 36
    "cape flower",                # 37
    "great masterwort",           # 38
    "siam tulip",                 # 39
    "lenten rose",                # 40
    "barbeton daisy",             # 41
    "daffodil",                   # 42
    "sword lily",                 # 43
    "poinsettia",                 # 44
    "bolero deep blue",           # 45
    "wallflower",                 # 46
    "marigold",                   # 47
    "buttercup",                  # 48
    "oxeye daisy",                # 49
    "common dandelion",           # 50
    "petunia",                    # 51
    "wild pansy",                 # 52
    "primula",                    # 53
    "sunflower",                  # 54
    "pelargonium",                # 55  (note: duplicates in Oxford dataset)
    "bishop of llandaff",         # 56
    "gaura",                      # 57
    "geranium",                   # 58
    "orange dahlia",              # 59
    "pink-yellow dahlia",         # 60
    "cautleya spicata",           # 61
    "japanese anemone",           # 62
    "black-eyed susan",           # 63
    "silverbush",                 # 64
    "californian poppy",          # 65
    "osteospermum",               # 66
    "spring crocus",              # 67
    "bearded iris",               # 68
    "windflower",                 # 69
    "tree poppy",                 # 70
    "gazania",                    # 71
    "azalea",                     # 72
    "water lily",                 # 73
    "rose",                       # 74
    "thorn apple",                # 75
    "morning glory",              # 76
    "passion flower",             # 77
    "lotus",                      # 78
    "toad lily",                  # 79
    "anthurium",                  # 80
    "frangipani",                 # 81
    "clematis",                   # 82
    "hibiscus",                   # 83
    "columbine",                  # 84
    "desert-rose",                # 85
    "tree mallow",                # 86
    "magnolia",                   # 87
    "cyclamen",                   # 88
    "watercress",                 # 89
    "canna lily",                 # 90
    "hippeastrum",                # 91
    "bee balm",                   # 92
    "ball moss",                  # 93
    "foxglove",                   # 94
    "bougainvillea",              # 95
    "camellia",                   # 96
    "mallow",                     # 97
    "mexican petunia",            # 98
    "bromelia",                   # 99
    "blanket flower",             # 100
    "trumpet creeper",            # 101  (Oxford class 102)
]

# ── Display names (title-cased) ─────────────────────────────────────────────────
FLOWER_DISPLAY_NAMES = {i: label.title() for i, label in enumerate(OXFORD_FLOWER_LABELS)}

# ── Flower emojis (best-effort mapping) ─────────────────────────────────────────
FLOWER_EMOJI = {
    "pink primrose": "🌸", "hard-leaved pocket orchid": "🌺", "canterbury bells": "🔔",
    "sweet pea": "🌷", "english marigold": "🌼", "tiger lily": "🌺",
    "moon orchid": "🌸", "bird of paradise": "🌴", "monkshood": "💜",
    "globe thistle": "🌐", "snapdragon": "🌻", "colt's foot": "🌿",
    "king protea": "👑", "spear thistle": "🌿", "yellow iris": "🌼",
    "globe-flower": "🌕", "purple coneflower": "🌸", "peruvian lily": "🌺",
    "balloon flower": "🎈", "giant white arum lily": "🤍", "fire lily": "🔥",
    "pincushion flower": "💙", "fritillary": "🦋", "red ginger": "🫚",
    "grape hyacinth": "🍇", "corn poppy": "🌹", "prince of wales feathers": "🪶",
    "stemless gentian": "💙", "artichoke": "🌿", "sweet william": "🌸",
    "sunflower": "🌻", "pelargonium": "🌸", "garden phlox": "🌸",
    "love in the mist": "💙", "mexican aster": "🌺", "alpine sea holly": "🔵",
    "rose": "🌹", "hibiscus": "🌺", "lotus": "🪷", "daffodil": "🌼",
    "daisy": "🌼", "marigold": "🌼", "camellia": "🌸", "magnolia": "🤍",
    "foxglove": "🔔", "petunia": "💜", "azalea": "🌸", "water lily": "🪷",
    "clematis": "💜", "bougainvillea": "🌺", "cyclamen": "🌸",
    "passion flower": "🌸", "morning glory": "💙", "frangipani": "🌸",
    "blanket flower": "🌻", "trumpet creeper": "🎺",
}

def get_flower_emoji(label: str) -> str:
    """Return the best emoji for a flower label."""
    return FLOWER_EMOJI.get(label.lower(), "🌸")

def get_display_name(idx: int) -> str:
    """Return title-cased display name for a class index."""
    if 0 <= idx < NUM_CLASSES:
        return OXFORD_FLOWER_LABELS[idx].title()
    return "Unknown"

def label_to_db_id(label: str) -> int:
    """Convert Oxford label string to 1-based Oxford class ID."""
    try:
        idx = OXFORD_FLOWER_LABELS.index(label.lower())
        return idx + 1
    except ValueError:
        return -1
