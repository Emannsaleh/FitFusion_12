import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
IMAGES_DIR = PROJECT_ROOT / "images"
KAGGLE_NOTEBOOK_DIR = PROJECT_ROOT / "kaggle_notebook"


def load_dotenv() -> None:
    if not ENV_PATH.exists():
        return

    with open(ENV_PATH, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def ensure_runtime_dirs() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_kaggle_cli() -> str:
    candidates = [
        PROJECT_ROOT / "venv" / "Scripts" / "kaggle.exe",
        PROJECT_ROOT / "venv" / "bin" / "kaggle",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    cli = shutil.which("kaggle")
    if cli:
        return cli

    raise FileNotFoundError(
        "Kaggle CLI not found. Install it in the project venv: pip install kaggle"
    )


def apply_kaggle_env() -> None:
    load_dotenv()
    username = os.getenv("KAGGLE_USERNAME")
    api_key = os.getenv("KAGGLE_KEY")

    if not username or not api_key:
        raise RuntimeError(
            "Kaggle credentials missing. Set KAGGLE_USERNAME and KAGGLE_KEY in App/.env"
        )

    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = api_key
    os.environ["PYTHONUTF8"] = "1"
