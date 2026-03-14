import os
import re
import json
from src.gemini_client import gemini_generate


class ResumeTailor:
    """
    Uses the Google GenAI SDK (Gemma 3 27B-IT) to generate
    tailored resume bullet points and a cold email from a
    job description, grounded strictly in the user's master profile.

    Enhanced: dynamically identifies skills from the JD that the
    candidate possesses but that are not yet highlighted, and weaves
    them into the tailored bullets.
    """

    MODEL = "gemma-3-27b-it"
    PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "master_profile.json")

    def __init__(self):
        # API key validation is handled by gemini_client module
        pass

    def _load_profile(self) -> dict:
        with open(self.PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _clean_response(text: str) -> dict:
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
        cleaned = re.sub(r"```\s*$", "", cleaned.strip())
        return json.loads(cleaned)

    def tailor_application(
        self,
        job_description_text: str,
        company_name: str,
        job_title: str,
    ) -> dict:
        profile = self._load_profile()

        prompt = (
            "You are an elite career strategist with deep expertise in Full Stack Development, "
            "Backend API design, Frontend React/Next.js engineering, and modern cloud-native hiring.\n\n"

            "## RULES\n"
            "1. **No Hallucination.** You must NEVER fabricate skills, tools, metrics, or "
            "experiences the candidate does NOT possess. Only reference what exists in "
            "their CANDIDATE PROFILE below.\n\n"

            "2. **Strict JSON Output.** Return **only** valid JSON with exactly one key:\n"
            '   - `"tailored_bullet_points"`: a JSON array of exactly 5 powerful, '
            "ATS-optimised resume bullet points (strings).\n"
            "   Do NOT wrap the JSON in markdown code fences or add any text outside it.\n\n"

            "3. **Dynamic Skill Injection from JD (CRITICAL).** Before writing bullets, "
            "carefully cross-reference the JOB DESCRIPTION against the CANDIDATE PROFILE. "
            "Identify every skill, technology, framework, or methodology mentioned in the JD "
            "that the candidate genuinely possesses (listed in their profile). "
            "You MUST weave these matching skills naturally into the bullet points — even "
            "if they are not prominently featured in the candidate's existing experience bullets. "
            "For example, if the JD mentions 'PostgreSQL' and the candidate lists it under "
            "cloud_data skills, reference it in a bullet. This maximises ATS keyword matching.\n\n"

            "4. **STAR+ Narrative Pivot.** When generating bullet points from the "
            "candidate's past full-stack development experience, dynamically reframe "
            "each accomplishment to align with the specific role requirements. Retain every "
            "original quantitative metric exactly as stated in the profile.\n\n"

            "5. **Self-Referencing Portfolio Injection.** Evaluate the job title "
            f'"{job_title}":\n'
            "   - **IF backend-heavy** (Backend Engineer, API Developer, etc.): highlight the "
            "candidate's \"Real-Time Web IDE\" project emphasising Spring Boot service, "
            "15+ REST APIs, execution caching, and cold-start optimisation.\n"
            "   - **IF frontend-heavy** (Frontend Developer, UI Engineer, etc.): highlight the "
            "candidate's \"Real-Time Stock Market App\" project emphasising Next.js 15, "
            "real-time updates, and alerting UI.\n"
            "   - **IF full-stack** (Full Stack Developer, Software Engineer, etc.): blend "
            "highlights from BOTH projects.\n\n"

            "6. **PLACEHOLDER BAN (CRITICAL).** The company you are writing for is "
            f'"**{company_name}**" and the role title is "**{job_title}**". '
            "Under **NO circumstances** may you use ANY bracketed placeholder "
            "tokens anywhere in your output. This includes, but is not limited to: "
            "`[Company Name]`, `[Startup]`, `[Your Name]`, `[Technology]`, "
            "or ANY other `[...]` token.\n\n"

            "7. **Quantify Everything.** Every bullet MUST contain at least one "
            "quantitative metric (percentage improvement, count, latency, throughput, etc.) "
            "drawn from the candidate's actual profile data.\n\n"

            "## CANDIDATE PROFILE\n"
            f"```json\n{json.dumps(profile, indent=2)}\n```\n\n"

            f"## TARGET COMPANY: {company_name}\n"
            f"## TARGET ROLE: {job_title}\n\n"
            "## JOB DESCRIPTION\n"
            f"```\n{job_description_text}\n```\n\n"

            "Now generate the JSON output."
        )

        response_text = gemini_generate(
            model=self.MODEL,
            contents=prompt,
        )

        return self._clean_response(response_text)
