from flask import Blueprint, current_app, jsonify

from backend.services.debug_payload_service import DebugPayloadService
from backend.services.run_record_service import RunRecordService


runs_blueprint = Blueprint("runs", __name__, url_prefix="/api")


def _run_record_service():
    return RunRecordService(current_app.config["SQLITE_PATH"])


@runs_blueprint.get("/runs/<run_id>")
def get_run(run_id):
    payload = DebugPayloadService(_run_record_service()).build_payload(run_id)
    if not payload:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(payload)


@runs_blueprint.get("/runs/<run_id>/safety-issues")
def get_run_safety_issues(run_id):
    record = _run_record_service().get_run_record(run_id)
    if not record:
        return jsonify({"error": "Run not found"}), 404
    return jsonify({"items": _run_record_service().list_safety_issues(run_id)})


@runs_blueprint.get("/chat/<session_id>/runs")
@runs_blueprint.get("/chat/sessions/<session_id>/runs")
def list_session_runs(session_id):
    return jsonify({"items": _run_record_service().list_runs_for_session(session_id)})
