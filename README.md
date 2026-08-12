# 📚 Decoupled PDF / Document Q&A Chatbot (RAG + Groq)

A clean, decoupled **Retrieval-Augmented Generation (RAG)** application featuring a **FastAPI backend REST API** and a **Modern HTML/CSS/JS frontend**.

---

## 🏗️ Architecture & Project Structure

```text
pdf_qa_rag_groq_decoupled/
├── backend/
│   ├── main.py            # FastAPI REST API (/api/upload, /api/query, /api/health)
│   ├── rag_engine.py      # LangChain + FAISS + Groq integration
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment template
├── frontend/
│   ├── index.html         # User interface
│   ├── style.css          # Dark-theme responsive styling
│   └── script.js          # API client calling FastAPI endpoints
├── sample_doc.txt         # Sample testing document
└── README.md              # Instructions & Deployment guide
```

---

## ⚡ Local Setup Guide

### Step 1: Run the Backend (FastAPI)

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # Windows:
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file and set your Groq API key:
   ```bash
   cp .env.example .env
   ```
   *(Edit `.env` to insert `GROQ_API_KEY=gsk_your_actual_key`).*

5. Start the FastAPI server:
   ```bash
   python main.py
   ```
   *The backend server will run at `http://localhost:8000`. You can test API endpoints at `http://localhost:8000/docs`.*

---

### Step 2: Run the Frontend (HTML/CSS/JS)

Since the frontend is static HTML/JS, you can serve it in any of the following ways:

- **Method A (Python Simple Server):**
  ```bash
  cd ../frontend
  python3 -m http.server 3000
  ```
  Open `http://localhost:3000` in your browser.

- **Method B (VS Code Live Server):**
  Right-click `frontend/index.html` in VS Code and click **Open with Live Server**.

- **Method C (Direct Browser Open):**
  Double-click `frontend/index.html` to open it in your browser.

---

## 💬 Real Prompt Examples

Upload `sample_doc.txt` in the UI and test the following prompts:

1. **Executive Summary Prompt:**
   > *"Give me a concise 3-bullet summary of this document."*

2. **Policy Lookup Prompt:**
   > *"What is the policy regarding AI code pull request reviews?"*

3. **Financial Data Prompt:**
   > *"What was Acme Corp's ARR and R&D spending in 2026?"*

4. **Negative Constraint / Unknown Information Test:**
   > *"What is the policy on employee vacation leave?"*  
   *(Expected response: States clearly that the document does not mention employee vacation leave).*

---

## ☁️ Deployment Guide

### Deploying Backend (FastAPI)
- **Render / Railway / Fly.io:**
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Set Environment Variable: `GROQ_API_KEY`

### Deploying Frontend (Static Web Hosting)
- **Vercel / Netlify / GitHub Pages:**
  - Deploy the `frontend/` folder directly.
  - Update `BACKEND_URL` in `frontend/script.js` to point to your live deployed backend URL (e.g. `https://your-rag-backend.onrender.com`).
