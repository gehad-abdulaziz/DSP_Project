"""
DSP LAB — Interactive Signal Processing Studio
Flask Backend Application

Serves a single-page application with API endpoints that execute
the real DSP modules and return results, images, and audio.
"""

import sys
import os
import json
import time
import base64
import threading
from pathlib import Path
from datetime import datetime

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request, send_from_directory, send_file, Response
from integration.execution_engine import run_part, run_all, PART_NAMES
from integration.parameter_manager import PART_PARAMETERS, get_defaults, validate_params
from integration.experiment_manager import (
    create_experiment, update_experiment, get_experiment,
    list_experiments, delete_experiment,
)

import config

app = Flask(__name__, static_folder="dashboard/static", static_url_path="/static")

# Global execution lock to prevent conflicting runs
_execution_lock = threading.Lock()
_current_execution = {"running": False, "part": None, "progress": 0, "total": 0, "status": "idle"}


# ─── Static Pages ────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_file(str(PROJECT_ROOT / "dashboard" / "index.html"))


# ─── API: Parameters ─────────────────────────────────────────────────
@app.route("/api/parameters/<int:part_num>")
def api_get_parameters(part_num):
    if part_num not in PART_PARAMETERS:
        return jsonify({"error": "Invalid part number"}), 404
    return jsonify({
        "part": part_num,
        "parameters": PART_PARAMETERS[part_num],
        "defaults": get_defaults(part_num),
    })


@app.route("/api/parameters/all")
def api_get_all_parameters():
    result = {}
    for part_num in range(1, 7):
        result[part_num] = {
            "parameters": PART_PARAMETERS[part_num],
            "defaults": get_defaults(part_num),
        }
    return jsonify(result)


# ─── API: Execution ──────────────────────────────────────────────────
@app.route("/api/run/<int:part_num>", methods=["POST"])
def api_run_part(part_num):
    if part_num not in PART_NAMES:
        return jsonify({"error": "Invalid part number"}), 404

    if not _execution_lock.acquire(blocking=False):
        return jsonify({"error": "Another experiment is running. Wait for it to finish."}), 409

    try:
        _current_execution.update({"running": True, "part": part_num, "progress": 0, "total": 1, "status": "running"})

        data = request.get_json(silent=True) or {}
        params = data.get("params", None)
        run_id = data.get("run_id", None)

        # Validate params
        if params:
            params = _convert_params(part_num, params)
            params = validate_params(part_num, params)

        result = run_part(part_num, params=params, run_id=run_id)

        _current_execution.update({"running": False, "part": None, "progress": 1, "total": 1, "status": "idle"})

        return jsonify(_serialize_result(result))
    except Exception as e:
        _current_execution.update({"running": False, "status": "error"})
        return jsonify({"error": str(e)}), 500
    finally:
        _execution_lock.release()


@app.route("/api/run/all", methods=["POST"])
def api_run_all():
    if not _execution_lock.acquire(blocking=False):
        return jsonify({"error": "Another experiment is running."}), 409

    try:
        data = request.get_json(silent=True) or {}
        params_all = data.get("params", {})
        run_id = data.get("run_id", None)

        # Convert string keys to ints and validate
        params_per_part = {}
        for key, val in params_all.items():
            part_num = int(key)
            converted = _convert_params(part_num, val)
            params_per_part[part_num] = validate_params(part_num, converted)

        results = []
        total = 6
        for i, part_num in enumerate(range(1, 7), 1):
            _current_execution.update({
                "running": True, "part": part_num,
                "progress": i - 1, "total": total, "status": f"Running Part {part_num}"
            })

            p = params_per_part.get(part_num, None)
            result = run_part(part_num, params=p, run_id=run_id)
            results.append(_serialize_result(result))

        _current_execution.update({"running": False, "part": None, "progress": total, "total": total, "status": "idle"})

        return jsonify({"results": results})
    except Exception as e:
        _current_execution.update({"running": False, "status": "error"})
        return jsonify({"error": str(e)}), 500
    finally:
        _execution_lock.release()


@app.route("/api/status")
def api_status():
    return jsonify(_current_execution)


# ─── API: Outputs & Files ────────────────────────────────────────────
@app.route("/api/outputs/<int:part_num>")
def api_list_outputs(part_num):
    out_dir = config.OUT_DIR / f"part{part_num}"
    if not out_dir.exists():
        return jsonify({"files": []})
    files = []
    for f in sorted(out_dir.iterdir()):
        if f.is_file():
            files.append({
                "name": f.name,
                "path": str(f),
                "size": f.stat().st_size,
                "type": _file_type(f.name),
                "url": f"/api/file/{part_num}/{f.name}",
            })
    return jsonify({"files": files})


@app.route("/api/file/<int:part_num>/<filename>")
def api_serve_file(part_num, filename):
    out_dir = config.OUT_DIR / f"part{part_num}"
    filepath = out_dir / filename
    if not filepath.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(str(filepath))


@app.route("/api/data/<filename>")
def api_serve_data_file(filename):
    filepath = config.DATA_DIR / filename
    if not filepath.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(str(filepath))


# ─── API: Experiments ─────────────────────────────────────────────────
@app.route("/api/experiments", methods=["GET"])
def api_list_experiments():
    return jsonify({"experiments": list_experiments()})


