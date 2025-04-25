## Steps — Running in PyCharm

### 1. **Install Python**

If not already installed:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```
---

### 📦 2. **Install Poetry (Dependency Manager)**

Run in terminal (Linux):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Then make sure it's in your `PATH`:

**Linux/macOS:**
```bash
export PATH="$HOME/.local/bin:$PATH"
```
or which ever PATH poetry was installed in.

Check it's working:
```bash
poetry --version
```

---

### 🧠 3. **Open in PyCharm IDE**
- Open the folder in **PyCharm**.
- PyCharm may auto-detect `pyproject.toml`. If not, follow the next step.

---

### ⚙️ 4. **Configure Poetry in PyCharm**

1. Go to **File > Settings (or Preferences on macOS) > Python Interpreter**
2. Click the ⚙️ (gear) icon → **Add**
3. Select **Poetry Environment**
4. Set:
   - **Environment**: "New" or "Existing" (you can reuse Poetry's env)
   - **Interpreter**: let it auto-find Python or browse to it

5. Click OK and Apply

---

### 📥 5. **Install Dependencies**

Open PyCharm’s terminal:
```bash
poetry install
```

This creates a virtual env and installs all dependencies from `pyproject.toml`.

---

### 🚀 6. **Run the FastAPI Server**

#### Terminal
```bash
uvicorn main:app --reload
```
---

### 🧪 7. **Test the Server**

- Find Documentation Here: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) → OpenAPI Docs

---

Use --reload flag for DEV
```commandline
uvicorn app:main --reload 
```

For PROD Build
```commandline
uvicorn app:main --reload 
```

[Production Endpoint HERE:](https://docushield-backend-production.up.railway.app)