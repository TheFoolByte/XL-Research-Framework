import os
import subprocess
import json
from flask import Flask, render_template, request, redirect, url_for

UPLOAD = "web/uploads"
REPORT = "output/reports"
STATS_FILE = "output/stats.json"

os.makedirs(UPLOAD, exist_ok=True)
os.makedirs("output", exist_ok=True)

app = Flask(__name__)


def get_stats():
    """Get analysis statistics"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {"total": 0, "threats": 0, "safe": 0}


def update_stats(is_threat=False):
    """Update statistics after analysis"""
    stats = get_stats()
    stats["total"] += 1
    if is_threat:
        stats["threats"] += 1
    else:
        stats["safe"] += 1
    
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)
    return stats


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        file = request.files["apk"]

        if file:

            path = os.path.join(UPLOAD, file.filename)
            file.save(path)

            result = subprocess.run([
                "python",
                "main.py",
                path
            ], capture_output=True, text=True)

            # Check if threats found (simple heuristic)
            is_threat = "High" in result.stdout or "RISK:" in result.stdout
            update_stats(is_threat)

            return redirect(url_for("reports", success=1))

    stats = get_stats()
    return render_template("index.html", stats=stats)


@app.route("/reports")
def reports():

    files = []
    stats = get_stats()

    if os.path.exists(REPORT):
        files = os.listdir(REPORT)

    success = request.args.get("success")

    return render_template(
        "report.html",
        files=files,
        stats=stats,
        success=success
    )


@app.route("/view/<name>")
def view(name):

    path = os.path.join(REPORT, name)

    with open(path) as f:
        data = f.read()

    return render_template("view.html", name=name, content=data)


@app.route("/api/stats")
def api_stats():
    """API endpoint for stats"""
    return get_stats()


if __name__ == "__main__":

    app.run(debug=True)
