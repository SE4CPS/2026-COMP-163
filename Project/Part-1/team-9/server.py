import admin
from app import app
from threading import Thread
from time import sleep

WATER_LEVEL_UPDATE_INTERVAL = 24 * 60 * 60  # 1 day in seconds


def update_loop():
    # currently just updates water level every 24 hours
    while True:
        print("updating water levels")
        admin.update_water_levels()
        sleep(WATER_LEVEL_UPDATE_INTERVAL)


def create_app():
    admin.init_db()
    admin.seed_data()

    update_thread = Thread(target=update_loop, daemon=True)
    update_thread.start();

    return app

application = create_app()

if __name__ == "__main__":
    application.run(host="127.0.0.1", port=5001, debug=True)
