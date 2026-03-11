import os
import time
from dotenv import load_dotenv
from src.db_manager import SheetManager
from src.job_fetcher import JobFetcher
from src.ai_tailor import ResumeTailor
from src.job_filter import JobEvaluator
import json
from src.pdf_generator import generate_pdf
from src.cloud_storage import upload_to_drive

def main():
    load_dotenv()

    print("\n[main] Initializing services...")
    try:
        sheet_manager = SheetManager()
        job_fetcher = JobFetcher()
        resume_tailor = ResumeTailor()
        job_evaluator = JobEvaluator()
    except Exception as e:
        err_msg = str(e)
        if "Expecting value" in err_msg or "JSONDecodeError" in err_msg or "not found" in err_msg:
            print("\n" + "="*80)
            print("[!] FATAL ERROR: Credentials missing or invalid!")
            print("[!] If running on GitHub Actions, you did not paste the FULL JSON into your Secrets.")
            print(f"[!] Please set GCP_SERVICE_ACCOUNT_JSON and GCP_OAUTH_TOKEN_JSON correctly.")
            print("="*80 + "\n")
        print(f"[main] Initialization failed: {e}")
        return

    print("\n[main] Fetching jobs from JSearch API...")
    try:
        new_jobs = job_fetcher.fetch_jobs()
    except Exception as e:
        print(f"[main] Failed to fetch jobs: {e}")
        return

    if not new_jobs:
        print("[main] No new jobs found. Exiting.")
        return

    print(f"\n[main] Processing {len(new_jobs)} new jobs...\n")

    for idx, job in enumerate(new_jobs, start=1):
        job_hash = job["job_hash_id"]
        company = job["company_name"]
        title = job["job_title"]
        description = job["job_description"]
        link = job["apply_link"]

        print(f"--- Job {idx}/{len(new_jobs)}: {company} - {title} ---")

        if sheet_manager.job_exists(job_hash):
            print(f"   [!] Job {job_hash} already exists in Sheet. Skipping.")
            continue

        print("   -> Evaluating job compatibility (Gemma 12B)...")
        try:
            verdict = job_evaluator.evaluate_job(description)
            decision = verdict.get("decision", "Proceed")
            match_score = verdict.get("match_score", "N/A")
            pain_point = verdict.get("extracted_pain_point", "N/A")
            eval_reason = verdict.get("evaluation_reason", "")
        except Exception as e:
            print(f"   [!] Job evaluation failed: {e}. Proceeding anyway.")
            decision = "Proceed"
            match_score = "N/A"
            pain_point = "N/A"
            eval_reason = f"Evaluation failed: {e}"

        if decision == "Rejected - Red Flag":
            reason = verdict.get("red_flag_reason", "Unknown")
            print(f"   [X] REJECTED (Red Flag): {reason}")
            sheet_manager.log_job(
                job_hash_id=job_hash, company=company, title=title,
                status="Rejected - Red Flag", match_score=match_score,
                evaluation_reason=eval_reason, pain_point=pain_point, job_link=link,
            )
            continue

        if decision == "Low Match":
            print(f"   [~] LOW MATCH (Score: {match_score}). Skipping.")
            sheet_manager.log_job(
                job_hash_id=job_hash, company=company, title=title,
                status="Low Match", match_score=match_score,
                evaluation_reason=eval_reason, pain_point=pain_point, job_link=link,
            )
            continue

        try:
            score_int = int(match_score)
        except (ValueError, TypeError):
            score_int = 0

        if score_int < 60:
            print(f"   [~] LOW MATCH (Score: {score_int} < 60). Skipping.")
            sheet_manager.log_job(
                job_hash_id=job_hash, company=company, title=title,
                status="Low Match", match_score=match_score,
                evaluation_reason=eval_reason, pain_point=pain_point, job_link=link,
            )
            continue

        print(f"   [OK] PROCEED (Score: {match_score}) | Pain Point: {pain_point}")

        print("   -> Tailoring application with Gemma 27B...")
        try:
            tailored_data = resume_tailor.tailor_application(description, company, title)
            bullets = tailored_data.get("tailored_bullet_points", [])
        except Exception as e:
            print(f"   [!] Failed to tailor application: {e}")
            continue

        print(f"   -> Generating tailored resume (PDF/TEX)...")
        pdf_result = generate_pdf(company, bullets)
        if pdf_result.get("status") != "success":
            print(f"   [!] Generation failed: {pdf_result.get('error')}")
            continue

        file_path = pdf_result.get("file_path", pdf_result.get("tex_path"))
        file_type = pdf_result.get("type", "tex").upper()
        print(f"   [OK] Saved locally: {file_path}")

        print(f"   -> Uploading {file_type} to Google Drive...")
        try:
            web_link = upload_to_drive(file_path, company)
            print(f"   [OK] Uploaded to Drive: {web_link}")
        except Exception as e:
            print(f"   [!] Drive upload failed: {e}")
            web_link = file_path # Fallback to local path if Drive fails

        print("   -> Logging to Google Sheet as 'Pending Review'...")
        sheet_manager.log_job(
            job_hash_id=job_hash, company=company, title=title,
            status="Pending Review", match_score=match_score,
            evaluation_reason=eval_reason, pain_point=pain_point,
            pdf_cloud_link=web_link, job_link=link,
        )
        print("   -> Logged.")

        print("   -> Pacing: sleeping 45s to respect TPM limit...")
        time.sleep(45)

    print("\n[main] Pipeline execution complete.")

if __name__ == "__main__":
    main()
