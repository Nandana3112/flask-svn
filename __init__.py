from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import os
import shlex
import tempfile

app = Flask(__name__)

# ===Path configurations===
SVN_BIN = r"C:\Program Files\Apache Subversion\bin\svn.exe"
SVNADM_BIN = r"C:\Program Files\Apache Subversion\bin\svnadmin.exe"
REPO_BASE = r"C:\svn-repos"
REPO_PATH = r"C:\svn-repos\myrepo"
WORKING_COPY = r"C:\svn\myrepo_wc"

# ===Helper Functions===


def run_cmd(cmd, cwd=None):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)
    return proc.returncode, proc.stdout, proc.stderr


def file_url(path):
    p = os.path.abspath(path).replace('\\', '/')
    return "file:///" + p


def ensure_repo_and_wc(repo_path=REPO_PATH, wc_path=WORKING_COPY):
    os.makedirs(os.path.dirname(repo_path), exist_ok=True)
    repo_existed = os.path.isdir(repo_path)
    if not repo_existed:
        rc, out, err = run_cmd([SVNADM_BIN, "create", repo_path])
        if rc != 0:
            return False, f"svnadmin create failed: {err or out}"
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "trunk"), exist_ok=True)
            rc, out, err = run_cmd([SVN_BIN, "import", file_url(
                repo_path), "-m", "Initial import", file_url(tmp)])
            if rc != 0:
                return False, f"svn import failed: {err or out}"
    if not os.path.exists(wc_path) or not os.path.isdir(os.path.join(wc_path, ".svn")):
        os.makedirs(wc_path, exist_ok=True)
        rc, out, err = run_cmd(
            [SVN_BIN, "checkout", file_url(repo_path) + "/trunk", wc_path])
        if rc != 0:
            return False, f"svn checkout failed: {err or out}"
    return True, "SVN repository and working copy are ready."


def svn_info(wc_path=WORKING_COPY):
    rc, out, err = run_cmd([SVN_BIN, "info", wc_path])
    return rc == 0, out if rc == 0 else err


def svn_status(wc_path=WORKING_COPY):
    rc, out, err = run_cmd([SVN_BIN, "status", wc_path])
    return rc == 0, out if rc == 0 else err


def svn_add_force(path):
    rc, out, err = run_cmd([SVN_BIN, "add", "--force", path])
    return rc == 0, out if rc == 0 else err


def svn_commit(wc_path=WORKING_COPY, message="Committed via API"):
    rc, out, err = run_cmd([SVN_BIN, "commit", wc_path, "-m", message])
    return rc == 0, out if rc == 0 else err


def add_file_to_wc(filename, file_content):
    os.makedirs(WORKING_COPY, exist_ok=True)
    dest = os.path.join(WORKING_COPY, filename)
    if os.path.isabs(filename) or '..' in filename.replace('\\', '/'):
        raise ValueError("Invalid filename")
    with open(dest, 'wb') as fh:
        fh.write(file_content if isinstance(file_content, bytes)
                 else file_content.encode('utf-8'))
    ok, msg = svn_add_force(dest)
    return dest, msg


# ==Ensure Repository and Working Copy Exist===
ensure_repo_and_wc(REPO_PATH, WORKING_COPY)

# ===Flask Routes===


@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    if request.method == 'POST':
        files = request.files.getlist('files')
        commit_message = request.form.get(
            'commit_message') or 'Add files via web'
        added_files = []
        for f in files:
            if f and f.filename:
                try:
                    dest, msg = add_file_to_wc(f.filename, f.read())
                    added_files.append(f.filename)
                except Exception as e:
                    message = f"Error for {f.filename}: {str(e)}<br>"
        if added_files:
            ok, msg = svn_commit(WORKING_COPY, commit_message)
            if ok:
                message += f"Committed files: {', '.join(added_files)}"
            else:
                message += f"Commit failed: {msg}"
        elif not message:
            message = "No files were added."

    def gather_files():
        for root, dirs, files in os.walk(WORKING_COPY):
            dirs[:] = [d for d in dirs if d != '.svn']
            for fname in files:
                yield os.path.relpath(os.path.join(root, fname), WORKING_COPY)
    files = sorted(gather_files())
    return render_template('home.html', files=files, message=message)


@app.route('/svn/info')
def info():
    ok, out = svn_info(WORKING_COPY)
    return jsonify({"info": out} if ok else {"error": out})


@app.route('/svn/status')
def status():
    ok, out = svn_status(WORKING_COPY)
    return jsonify({"status": out} if ok else {"error": out})


@app.route('/svn/create', methods=['POST'])
def create_repo():
    data = request.get_json(force=True, silent=True)
    repo_name = data.get('repo_name')
    if not repo_name:
        return jsonify({"error": "Repository name is Required"}), 400
    repo_path = os.path.join(REPO_BASE, repo_name)
    ok, msg = ensure_repo_and_wc(repo_path, WORKING_COPY)
    return jsonify({"message": msg} if ok else (jsonify({"error": msg}), 500))


@app.route('/svn/add_file', methods=['POST'])
def add_file():
    data = request.get_json(force=True, silent=True)
    filename = data.get('filename')
    content = data.get('content', '')
    if not filename:
        return jsonify({"error": "Filename is Required"}), 400
    try:
        dest, msg = add_file_to_wc(filename, content)
        return jsonify({"message": msg, "file_path": dest})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/svn/commit', methods=['POST'])
def commit():
    data = request.get_json(force=True, silent=True) or {}
    message = data.get('message', 'Committed via API')
    ok, msg = svn_commit(WORKING_COPY, message)
    return jsonify({"message": f"Committed with message: {message}"} if ok else (jsonify({"error": msg}), 500))


if __name__ == "__main__":
    app.run(debug=True)
