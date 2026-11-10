# A deliberately vulnerable app (SQL injection, XSS): the action's self-test expects inkdex to report it.
# Not under `test/` or `example/`: inkdex reads those as tests and examples, not the application.
import sqlite3

from flask import Flask, request

app = Flask(__name__)


@app.route("/user")
def user():
    name = request.args.get("name", "")
    db = sqlite3.connect("app.db")
    return str(db.execute("SELECT * FROM users WHERE name = '" + name + "'").fetchall())
