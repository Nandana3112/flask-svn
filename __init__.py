from flask import Flask, render_template,request, redirect, url_for, jsonify
import subprocess
import os

app = Flask(__name__)

SVN_BIN = r"C:\Program Files\Apache Subversion\bin\svn.exe"
SVNADM_BIN = r"C:\Program Files\Apache Subversion\bin\svnadmin.exe"
REPO_PATH = r"C:\svn-repos\myrepo"
WORKING_COPY = r"C:\svn\myrepo_wc"

def repo_exists(name):
    """Check if a repository exists."""
    repo_path = os.path.join(REPO_PATH, name)
    return os.path.isdir(repo_path)

def create_repo(name):
    repo_path = os.path.join(REPO_PATH, name)
    if repo_exists(name):
        raise FileExistsError(f"Repository {name} already exists.")
    subprocess.check_call([SVNADM_BIN, "create", repo_path])
    return repo_path

def svn_info():
    return subprocess.check_output([SVN_BIN, "info", WORKING_COPY], universal_newlines=True)

def svn_status(path):
    result = subprocess.run([SVN_BIN, "status", path], stdout=subprocess.PIPE)
    return result.stdout.decode()

def add_file_to_wc(filename, content):
    file_path = os.path.join(WORKING_COPY, filename)
    with open(file_path, 'w') as f:
        f.write(content)
    subprocess.check_call([SVN_BIN, "add", file_path])
    return file_path

def commit_file(message):
    subprocess.check_call([SVN_BIN, "commit", WORKING_COPY, "-m", message])
    return "Committed with message: " + message

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    if request.method == 'POST':
        files = request.files.getlist('files')
        added = []
        for file in files:
            if file in files:
                dest = os.path.join(WORKING_COPY, file.filename)
                file.save(dest)
                try:
                    subprocess.check_call([SVN_BIN, "add", dest])
                    added.append(file.filename)
                except subprocess.CalledProcessError:
                    pass
        if added:
            commit_msg = f"Added files: {', '.join(added)}"
            subprocess.check_call([SVN_BIN, "commit", WORKING_COPY, "-m", commit_msg])
            message = f"Successfully added and committed: {', '.join(added)}"
        else:
            message = "No files were uploaded."
    files = [
        f for f in os.listdir(WORKING_COPY)
        if os.path.isfile(os.path.join(WORKING_COPY, f)) and not f.startswith('.svn')
    ]
    return render_template("home.html", files=files, message=message)

@app.route('/svn/info')
def info():
    info = svn_info()
    return jsonify({"info": info})

@app.route('/svn/status')
def status():
    status = svn_status(WORKING_COPY)
    return jsonify({"status": status})

@app.route('/svn/create', methods=['POST'])
def create():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "Repository name is Required"}), 400
    if repo_exists(name):
        return jsonify({"error": f"Repository '{name}' already exists."}), 400
    try:
        repo_path = create_repo(name)
        return jsonify({"message": f"Repository '{name}' created at {repo_path}"})
    except FileExistsError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/svn/add_file', methods=['POST'])
def add_file():
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content', '')
    if not filename:
        return jsonify({"error": "Filename is Required"}), 400
    file_path = add_file_to_wc(filename, content)
    return jsonify({"message": f"File {file_path} added to working copy", "file_path": file_path})

@app.route('/svn/commit', methods=['POST'])
def commit():
    data = request.get_json()
    message = data.get('message', 'Committed via API')
    commit_message = commit_file(message)
    return jsonify({"message": commit_message})

if __name__ == "__main__":
    app.run(debug=True)