@app.route("/api/experiments", methods=["POST"])
def api_create_experiment():
    data = request.get_json()
    parts = data.get("parts", list(range(1, 7)))
    params = data.get("params", {})
    label = data.get("label", "")
    exp = create_experiment(parts, params, label)
    return jsonify(exp)


@app.route("/api/experiments/<exp_id>", methods=["GET"])
def api_get_experiment(exp_id):
    exp = get_experiment(exp_id)
    if not exp:
        return jsonify({"error": "Not found"}), 404
    return jsonify(exp)


@app.route("/api/experiments/<exp_id>", methods=["DELETE"])
def api_delete_experiment(exp_id):
    delete_experiment(exp_id)
    return jsonify({"status": "deleted"})


@app.route("/api/experiments/<exp_id>/run", methods=["POST"])
def api_run_experiment(exp_id):
    exp = get_experiment(exp_id)
    if not exp:
        return jsonify({"error": "Not found"}), 404

    if not _execution_lock.acquire(blocking=False):
        return jsonify({"error": "Another experiment is running."}), 409

    try:
        update_experiment(exp_id, {"status": "running"})
        start = time.time()

        all_results = {}
        all_metrics = {}

        parts = exp.get("parts", list(range(1, 7)))
        params_all = exp.get("params", {})

        for part_num in parts:
            _current_execution.update({
                "running": True, "part": part_num,
                "progress": parts.index(part_num),
                "total": len(parts), "status": f"Running Part {part_num}"
            })

            p = params_all.get(str(part_num), None)
            if p:
                p = _convert_params(part_num, p)
                p = validate_params(part_num, p)

            result = run_part(part_num, params=p, run_id=exp_id)
            all_results[part_num] = _serialize_result(result)
            all_metrics[part_num] = result.metrics

        duration = time.time() - start
        update_experiment(exp_id, {
            "status": "completed",
            "results": all_results,
            "metrics": all_metrics,
            "duration": duration,
        })

        _current_execution.update({"running": False, "status": "idle"})

        return jsonify({"status": "completed", "duration": duration, "results": all_results})
    except Exception as e:
        update_experiment(exp_id, {"status": "failed", "error": str(e)})
        _current_execution.update({"running": False, "status": "error"})
        return jsonify({"error": str(e)}), 500
    finally:
        _execution_lock.release()


# ─── API: Project Info ────────────────────────────────────────────────
@app.route("/api/project-info")
def api_project_info():
    # Check which outputs exist
    parts_status = {}
    for i in range(1, 7):
        out_dir = config.OUT_DIR / f"part{i}"
        has_outputs = out_dir.exists() and any(out_dir.iterdir()) if out_dir.exists() else False
        parts_status[i] = {
            "name": PART_NAMES[i],
            "has_outputs": has_outputs,
            "output_count": len(list(out_dir.glob("*"))) if out_dir.exists() else 0,
        }

    return jsonify({
        "project_name": "DSP LAB — Interactive Signal Processing Studio",
        "total_parts": 6,
        "parts": parts_status,
        "data_files": {
            "audio": config.AUDIO_PATH.exists(),
            "image": config.IMAGE_PATH.exists(),
        },
    })


# ─── Helpers ──────────────────────────────────────────────────────────
def _convert_params(part_num, params):
    """Convert JSON parameter values to the correct Python types."""
    schema = PART_PARAMETERS.get(part_num, {})
    converted = {}
    for key, val in params.items():
        if key in schema:
            ptype = schema[key]["type"]
            if ptype == "int":
                converted[key] = int(val)
            elif ptype == "float":
                converted[key] = float(val)
            elif ptype == "tuple_int":
                if isinstance(val, str):
                    converted[key] = tuple(int(v.strip()) for v in val.split(","))
                elif isinstance(val, list):
                    converted[key] = tuple(int(v) for v in val)
                else:
                    converted[key] = val
            elif ptype == "tuple_float":
                if isinstance(val, str):
                    converted[key] = tuple(float(v.strip()) for v in val.split(","))
                elif isinstance(val, list):
                    converted[key] = tuple(float(v) for v in val)
                else:
                    converted[key] = val
            else:
                converted[key] = val
        else:
            converted[key] = val
    return converted


def _serialize_result(result):
    """Convert a PartResult to a JSON-serializable dict."""
    return {
        "part_num": result.part_num,
        "name": result.name,
        "status": result.status,
        "duration": round(result.duration, 3),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "error": result.error,
        "outputs": result.outputs,
        "metrics": result.metrics,
        "params_used": _serialize_params(result.params_used),
    }


def _serialize_params(params):
    """Make params JSON-safe (tuples -> lists)."""
    out = {}
    for k, v in params.items():
        if isinstance(v, tuple):
            out[k] = list(v)
        else:
            out[k] = v
    return out


def _file_type(filename):
    ext = filename.lower().split(".")[-1]
    if ext in ("png", "jpg", "jpeg", "bmp", "gif"):
        return "image"
    elif ext in ("wav", "mp3", "ogg"):
        return "audio"
    elif ext in ("json", "txt", "csv"):
        return "text"
    else:
        return "other"


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  DSP LAB — Interactive Signal Processing Studio")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
