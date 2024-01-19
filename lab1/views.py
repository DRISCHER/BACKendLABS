from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)



@app.route("/")
def start_page():
    return f"<a href='/healthcheck'>Lab1</a>"


@app.route("/healthcheck")
def healthcheck():
    otvet = jsonify(date=datetime.now(), status="OK")
    otvet.status_code = 200
    return otvet
