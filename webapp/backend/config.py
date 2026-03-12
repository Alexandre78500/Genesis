from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_TSV = PROJECT_ROOT / "results.tsv"
HISTORY_TSV = PROJECT_ROOT / "history.tsv"
GAMIFICATION_DIR = PROJECT_ROOT / "gamification"
STATE_JSON = GAMIFICATION_DIR / "state.json"
CONFIG_JSON = GAMIFICATION_DIR / "config.json"
RUN_LOG = PROJECT_ROOT / "run.log"
GIT_DIR = PROJECT_ROOT / ".git"

SSE_RETRY_MS = 3000
POLL_INTERVAL_S = 2.0
HEARTBEAT_INTERVAL_S = 15.0
