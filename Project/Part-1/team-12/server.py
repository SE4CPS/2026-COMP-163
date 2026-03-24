import admin
from app import app

def create_app():

    admin.init_db()
    admin.seed_data()

    return app

application = create_app()

if __name__ == "__main__":
    print(app.url_map)
    application.run(host="127.0.0.1", port=5001, debug=True)