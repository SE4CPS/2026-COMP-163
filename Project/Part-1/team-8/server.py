from flask import Flask
import admin
from frontend import frontend_bp

def create_app():
    app = Flask(__name__)

    admin.init_db()
    admin.seed_data()

    app.register_blueprint(frontend_bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
