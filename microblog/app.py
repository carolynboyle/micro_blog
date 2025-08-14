from flask import Flask

# Create Flask app instance
app = Flask(__name__)

@app.route("/")
def home():
    return "Microblog is running!"

# Run directly if executed (not needed when using `flask run`)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
