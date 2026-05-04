from flask import Blueprint, current_app, jsonify, request

from backend.services.collection_service import CollectionService

collections_blueprint = Blueprint("collections", __name__, url_prefix="/api/collections")


def _service():
    return CollectionService(current_app.config["SQLITE_PATH"])


@collections_blueprint.get("")
def list_collections():
    return jsonify({"items": _service().list_collections()})


@collections_blueprint.post("")
def create_collection():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Collection name is required"}), 400
    collection = _service().create_collection(
        name=name,
        description=payload.get("description"),
        routing_description=payload.get("routing_description"),
    )
    return jsonify(collection), 201


@collections_blueprint.get("/<collection_id>")
def get_collection(collection_id):
    collection = _service().get_collection(collection_id)
    if not collection:
        return jsonify({"error": "Collection not found"}), 404
    return jsonify(collection)


@collections_blueprint.put("/<collection_id>")
def update_collection(collection_id):
    payload = request.get_json(silent=True) or {}
    collection = _service().update_collection(
        collection_id,
        name=payload.get("name"),
        description=payload.get("description"),
        routing_description=payload.get("routing_description"),
    )
    if not collection:
        return jsonify({"error": "Collection not found"}), 404
    return jsonify(collection)


@collections_blueprint.patch("/<collection_id>/default")
def set_default_collection(collection_id):
    collection = _service().set_default_collection(collection_id)
    if not collection:
        return jsonify({"error": "Collection not found"}), 404
    return jsonify(collection)


@collections_blueprint.delete("/<collection_id>")
def delete_collection(collection_id):
    deleted, error = _service().delete_collection(collection_id)
    if not deleted:
        return jsonify({"error": error}), 400
    return jsonify({"deleted": True, "collection_id": collection_id})
