# AI Job Autopilot 🎯

A fully autonomous AI pipeline that scrapes job listings, filters them using **Model Cascading**, tailors LaTeX resumes with an LLM, and routes qualified applications to a **Human-in-the-Loop Streamlit dashboard** for final approval and dispatch.

---

## Overview

AI Job Autopilot eliminates the repetitive grind of job applications. Every day, a GitHub Actions workflow:

1. **Fetches** fresh job listings from the JSearch API (RapidAPI).
2. **Evaluates** each role against your master profile using a fast, lightweight LLM.
3. **Tailors** a resume and cold email for every qualifying job using a heavier creative model.
4. **Generates** a pixel-perfect LaTeX PDF resume.
5. **Uploads** the PDF to Google Drive (dynamic `YYYY-MM/Company/` folder routing).
6. **Logs** every decision to a Google Sheet for full auditability.

You then open the **Streamlit Mission Control** dashboard to review, edit email drafts, and dispatch — or reject — each application with one click.

---

## Architecture

### Model Cascade (Token-Efficient AI)

| Stage | Model | Purpose |
|-------|-------|---------|
| **Filtering & Scoring** | Gemma 3 **12B**-IT | Fast boolean red-flag detection, 0-100 match scoring, and pain-point extraction. Uses fewer tokens to stay within the 15k TPM budget. |
| **Creative Tailoring** | Gemma 3 **27B**-IT | Heavy prose generation: 5 ATS-optimised STAR+ bullet points and a 3-paragraph cold email with portfolio injection. |

### 3-Tier Confidence Routing

```
                    ┌─────────────────────┐
                    │  JobEvaluator (12B)  │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        🚩 Red Flag     📉 Low Match    ✅ Proceed
        (hard block)    (score < 60)    (score ≥ 60)
              │              │              │
              ▼              ▼              ▼
         Log & Skip     Log & Skip    Tailor (27B)
                                           │
                                     ┌─────┴─────┐
                                     ▼           ▼
                                 PDF Gen    Drive Upload
                                     │           │
                                     └─────┬─────┘
                                           ▼
                                   Log "Pending Review"
                                           │
                                           ▼
                                 ┌─────────────────┐
                                 │  Streamlit HITL  │
                                 │  Mission Control │
                                 └─────────────────┘
```

### Multi-Tab Dashboard

| Tab | Purpose |
|-----|---------|
| 📋 **Pending Review** | Full job cards with match score, pain point, editable email draft, PDF link, and Approve/Reject buttons. |
| ✅ **Dispatch History** | Applied jobs showing the recruiter email, score, and submitted PDF. |
| 🗑️ **Evaluation Logs** | Audit trail for rejected and low-match jobs with the 12B model's evaluation reasoning. |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.11+ |
| **AI Models** | Google Gemma 3 (12B-IT, 27B-IT) via `google-genai` SDK |
| **CI/CD** | GitHub Actions (scheduled daily cron) |
| **Frontend** | Streamlit (wide-layout Mission Control) |
| **Cloud Storage** | Google Drive API v3 (OAuth 2.0, resumable uploads) |
| **Database** | Google Sheets API (11-column schema via `gspread`) |
| **Job Source** | RapidAPI JSearch |
| **Resume** | LaTeX → `pdflatex` compilation |
| **Email** | SMTP2GO (with PDF attachment) |

---

## Project Structure

```
ai-job-autopilot/
├── main.py                  # Pipeline entry point (daily cron target)
├── app.py                   # Streamlit Mission Control dashboard
├── requirements.txt
├── .env                     # Local env vars (not committed)
├── .github/
│   └── workflows/
│       └── daily_autopilot.yml
├── src/
│   ├── job_fetcher.py       # JSearch API client
│   ├── job_filter.py        # JobEvaluator (Gemma 12B)
│   ├── ai_tailor.py         # ResumeTailor (Gemma 27B)
│   ├── pdf_generator.py     # LaTeX → PDF compiler
│   ├── cloud_storage.py     # Google Drive upload/download
│   ├── db_manager.py        # Google Sheets CRUD (11-col schema)
│   └── email_dispatcher.py  # SMTP cold email sender
├── data/
│   └── master_profile.json  # Candidate profile (skills, experience)
├── templates/
│   └── template.tex         # LaTeX resume template
├── tools/
│   ├── oauth_setup.py       # One-time OAuth token generator
│   └── test_dummy_jobs.py   # 3-job routing test harness
└── req_files/               # Credentials (gitignored)
    ├── gcp_service_account.json
    ├── client_secret.json
    └── token.json
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Pr33datorrr/ai-job-autopilot.git
cd ai-job-autopilot

# 2. Virtual environment
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install
pip install -r requirements.txt

# 4. Configure .env (see .env.example)

# 5. One-time OAuth setup for Google Drive
python tools/oauth_setup.py

# 6. Run the pipeline
python main.py

# 7. Launch Mission Control
streamlit run app.py
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMMA_API_KEY` | Google AI Studio API key |
| `RAPIDAPI_KEY` | RapidAPI key for JSearch |
| `GOOGLE_SHEETS_CREDENTIALS` | Path to GCP service account JSON |
| `GOOGLE_SHEETS_ID` | Google Sheet ID |
| `DRIVE_ROOT_FOLDER_ID` | Root Drive folder for PDF uploads |
| `SAFE_MODE_EMAIL` | Fallback email for Drive permissions |
| `SMTP2GO_USERNAME` | SMTP2GO username |
| `SMTP2GO_PASSWORD` | SMTP2GO password |

---

## License

MIT
