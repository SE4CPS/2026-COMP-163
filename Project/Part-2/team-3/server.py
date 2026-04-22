from flask import Flask, jsonify
import admin
from frontend import frontend_bp

def create_app():
    app = Flask(__name__)

    admin.init_db()
    admin.seed_data()
    admin.create_indexes()


    app.register_blueprint(frontend_bp)

    @app.route("/slow_query", methods=["GET"])
    def slow_query():
        return jsonify(admin.run_slow_query())

    @app.route("/fast_query", methods=["GET"])
    def fast_query():
        return jsonify(admin.run_fast_query())
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)