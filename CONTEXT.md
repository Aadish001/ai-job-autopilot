# 🎯 AI Job Autopilot — Project Context

## Purpose
AI Job Autopilot is an automated job application pipeline designed for **Aadish Kaushal**. It autonomously:
1. Searches for relevant jobs (Full Stack Dev / Software Dev in Metro Vancouver & Ontario)
2. Evaluates each job description against Aadish's profile using AI
3. Tailors resume bullet points to match the specific JD
4. Generates a LaTeX resume → compiles to PDF (where `pdflatex` is available)
5. Uploads the final document to Google Drive
6. Logs everything to a Google Sheet for review via a Streamlit dashboard

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Job Search** | [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) (RapidAPI) | Fetches job postings from multiple boards |
| **AI Evaluation** | [Google Gemma 3 12B-IT](https://ai.google.dev/) (`google-genai`) | Scores job-candidate compatibility (0-100) |
| **AI Tailoring** | [Google Gemma 3 27B-IT](https://ai.google.dev/) (`google-genai`) | Generates 5 tailored bullet points per JD |
| **Resume Gen** | LaTeX (`pdflatex`) | Compiles `.tex` templates into polished PDFs |
| **Cloud Storage** | [Google Drive API v3](https://developers.google.com/drive/api/v3/about-sdk) | Organizes and stores generated resumes |
| **Database** | [Google Sheets API](https://developers.google.com/sheets/api) (`gspread` + `oauth2client`) | Tracks all jobs, scores, statuses, and links |
| **Dashboard** | [Streamlit](https://streamlit.io/) | Review, approve, or reject tailored applications |
| **Orchestration** | [GitHub Actions](https://docs.github.com/en/actions) | Daily cron schedule + manual `workflow_dispatch` |

---

## File Structure

```
ai-job-autopilot/
├── .github/workflows/
│   ├── daily_autopilot.yml      # Daily cron (17:00 UTC) + manual trigger
│   └── test_run.yml             # Manual-only test workflow (uses test_local.py)
├── .streamlit/
│   └── secrets.toml             # Streamlit Cloud secrets (gitignored)
├── data/
│   └── master_profile.json      # Aadish's full resume data (skills, experience, projects)
├── Req_File/                    # Credentials folder (gitignored)
│   ├── autojobs-*.json          # GCP Service Account JSON
│   ├── credentials.json         # OAuth Desktop App client (for generating token.json)
│   └── token.json               # OAuth refresh token (for Drive uploads)
├── src/
│   ├── ai_tailor.py             # Gemma 27B integration — generates tailored bullets
│   ├── cloud_storage.py         # Google Drive upload (OAuth) — folder management
│   ├── db_manager.py            # Google Sheets read/write via gspread
│   ├── email_dispatcher.py      # (Unused) SMTP2GO cold email sender
│   ├── job_fetcher.py           # JSearch API client — queries & deduplicates jobs
│   ├── job_filter.py            # Gemma 12B integration — evaluates JD compatibility
│   └── pdf_generator.py         # LaTeX template injection + optional pdflatex compilation
├── templates/
│   └── template.tex             # LaTeX resume template with [[BULLET1]]-[[BULLET5]] placeholders
├── tools/
│   └── oauth_setup.py           # One-time script to generate token.json via browser OAuth
├── app.py                       # Streamlit dashboard (Mission Control)
├── main.py                      # Production pipeline entry point
├── test_local.py                # Local test script with hardcoded dummy JD
├── verify_setup.py              # Quick environment variable checker
├── requirements.txt             # Python dependencies
├── .env                         # Local environment variables (gitignored)
└── .gitignore                   # Ignores Req_File/, .env, output/, secrets.toml
```

---

## Key Design Decisions

1. **LaTeX over HTML/PDF libraries**: LaTeX produces pixel-perfect, professional resumes that pass ATS scanners. The template uses `\item` bullet points with `[[BULLET1]]`–`[[BULLET5]]` placeholders for AI injection.

2. **Intelligent PDF Compilation**: `pdf_generator.py` automatically detects if `pdflatex` is installed. On GitHub Actions (where `texlive` is installed), it compiles to PDF. On local machines without LaTeX, it gracefully degrades to `.tex` output.

3. **OAuth for Drive, Service Account for Sheets**: Google Drive uploads require OAuth `token.json` (personal Drive doesn't support service account storage). Google Sheets uses the GCP Service Account for headless access.

4. **Dual AI Models**: The 12B model handles fast evaluation/scoring. The 27B model handles the more complex tailoring task, producing higher-quality output.

5. **45s Sleep Between Jobs**: Respects the Gemini API TPM (Tokens Per Minute) rate limit to avoid 429 errors during batch processing.
