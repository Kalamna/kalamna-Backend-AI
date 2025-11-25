# **Project Setup & Run Instructions (Local + Docker)**

## **1. Run the Project Locally**

### **1. Create a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### **2. Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### **3. Run FastAPI**

```bash
uvicorn app.main:app --reload
```

### **4. Open API Documentation**

Swagger UI:

```
http://127.0.0.1:8000/doc
```

ReDoc:

```
http://127.0.0.1:8000/redoc
```

Root endpoint:

```
http://127.0.0.1:8000/
```

---

## **2. Run the Project with Docker**

### **1. Build Docker image**

```bash
docker build -t kalamna-api .
```

### **2. Run Docker container**

```bash
docker run -p 8000:8000 kalamna-api
```

### **3. Open API Documentation**

Swagger UI:

```
http://127.0.0.1:8000/doc
```

ReDoc:

```
http://127.0.0.1:8000/redoc
```

Root endpoint:

```
{"message": "Hello, World!"}
```

---

## **4. Ruff Commands (Quick Reference)**

| Action             | Command                               |
| ------------------ | ------------------------------------- |
| Lint               | `ruff check .`                        |
| Fix                | `ruff check . --fix`                  |
| Format             | `ruff format .`                       |
| Fix + Format       | `ruff check . --fix && ruff format .` |
| Lint specific file | `ruff check path/to/file.py`          |
---