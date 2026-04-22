from flask import Flask
import admin
from frontend import frontend_bp
import backend

def create_app():
    app = Flask(__name__)


    app.register_blueprint(frontend_bp)
    return app


if __name__ == "__main__":
	# app = Flask(__name__)
	# app.register_blueprint(frontend_bp)
	# app.run(host="127.0.0.1", port=5001, debug=True)

	while True:
		user = input("Choice: ")
		match user:
			case "d":
				print("Delete db")
				admin.del_db()
			case "s":
				admin.seed_data()
			case "i":
				print("Init db")
				admin.init_db()
			case "gc":
				print("Gen customers")
				admin.generate_customers()
			case "go":
				print("Gen orders")
				admin.generate_orders()
			case "q":
				print("Running query")
				rows = backend.slow()
				print(len(rows))
				for r in rows:
					print(r)
			case _:
				print("Invalid choice")
				continue
