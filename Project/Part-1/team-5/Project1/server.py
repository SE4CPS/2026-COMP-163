# takes html file from directory
from flask import send_from_directory
import admin
# from frontend import frontend_bp
from app import app as app_API, water_loss

app = app_API

admin.init_db()
admin.seed_data()

# calculates water loss once when server starts
water_loss()

@app.route('/')
def flowers_app():
    return send_from_directory('.', 'flowers.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)