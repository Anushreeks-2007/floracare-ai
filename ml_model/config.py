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
    "pink primrose",
    "hard-leaved pocket orchid",
    "canterbury bells",
    "sweet pea",
    "english marigold",
    "tiger lily",
    "moon orchid",
    "bird of paradise",
    "monkshood",
    "globe thistle",
    "snapdragon",
    "colt's foot",
    "king protea",
    "spear thistle",
    "yellow iris",
    "globe-flower",
    "purple coneflower",
    "peruvian lily",
    "balloon flower",
    "giant white arum lily",
    "fire lily",
    "pincushion flower",
    "fritillary",
    "red ginger",
    "grape hyacinth",
    "corn poppy",
    "prince of wales feathers",
    "stemless gentian",
    "artichoke",
    "sweet william",
    "carnation",
    "garden phlox",
    "love in the mist",
    "mexican aster",
    "alpine sea holly",
    "ruby-lipped cattleya",
    "cape flower",
    "great masterwort",
    "siam tulip",
    "lenten rose",
    "barbeton daisy",
    "daffodil",
    "sword lily",
    "poinsettia",
    "bolero deep blue",
    "wallflower",
    "marigold",
    "buttercup",
    "oxeye daisy",
    "common dandelion",
    "petunia",
    "wild pansy",
    "primula",
    "sunflower",
    "pelargonium",
    "bishop of llandaff",
    "gaura",
    "geranium",
    "orange dahlia",
    "pink-yellow dahlia?",
    "cautleya spicata",
    "japanese anemone",
    "black-eyed susan",
    "silverbush",
    "californian poppy",
    "osteospermum",
    "spring crocus",
    "bearded iris",
    "windflower",
    "tree poppy",
    "gazania",
    "azalea",
    "water lily",
    "rose",
    "thorn apple",
    "morning glory",
    "passion flower",
    "lotus",
    "toad lily",
    "anthurium",
    "frangipani",
    "clematis",
    "hibiscus",
    "columbine",
    "desert-rose",
    "tree mallow",
    "magnolia",
    "cyclamen",
    "watercress",
    "canna lily",
    "hippeastrum",
    "bee balm",
    "ball moss",
    "foxglove",
    "bougainvillea",
    "camellia",
    "mallow",
    "mexican petunia",
    "bromelia",
    "blanket flower",
    "trumpet creeper",
    "blackberry lily",
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
