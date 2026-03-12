# 🔐 AI Job Autopilot — Requirements & Credentials

> **⚠️ SENSITIVE FILE** — This file contains credential identifiers. Do NOT commit actual secret values to Git.

---

## Python Dependencies

```
requests              # HTTP client for JSearch API
gspread               # Google Sheets Python client
oauth2client          # Service Account authentication for Sheets
python-dotenv         # .env file loader
google-genai          # Google Gemini/Gemma AI SDK
google-api-python-client  # Google Drive API v3
streamlit             # Web dashboard framework
google-auth           # OAuth2 credentials handling (transitive)
google-auth-oauthlib  # OAuth2 InstalledAppFlow (for tools/oauth_setup.py)
```

Install: `pip install -r requirements.txt`

---

## System Dependencies (GitHub Actions Only)

```bash
# LaTeX compiler for PDF generation (installed in GitHub Actions)
sudo apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra
```

---

## API Keys & Services

### 1. Google Gemini API (AI Studio)
| Field | Value |
|-------|-------|
| **Env Variable** | `GEMMA_API_KEY` |
| **Used By** | `src/ai_tailor.py` (27B), `src/job_filter.py` (12B) |
| **Models** | `gemma-3-12b-it` (evaluation), `gemma-3-27b-it` (tailoring) |
| **Console** | [Google AI Studio](https://aistudio.google.com/apikey) |
| **Value** | `<YOUR_GEMMA_API_KEY>` |

### 2. RapidAPI — JSearch
| Field | Value |
|-------|-------|
| **Env Variable** | `RAPIDAPI_KEY` |
| **Host** | `jsearch.p.rapidapi.com` |
| **Used By** | `src/job_fetcher.py` |
| **Console** | [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) |
| **Value** | `<YOUR_RAPIDAPI_KEY>` |

### 3. Google Sheets
| Field | Value |
|-------|-------|
| **Env Variable** | `GOOGLE_SHEETS_CREDENTIALS` |
| **Points To** | `Req_File/autojobs-489723-decb2ee3f6e0.json` (Service Account) |
| **Sheet ID Env** | `GOOGLE_SHEETS_ID` |
| **Sheet ID** | `<YOUR_GOOGLE_SHEETS_ID>` |
| **Sheet URL** | [Open Sheet](https://docs.google.com/spreadsheets/d/<YOUR_GOOGLE_SHEETS_ID>) |
| **Service Account Email** | `<YOUR_SERVICE_ACCOUNT>@<PROJECT_ID>.iam.gserviceaccount.com` |

### 4. Google Drive
| Field | Value |
|-------|-------|
| **Auth Method** | OAuth 2.0 (`Req_File/token.json`) |
| **Env Variable** | `DRIVE_ROOT_FOLDER_ID` |
| **Root Folder ID** | `<YOUR_DRIVE_ROOT_FOLDER_ID>` |
| **Used By** | `src/cloud_storage.py` |
| **OAuth Client** | Desktop App (`Req_File/credentials.json`) |
| **Drive Account** | `<YOUR_GMAIL_ACCOUNT>` |

### 5. Safe Mode Email
| Field | Value |
|-------|-------|
| **Env Variable** | `SAFE_MODE_EMAIL` |
| **Value** | `<YOUR_EMAIL>` |

---

## GCP Project Details

| Field | Value |
|-------|-------|
| **Project ID** | `<YOUR_GCP_PROJECT_ID>` |
| **Service Account** | `<YOUR_SERVICE_ACCOUNT>@<PROJECT_ID>.iam.gserviceaccount.com` |
| **OAuth Client ID** | `<YOUR_OAUTH_CLIENT_ID>.apps.googleusercontent.com` |
| **APIs Enabled** | Google Sheets API, Google Drive API |
| **Console** | [GCP Console](https://console.cloud.google.com/apis/dashboard?project=<YOUR_GCP_PROJECT_ID>) |

---

## GitHub Repository Secrets

These secrets are configured in **Settings → Secrets → Actions** on `Aadish001/ai-job-autopilot`:

| Secret Name | Source | Description |
|------------|--------|-------------|
| `GEMMA_API_KEY` | `.env` | Google AI Studio API key |
| `RAPIDAPI_KEY` | `.env` | RapidAPI JSearch key |
| `DRIVE_ROOT_FOLDER_ID` | `.env` | Google Drive root folder ID |
| `SAFE_MODE_EMAIL` | `.env` | Fallback notification email |
| `GOOGLE_SHEETS_ID` | `.env` | Google Sheet spreadsheet ID |
| `GCP_SERVICE_ACCOUNT_JSON` | Full contents of `Req_File/autojobs-*.json` | GCP Service Account (for Sheets) |
| `GCP_OAUTH_TOKEN_JSON` | Full contents of `Req_File/token.json` | OAuth refresh token (for Drive) |

---

## Streamlit Cloud Secrets

Located at `.streamlit/secrets.toml` (gitignored). Copy-paste into **Streamlit Cloud → App Settings → Secrets**.

Contains:
- `GOOGLE_SHEETS_ID` — Sheet ID string
- `GCP_SERVICE_ACCOUNT_JSON` — Full JSON blob (multi-line TOML string)

---

## Local `.env` File

```env
# Google Gemini API Key (AI Studio)
GEMMA_API_KEY=<YOUR_GEMMA_API_KEY>

# RapidAPI (JSearch)
RAPIDAPI_KEY=<YOUR_RAPIDAPI_KEY>

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS=Req_File/<YOUR_SERVICE_ACCOUNT_FILE>.json
GOOGLE_SHEETS_ID=<YOUR_GOOGLE_SHEETS_ID>

# Google Drive
DRIVE_ROOT_FOLDER_ID=<YOUR_DRIVE_ROOT_FOLDER_ID>

# Safe mode email
SAFE_MODE_EMAIL=<YOUR_EMAIL>
```

---

## Credential Files (in `Req_File/`)

| File | Purpose | How to Generate |
|------|---------|-----------------|
| `autojobs-489723-decb2ee3f6e0.json` | GCP Service Account key (Sheets auth) | GCP Console → IAM → Service Accounts → Keys → Add Key |
| `credentials.json` | OAuth 2.0 Desktop App client | GCP Console → APIs & Services → Credentials → OAuth Client |
| `token.json` | OAuth refresh token (Drive auth) | Run `python tools/oauth_setup.py`, authenticate in browser |

---

## Job Search Configuration

| Parameter | Value |
|-----------|-------|
| **Target Roles** | Full Stack Developer, Software Developer |
| **Target Locations** | Vancouver, Toronto (Metro Vancouver & Ontario) |
| **Search Queries** | 4 combinations of role × location |
| **Date Posted** | `month` (last 30 days) |
| **Results Per Query** | 10 |
| **Min Match Score** | 60/100 |
