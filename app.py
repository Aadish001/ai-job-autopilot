import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.db_manager import SheetManager

st.set_page_config(
    page_title="AI Job Autopilot - Mission Control",
    page_icon="\U0001f3af",
    layout="wide",
)


def bootstrap_cloud_env():
    """Write credential files and inject env vars from Streamlit Secrets."""
    try:
        os.makedirs("Req_File", exist_ok=True)
        if "GCP_SERVICE_ACCOUNT_JSON" in st.secrets:
            sa_path = os.path.join("Req_File", "gcp_service_account.json")
            with open(sa_path, "w") as f:
                f.write(st.secrets["GCP_SERVICE_ACCOUNT_JSON"])
            os.environ.setdefault("GOOGLE_SHEETS_CREDENTIALS", sa_path)
        for env_var in ["GOOGLE_SHEETS_ID"]:
            if env_var in st.secrets:
                os.environ.setdefault(env_var, st.secrets[env_var])
    except Exception:
        pass


bootstrap_cloud_env()


st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
    }
    .main-header h1 { color: #ffffff; font-size: 2.2rem; margin: 0; }
    .main-header p { color: #a0a0cc; font-size: 1rem; margin: 0.3rem 0 0 0; }
    </style>
    <div class="main-header">
        <h1>\U0001f3af AI Job Autopilot \u2014 Mission Control</h1>
        <p>Review AI-generated applications. Approve or reject tailored resumes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

NUM_COLS = 11
COL_NAMES = [
    "Job_Hash_ID", "Company", "Job_Title", "Status",
    "Match_Score", "Evaluation_Reason", "Pain_Point",
    "Email_Draft_Body", "PDF_Cloud_Link", "Job_Link",
    "Applied_To_Email",
]

@st.cache_resource(ttl=30)
def get_sheet_manager():
    return SheetManager()

def _parse_rows(raw):
    parsed = []
    for row in raw[1:]:
        row += [''] * (NUM_COLS - len(row))
        parsed.append(dict(zip(COL_NAMES, row[:NUM_COLS])))
    return parsed

def fetch_by_status(sheet, statuses):
    raw = sheet.sheet.get_all_values()
    if len(raw) < 2:
        return []
    rows = _parse_rows(raw)
    filtered = [r for r in rows if r["Status"] in statuses]
    for r in filtered:
        ms = r["Match_Score"]
        r["Match_Score"] = int(ms) if str(ms).isdigit() else 0
    return filtered

sheet_manager = get_sheet_manager()

tab1, tab2, tab3 = st.tabs([
    "\U0001f4cb Pending Review",
    "\u2705 Approved",
    "\U0001f5d1\ufe0f Evaluation Logs",
])

# TAB 1 - Pending Review
with tab1:
    pending_jobs = fetch_by_status(sheet_manager, ["Pending Review"])
    if not pending_jobs:
        st.success("\U0001f389 **All caught up!** No pending applications.")
    else:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Pending Review", len(pending_jobs))
        avg_score = sum(j["Match_Score"] for j in pending_jobs) / len(pending_jobs)
        col_m2.metric("Avg Match Score", f"{avg_score:.0f}")
        col_m3.metric("Top Match", max(j["Match_Score"] for j in pending_jobs))
        st.divider()

        for idx, job in enumerate(pending_jobs):
            job_hash = job["Job_Hash_ID"]
            company = job["Company"]
            title = job["Job_Title"]
            score_int = job["Match_Score"]
            eval_reason = job["Evaluation_Reason"]
            pain_point = job["Pain_Point"]
            tex_link = job["PDF_Cloud_Link"]
            job_link = job["Job_Link"]

            label = f"\U0001f3e2 {company}  |  \U0001f4bc {title}  |  \U0001f3af Match: {score_int}%"
            with st.expander(label, expanded=(idx == 0)):
                met_col1, met_col2, met_col3 = st.columns(3)
                with met_col1:
                    st.metric("Match Score", f"{score_int}%")
                    st.progress(min(score_int, 100) / 100.0)
                with met_col2:
                    if pain_point:
                        st.info(f"**Extracted Pain Point**\n\n{pain_point}")
                    else:
                        st.info("No pain point extracted.")
                with met_col3:
                    if tex_link:
                        st.caption(f"**LaTeX Path:** `{tex_link}`")
                    else:
                        st.caption("No LaTeX file available.")

                if eval_reason:
                    st.caption(f"**12B Evaluation:** {eval_reason}")
                st.divider()

                col_left, col_right = st.columns([1, 1])
                with col_left:
                    st.subheader("Context")
                    if job_link:
                        st.markdown(f"[\U0001f517 Link to Original Job Posting]({job_link})")
                    else:
                        st.caption("No job link available.")
                    st.markdown(f"**Company:** {company}")
                    st.markdown(f"**Role:** {title}")
                    st.markdown(f"**Match Score:** {score_int}%")
                    if pain_point:
                        st.markdown("---")
                        st.markdown(f"**Pain Point:** {pain_point}")

                with col_right:
                    st.subheader("Resume LaTeX")
                    if tex_link:
                        st.markdown(f"Generated LaTeX saved at: `{tex_link}`")
                        
                        # Add a quick download button or code display if the file exists
                        try:
                            if os.path.exists(tex_link):
                                with open(tex_link, "r", encoding="utf-8") as f:
                                    tex_content = f.read()
                                st.download_button(
                                    label="\u2b07\ufe0f Download .tex file",
                                    data=tex_content,
                                    file_name=os.path.basename(tex_link),
                                    mime="text/plain",
                                    key=f"dl_{job_hash}"
                                )
                                with st.expander("View LaTeX Source"):
                                    st.code(tex_content, language="latex")
                        except Exception as e:
                            st.caption(f"Could not read local file: {e}")
                    else:
                        st.caption("No LaTeX generated for this job.")

                st.divider()
                _, btn_left, btn_right, _ = st.columns([1, 2, 2, 1])
                with btn_left:
                    approve = st.button("\u2705 Approve", key=f"approve_{job_hash}", type="primary", use_container_width=True)
                with btn_right:
                    reject = st.button("\u274c Reject", key=f"reject_{job_hash}", use_container_width=True)

                if reject:
                    sheet_manager.update_status(job_hash, "Rejected - UI")
                    st.toast(f"Rejected: {company} \u2014 {title}", icon="\u274c")
                    st.rerun()
                if approve:
                    sheet_manager.update_status(job_hash, "Approved")
                    st.toast(f"Approved: {company} \u2014 {title}", icon="\u2705")
                    st.rerun()

# TAB 2 - Approved
with tab2:
    approved_jobs = fetch_by_status(sheet_manager, ["Approved"])
    if not approved_jobs:
        st.info("No approved applications yet.")
    else:
        st.metric("Total Approved", len(approved_jobs))
        st.divider()
        for job in approved_jobs:
            company = job["Company"]
            title = job["Job_Title"]
            score = job["Match_Score"]
            tex_link = job["PDF_Cloud_Link"]
            job_link = job["Job_Link"]
            with st.expander(f"\u2705 {company} \u2014 {title} (Score: {score}%)"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Company:** {company}")
                    st.markdown(f"**Role:** {title}")
                    st.markdown(f"**Match Score:** {score}%")
                    if job_link:
                        st.markdown(f"[\U0001f517 Job Posting]({job_link})")
                with c2:
                    if tex_link:
                        st.caption(f"**LaTeX Path:** `{tex_link}`")
                    else:
                        st.caption("No LaTeX link.")

# TAB 3 - Evaluation Logs
with tab3:
    eval_jobs = fetch_by_status(sheet_manager, ["Rejected - Red Flag", "Low Match", "Rejected - UI"])
    if not eval_jobs:
        st.info("No rejected or low-match jobs to display.")
    else:
        red_flags = [j for j in eval_jobs if j["Status"] == "Rejected - Red Flag"]
        low_matches = [j for j in eval_jobs if j["Status"] == "Low Match"]
        ui_rejects = [j for j in eval_jobs if j["Status"] == "Rejected - UI"]
        c1, c2, c3 = st.columns(3)
        c1.metric("\U0001f6a9 Red Flags", len(red_flags))
        c2.metric("\U0001f4c9 Low Match", len(low_matches))
        c3.metric("\U0001f5d1\ufe0f UI Rejected", len(ui_rejects))
        st.divider()
        for job in eval_jobs:
            company = job["Company"]
            title = job["Job_Title"]
            score = job["Match_Score"]
            status = job["Status"]
            eval_reason = job["Evaluation_Reason"]
            pain_point = job["Pain_Point"]
            icon = "\U0001f6a9" if "Red Flag" in status else ("\U0001f4c9" if status == "Low Match" else "\U0001f5d1\ufe0f")
            with st.expander(f"{icon} {company} \u2014 {title} | {status} | Score: {score}%"):
                st.markdown(f"**Status:** {status}")
                st.markdown(f"**Match Score:** {score}%")
                if eval_reason:
                    st.warning(f"**12B Evaluation Reason:**\n\n{eval_reason}")
                else:
                    st.caption("No evaluation reason recorded.")
                if pain_point:
                    st.info(f"**Pain Point:** {pain_point}")
