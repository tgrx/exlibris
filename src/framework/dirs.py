import os
from pathlib import Path

_this_file = Path(__file__).resolve()

DIR_REPO = _this_file.parent.parent.parent.resolve()

DIR_CONFIG = (DIR_REPO / "config").resolve()
assert DIR_CONFIG.is_dir()

DIR_CONFIG_SECRETS = Path(os.getenv("SECRETS_DIR", DIR_CONFIG / ".secrets"))
DIR_CONFIG_SECRETS.mkdir(exist_ok=True)
assert DIR_CONFIG_SECRETS.is_dir()

DIR_IDEA = (DIR_REPO / ".idea").resolve()

DIR_SRC = (DIR_REPO / "src").resolve()
assert DIR_SRC.is_dir()

DIR_FRAMEWORK = (DIR_SRC / "framework").resolve()
assert DIR_FRAMEWORK.is_dir()

DIR_STATIC = (DIR_SRC / "static").resolve()
assert DIR_STATIC.is_dir()

DIR_SCRIPTS = (DIR_REPO / "scripts").resolve()
assert DIR_SCRIPTS.is_dir()
