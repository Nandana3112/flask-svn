from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

SVN_BIN = r"C:\Program Files\VisualSVN Server\bin\svn.exe"
WORKING_COPY = r"C:\svn\testrepo_wc"

def svn_info():
    return subprocess.check_output([SVN_BIN, "info", WORKING_COPY], universal_newlines=True)

def svn_status(path):
    result = subprocess.run([SVN_BIN, "status", path], stdout=subprocess.PIPE)
    return result.stdout.decode()

@app.route('/')
def home():
    return """
    <h2>Welcome to the SVN API!</h2>
    <p>Try <a href="/svn/info">/svn/info</a> or <a href="/svn/status">/svn/status</a></p>
    """

@app.route('/svn/info')
def info_route():
    info = svn_info()
    return jsonify({"info": info})

@app.route('/svn/status')
def status_route():
    status = svn_status(WORKING_COPY)
    return jsonify({"status": status})

if __name__ == "__main__":
    app.run(debug=True)