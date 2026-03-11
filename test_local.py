import os
import uuid
import time
from dotenv import load_dotenv

from src.db_manager import SheetManager
from src.ai_tailor import ResumeTailor
from src.job_filter import JobEvaluator
from src.pdf_generator import generate_pdf

def test_local_jd():
    load_dotenv()
    
    # 1. Provide a dummy Job Description
    company = "TechNova Solutions"
    title = "Full Stack Engineer"
    description = """
    About Us
    TechNova is a fast-growing startup building real-time collaboration tools. We are looking for a Full Stack Engineer to join our Vancouver team.

    Responsibilities:
    - Architect and build scalable backend services using Java and Spring Boot.
    - Develop responsive, interactive frontend components using React and Next.js.
    - Design and optimize relational databases (PostgreSQL) for high-throughput, low-latency queries.
    - Set up and maintain CI/CD pipelines using GitHub Actions.
    - Collaborate with product to define API contracts and feature requirements.

    Requirements:
    - 2+ years of professional software engineering experience.
    - Strong proficiency in Java, TypeScript, and SQL.
    - Experience with Spring Boot and React/Next.js.
    - Solid understanding of REST APIs and microservices.
    - Familiarity with AWS is a plus.
    - Excellent problem-solving and communication skills.
    
    Nice to have:
    - Experience with real-time technologies like WebSockets or Convex.
    """
    link = "https://example.com/job/technova-fullstack"
    job_hash = str(uuid.uuid4())[:12] # Generate a random hash for this test run

    print(f"\n--- Testing JD: {company} - {title} ---")
    
    try:
        sheet_manager = SheetManager()
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
        print(f"[!] Services failed to initialize: {e}")
        return

    print("-> Evaluating job compatibility (Gemma 12B)...")
    try:
        verdict = job_evaluator.evaluate_job(description)
        decision = verdict.get("decision", "Proceed")
        match_score = verdict.get("match_score", "N/A")
        pain_point = verdict.get("extracted_pain_point", "N/A")
        eval_reason = verdict.get("evaluation_reason", "")
    except Exception as e:
        print(f"[!] Job evaluation failed: {e}")
        return

    print(f"   [Decision: {decision}] Score: {match_score}")
    print(f"   [Reason: {eval_reason}]")

    print("\n-> Tailoring application (Gemma 27B)...")
    try:
        tailored_data = resume_tailor.tailor_application(description, company, title)
        bullets = tailored_data.get("tailored_bullet_points", [])
    except Exception as e:
        print(f"[!] Tailoring failed: {e}")
        return

    print("\nGenerated Bullets:")
    for b in bullets:
        print(f" - {b}")

    from src.cloud_storage import upload_to_drive

    print("\n-> Generating Resume (PDF/TEX)...")
    pdf_result = generate_pdf(company, bullets)
    if pdf_result.get("status") != "success":
        print(f"[!] Generation failed: {pdf_result.get('error')}")
        return

    file_path = pdf_result.get("file_path", pdf_result.get("tex_path"))
    file_type = pdf_result.get("type", "tex").upper()
    print(f"   [OK] Saved locally: {file_path}")

    print(f"\n-> Uploading {file_type} to Google Drive...")
    web_link = upload_to_drive(file_path, company)
    if web_link:
        print(f"   [OK] Uploaded to Drive: {web_link}")
    else:
        print("   [!] Drive upload failed or was skipped. Using local path.")
        web_link = file_path

    print("\n-> Logging to Google Sheet as 'Pending Review'...")
    try:
        sheet_manager.log_job(
            job_hash_id=job_hash, company=company, title=title,
            status="Pending Review", match_score=match_score,
            evaluation_reason=eval_reason, pain_point=pain_point,
            pdf_cloud_link=web_link, job_link=link,
        )
        print("   [OK] Logged to Sheet.")
    except Exception as e:
        print(f"[!] Failed to log to sheet: {e}")

    print("\nTest Complete! You can now run `streamlit run app.py` to view the generated LaTeX.")

if __name__ == "__main__":
    test_local_jd()
