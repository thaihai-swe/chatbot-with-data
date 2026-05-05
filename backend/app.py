from pathlib import Path
from flask import Flask, abort, jsonify, send_from_directory
from flask_cors import CORS #
from backend.config import build_config
from backend.persistence.chroma import init_chroma_client
from backend.persistence.schema import init_schema
from backend.routes.collections import collections_blueprint
from backend.routes.chat import chat_blueprint
from backend.routes.documents import documents_blueprint
from backend.routes.ingestion import ingestion_blueprint
from backend.routes.runs import runs_blueprint

def create_app(overrides=None):
    app = Flask(__name__)

    # Initialize CORS here to cover all routes and blueprints
    CORS(app) #[cite: 1]

    app.config.update(build_config(overrides))
    if app.config.get("TESTING") and (not overrides or "GENERATION_PROVIDER" not in overrides):
        app.config["GENERATION_PROVIDER"] = "local-extractive-v1"
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

    data_dir = Path(app.config["DATA_DIR"])
    sqlite_path = Path(app.config["SQLITE_PATH"])
    chroma_dir = Path(app.config["CHROMA_DIR"])
    upload_dir = Path(app.config["UPLOAD_DIR"])

    data_dir.mkdir(parents=True, exist_ok=True)
    upload_dir.mkdir(parents=True, exist_ok=True)
    init_schema(sqlite_path)

    app.extensions["data_dir"] = data_dir
    app.extensions["sqlite_path"] = sqlite_path
    app.extensions["upload_dir"] = upload_dir
    app.extensions["chroma_client"] = init_chroma_client(chroma_dir)

    app.register_blueprint(collections_blueprint)
    app.register_blueprint(chat_blueprint)
    app.register_blueprint(documents_blueprint)
    app.register_blueprint(ingestion_blueprint)
    app.register_blueprint(runs_blueprint)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    @app.get("/<path:filename>")
    def frontend_asset(filename):
        asset_path = frontend_dir / filename
        if not asset_path.is_file():
            abort(404)
        return send_from_directory(frontend_dir, filename)

    # Removed the manual @app.after_request block as CORS(app) handles this better.

    return app

# Main entry point
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
