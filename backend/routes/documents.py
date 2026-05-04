from flask import Blueprint, current_app, jsonify, request

from backend.services.document_service import DocumentService
from backend.services.ingestion_service import IngestionService
from backend.services.indexing_service import IndexingService

documents_blueprint = Blueprint("documents", __name__, url_prefix="/api/documents")


def _document_service():
    return DocumentService(current_app.config["SQLITE_PATH"])


def _ingestion_service():
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


@documents_blueprint.get("")
def list_documents():
    collection_id = request.args.get("collection_id")
    search = request.args.get("search")
    status = request.args.get("status")
    return jsonify(
        {"items": _document_service().list_documents(collection_id=collection_id, search=search, status=status)}
    )


@documents_blueprint.get("/<document_id>")
def get_document(document_id):
    document = _document_service().get_document(document_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(document)


@documents_blueprint.post("")
def create_document():
    payload = request.get_json(silent=True) or {}
    source_type = (payload.get("source_type") or "").strip()
    if not source_type:
        return jsonify({"error": "source_type is required"}), 400
    document = _document_service().create_document(
        source_type=source_type,
        collection_id=payload.get("collection_id"),
        source_url=payload.get("source_url"),
        source_identity=payload.get("source_identity"),
        source_filename=payload.get("source_filename"),
        title=payload.get("title"),
        raw_text=payload.get("raw_text"),
        ingestion_status=payload.get("ingestion_status", "pending"),
        duplicate_status=payload.get("duplicate_status"),
        file_hash=payload.get("file_hash"),
        text_hash=payload.get("text_hash"),
        freshness_metadata=payload.get("freshness_metadata"),
    )
    return jsonify(document), 201


@documents_blueprint.patch("/<document_id>/collection")
def move_document_to_collection(document_id):
    payload = request.get_json(silent=True) or {}
    collection_id = payload.get("collection_id")
    document = _document_service().get_document(document_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404

    old_chunks = _document_service().get_chunks_for_document(document_id)
    updated = _document_service().move_document_to_collection(document_id, collection_id)
    if old_chunks:
        IndexingService(
            current_app.extensions["chroma_client"],
            collection_prefix=current_app.config["CHROMA_COLLECTION_PREFIX"],
            embedding_model=current_app.config["DEFAULT_EMBEDDING_MODEL"],
            dimensions=current_app.config["EMBEDDING_DIMENSIONS"],
        ).move_document(document, old_chunks, collection_id)
        for chunk in old_chunks:
            _document_service().upsert_chunk_metadata(
                {
                    **chunk,
                    "collection_id": collection_id,
                }
            )
    return jsonify(updated)


@documents_blueprint.post("/<document_id>/re-index")
@documents_blueprint.patch("/<document_id>/re-index")
def reindex_document(document_id):
    document, error = _ingestion_service().reindex_document(document_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(document)


@documents_blueprint.delete("/<document_id>")
def delete_document(document_id):
    deleted, error = _ingestion_service().delete_document(document_id)
    if not deleted:
        return jsonify({"error": error}), 404
    return jsonify({"deleted": True, "document_id": document_id})
