from flask import Flask, send_from_directory
import app as api_app_module

api = api_app_module.app

# Serve flowers.html from ./static
@api.route("/")
def index():
    return send_from_directory("static", "flowers.html")

# Optional: let Flask serve other static files from ./static automatically
# (Flask already serves under /static/<path> if you put files there.)

if __name__ == "__main__":
    api.run(host="127.0.0.1", port=5000, debug=True)