# 🩺 Mani — AI Medical Research Assistant

Mani is an AI-powered medical assistant that answers medical questions, analyzes uploaded medical reports and scans, explains medicines and results in plain language, tracks health trends over time, and remembers conversation history across sessions.

🔗 **Live App:** https://mani-medical-research-agent1.onrender.com/

---

## ✨ Features

- **Medical Q&A** — Ask general medical/health questions and get clear, reliable answers.
- **Report & Scan Analysis** — Upload lab reports, prescriptions, or scan summaries; Mani extracts and explains the medicines, values, and findings in simple, non-technical language.
- **Health Trend Tracking** — Automatically tracks key metrics (e.g. blood sugar, cholesterol, BP) across multiple report uploads over time, so you can see how your health is trending.
- **Chat History** — Conversations and analyzed reports are saved, so you can pick up where you left off.
- **Simplified Explanations** — Converts clinical/medical jargon into everyday language anyone can understand.

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| LLM | [Groq](https://groq.com/) — fast LLM inference |
| LLM Framework | [LangChain] |
| AI Workflow | [LangGraph] |
| Medical Literature | [PubMed email configuration] — for evidence-based medical information |
| News / Current Info | [NewsAPI](https://newsapi.org/) — for health/medical news context |
| Database | PostgreSQL — user login, authentication, chat history & health trend storage |
| Database Hosting | Neon PostgreSQL |
| Authentication | [Flask-Login] |
| ORM | [Flask-SQLAlchemy] |
| Environment Management | [python-dotenv] |
| Backend | [Flask] |
| Frontend | [HTML/CSS/JavaScript with Jinja templates] |
| PDF Processing | [PyMuPDF (fitz)] |
| Deployment | Render |

## 📁 Project Structure

```
Medical_Research_Agent/
│
├── app.py
├── graph.py
├── report_analyzer.py
├── scan_analyzer.py
├── models.py
├── extensions.py
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── research.html
│   ├── reports.html
│   ├── scans.html
│   ├── medicines.html
│   ├── history.html
│   ├── trends.html
│   ├── profile.html
│   └── about.html
│
├── static/
│   ├── css/
│   └── ...
│
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ How It Works

1. **User logs in** (authentication backed by PostgreSQL) and uploads a report/scan or asks a question via the chat interface.
2. **Document parsing** (if a file is uploaded) extracts text, medicine names, and lab values.
3. **Groq-powered LLM** interprets the extracted data / question, cross-references relevant findings via the **PubMed API** for evidence-based accuracy, and pulls supplementary context via **NewsAPI** where relevant, then generates a plain-language explanation.
4. **Trend engine** compares new report values against previously stored ones for the user (from PostgreSQL) and updates health trend charts over time.
5. **Chat history** for each user is saved in PostgreSQL for later reference across sessions.

## 🚀 Running Locally

```bash
git clone https://github.com/yourusername/mani.git
cd mani

# backend setup
pip install -r requirements.txt
cp .env.example .env   # add your API keys and DB config
python app.py

# if frontend is separate
cd frontend
npm install
npm start
```

## 🔑 Environment Variables

```
GROQ_API_KEY=your_groq_api_key_here
PUBMED_API_KEY=your_pubmed_api_key_here
NEWSAPI_KEY=your_newsapi_key_here
DATABASE_URL=your_postgresql_connection_string_here
```

## ⚠️ Disclaimer

Mani provides general health information and simplified explanations of medical reports for educational purposes only. It is **not a substitute for professional medical advice, diagnosis, or treatment**. Always consult a qualified healthcare provider regarding any medical condition or before making health decisions.

## 📫 Contact

Feel free to reach out via [your email / LinkedIn / GitHub profile link] for questions or collaboration.
