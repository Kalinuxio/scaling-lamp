from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.post("/run")
def run_command():
    cmd = request.json.get("cmd")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except Exception as e:
        return jsonify({"error": str(e)})

app.run(host="127.0.0.1", port=5000)
