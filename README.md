# flask-svn

This README demonstrates the common workflow for the Flask SVN app:

1. Create a new repository
2. Add a new file to the working copy
3. Commit the file to the repository

All examples use the API endpoints via `curl`. The server is assumed to run at `http://127.0.0.1:5000`.

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



## 2b. Adding a new file to the working copy via the Web Interface

**Input**

1. Open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
2. Use the **file upload form** presented on the homepage (`home.html`):
   - Click "Choose File" or "Browse", select `test.txt` from your PC.
   - Click "Upload".

**Output**

- On successful upload, you will see a message on the page such as:

  Committed files: test.txt

```
- The file will also appear in the "Files in Working Copy" list below the upload form.
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
