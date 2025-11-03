# flask-svn

This README demonstrates the common workflow for the Flask SVN app:

1. Create a new repository
2. Add a new file to the working copy
3. Commit the file to the repository

The server is assumed to run at `http://127.0.0.1:5000`.

# Using the Flask SVN App GUI

You can manage your Subversion repository **without any command line or curl** simply use the web interface provided by the Flask app!

---

## 1. Uploading and Committing Files via the Web GUI

**Steps:**

1. **Start the Flask app**Run:

   ```
   python __init__.py
   ```

   or

   ```
   flask run
   ```

   *(depending on your setup)*
2. **Open your browser and go to:**[http://127.0.0.1:5000/](http://127.0.0.1:5000/)
3. **On the homepage, use the "Upload files to SVN Repository" form:**

   - Click **"Choose File"** and select one or more files from your computer.
   - Click **"Upload"**.
4. **Result:**

   - The files are added to the Subversion working copy and committed to the repository with your message.
   - You'll see a success message and the uploaded files listed under "Files in Working Copy".

---

## Example Workflow in the GUI

- Choose and upload files right from your browser.
- Each upload will:
  - Save the file(s) in the working copy.
  - Add them to SVN versioning.
  - Commit them to the repository.
- No need for curl, command line, or manual SVN commands.

---

## Use Cases with Curl/API

*(For power users and automation, see below for the curl/API commands.)*

---

## 1.Creating a new repository

**Input**

```bash
curl -X POST http://127.0.0.1:5000/svn/create_repo \
     -H "Content-Type: application/json" \
     -d '{"repo_name":"myrepo"}'
```

**Output**

```json
{
  "message": "SVN repository and working copy are ready."
}
```

---

## 2. Adding a new file to the working copy

**Input**

```bash
curl -X POST http://127.0.0.1:5000/svn/add_file \
     -H "Content-Type: application/json" \
     -d '{"filename":"greeting.txt", "content":"Hello from the API!"}'
```

**Output**

```json
{
  "message": "Added to working copy (scheduled for commit).",
  "file_path": "C:\\svn\\myrepo_wc\\greeting.txt"
}
```

---



## 3. Committing the file to the repository

**Input**

```bash
curl -X POST http://127.0.0.1:5000/svn/commit \
     -H "Content-Type: application/json" \
     -d '{"message":"Initial greeting.txt commit"}'
```

**Output**

```json
{
  "message": "Committed with message: Initial greeting.txt commit"
}
```

---
