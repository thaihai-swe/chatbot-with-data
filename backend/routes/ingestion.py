from flask import Blueprint, current_app, jsonify, request

from backend.services.ingestion_service import IngestionService

ingestion_blueprint = Blueprint("ingestion", __name__, url_prefix="/api")


def _service():
    return IngestionService(
        sqlite_path=current_app.config["SQLITE_PATH"],
        upload_dir=current_app.config["UPLOAD_DIR"],
        chroma_client=current_app.extensions["chroma_client"],
        collection_prefix=current_app.config["CHROMA_COLLECTION_PREFIX"],
        embedding_model=current_app.config["DEFAULT_EMBEDDING_MODEL"],
        embedding_dimensions=current_app.config["EMBEDDING_DIMENSIONS"],
        chunk_size=current_app.config["DEFAULT_CHUNK_SIZE"],
        chunk_overlap=current_app.config["DEFAULT_CHUNK_OVERLAP"],
        url_timeout_seconds=current_app.config["URL_TIMEOUT_SECONDS"],
    )


@ingestion_blueprint.post("/documents/upload")
def upload_document():
    if "file" not in request.files:
        return jsonify({"errors": ["file is required"]}), 400
    collection_id = request.form.get("collection_id")
    result = _service().ingest_uploaded_file(request.files["file"], collection_id=collection_id)
    status_code = 200 if result.get("status") != "failed" else 400
    return jsonify(result), status_code


@ingestion_blueprint.post("/documents/ingest-url")
def ingest_url():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or "").strip()
    if not url:
        return jsonify({"errors": ["url is required"]}), 400
    try:
        result = _service().ingest_url(url, collection_id=payload.get("collection_id"))
    except Exception as exc:  # pragma: no cover - integration behavior
        return jsonify({"status": "failed", "errors": [str(exc)]}), 400
    return jsonify(result)


@ingestion_blueprint.patch("/documents/<document_id>/duplicate-decision")
def duplicate_decision(document_id):
    payload = request.get_json(silent=True) or {}
    decision = payload.get("decision")
    if not decision:
        return jsonify({"error": "decision is required"}), 400
    document, error = _service().apply_duplicate_decision(document_id, decision)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(document)


@ingestion_blueprint.get("/ingestion-logs")
def list_logs():
    return jsonify({"items": _service().list_logs()})
