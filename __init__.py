from flask import Flask, render_template_string,request, redirect, url_for, jsonify
import subprocess
import os

app = Flask(__name__)

SVN_BIN = r"C:\Program Files\VisualSVN Server\bin\svn.exe"
SVNADM_BIN = r"C:\Program Files\VisualSVN Server\bin\svnadmin.exe"
REPO_PATH = r"C:\svn-repos\myrepo"
WORKING_COPY = r"C:\svn\myrepo_wc"

# Check repo exists, if not create one
if not os.path.exists(REPO_PATH):
    subprocess.check_call([SVNADM_BIN, "create", REPO_PATH])
    # Checkout working copy
    if not os.path.exists(WORKING_COPY):
        subprocess.check_call([SVN_BIN, "checkout", f"file:///{REPO_PATH.replace(os.sep, '/')}", WORKING_COPY])
elif not os.path.exists(WORKING_COPY):
    subprocess.check_call([SVN_BIN, "checkout", f"file:///{REPO_PATH.replace(os.sep, '/')}", WORKING_COPY])

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<title>SVN File Upload</title>
<h2>Upload files to SVN Repository</h2>
<form method="POST" enctype="multipart/form-data">
    <input type="file" name=files multiple />
    <input type=submit value=Upload />
</form>
{% if message %}
    <p>{{ message }}</p>
{% endif %}
<h3>Files in Working Copy:</h3>
<ul>
{% for f in files %}
    <li>{{ f }}</li>
{% endfor %}
</ul>
"""

def svn_info():
    return subprocess.check_output([SVN_BIN, "info", WORKING_COPY], universal_newlines=True)

def svn_status(path):
    result = subprocess.run([SVN_BIN, "status", path], stdout=subprocess.PIPE)
    return result.stdout.decode()

def create_repo(repo_name):
    repo_path = os.path.join(REPO_PATH, repo_name)
    subprocess.check_call([SVNADM_BIN, "create", repo_path])
    return repo_path

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
    return render_template_string(HTML_TEMPLATE, files=files, message=message)

@app.route('/svn/info')
def info_route():
    info = svn_info()
    return jsonify({"info": info})

@app.route('/svn/status')
def status_route():
    status = svn_status(WORKING_COPY)
    return jsonify({"status": status})

@app.route('/svn/create_repo', methods=['POST'])
def create_repo_route():
    data = request.get_json()
    repo_name = data.get('repo_name')
    if not repo_name:
        return jsonify({"error": "Repo_name is Required"}), 400
    repo_path = create_repo(repo_name)
    return jsonify({"message": f"Repository created at {repo_path}"})

@app.route('/svn/add_file', methods=['POST'])
def add_file_route():
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content', '')
    if not filename:
        return jsonify({"error": "Filename is Required"}), 400
    file_path = add_file_to_wc(filename, content)
    return jsonify({"message": f"File {file_path} added to working copy", "file_path": file_path})

@app.route('/svn/commit', methods=['POST'])
def commit_route():
    data = request.get_json()
    message = data.get('message', 'Committed via API')
    commit_message = commit_file(message)
    return jsonify({"message": commit_message})

if __name__ == "__main__":
    app.run(debug=True)