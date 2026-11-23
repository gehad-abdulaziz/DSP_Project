"""
Experiment Manager — Tracks experiment history, comparisons, and results.

Stores experiments as JSON files in the experiments/ directory.
"""

import json
import time
import uuid
from pathlib import Path
from datetime import datetime

EXPERIMENTS_DIR = Path(__file__).resolve().parent.parent / "experiments"
EXPERIMENTS_DIR.mkdir(exist_ok=True)


def _experiments_index_path():
    return EXPERIMENTS_DIR / "index.json"


def _load_index():
    path = _experiments_index_path()
    if path.exists():
        return json.loads(path.read_text())
    return []


def _save_index(index):
    _experiments_index_path().write_text(json.dumps(index, indent=2, default=str))


def create_experiment(parts: list, params: dict, label: str = "") -> dict:
    """Create a new experiment record. Returns the experiment dict."""
    exp_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    experiment = {
        "id": exp_id,
        "label": label,
        "created_at": datetime.now().isoformat(),
        "parts": parts,
        "params": params,
        "status": "pending",
        "results": {},
        "metrics": {},
        "duration": 0,
    }

    # Save individual experiment file
    exp_dir = EXPERIMENTS_DIR / exp_id
    exp_dir.mkdir(parents=True, exist_ok=True)
    (exp_dir / "experiment.json").write_text(json.dumps(experiment, indent=2, default=str))

    # Update index
    index = _load_index()
    index.append({
        "id": exp_id,
        "label": label,
        "created_at": experiment["created_at"],
        "parts": parts,
        "status": "pending",
    })
    _save_index(index)

    return experiment


def update_experiment(exp_id: str, updates: dict):
    """Update an experiment record."""
    exp_dir = EXPERIMENTS_DIR / exp_id
    exp_path = exp_dir / "experiment.json"
    if exp_path.exists():
        exp = json.loads(exp_path.read_text())
        exp.update(updates)
        exp_path.write_text(json.dumps(exp, indent=2, default=str))

    # Update index status
    index = _load_index()
    for item in index:
        if item["id"] == exp_id:
            if "status" in updates:
                item["status"] = updates["status"]
            break
    _save_index(index)


def get_experiment(exp_id: str) -> dict:
    """Load an experiment by ID."""
    exp_path = EXPERIMENTS_DIR / exp_id / "experiment.json"
    if exp_path.exists():
        return json.loads(exp_path.read_text())
    return None


def list_experiments() -> list:
    """List all experiments (most recent first)."""
    return list(reversed(_load_index()))


def delete_experiment(exp_id: str):
    """Remove an experiment."""
    import shutil
    exp_dir = EXPERIMENTS_DIR / exp_id
    if exp_dir.exists():
        shutil.rmtree(exp_dir)
    index = _load_index()
    index = [e for e in index if e["id"] != exp_id]
    _save_index(index)
