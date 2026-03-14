"""
Shared Gemini API client with automatic key cascading.

If the primary key (GEMMA_API_KEY) hits a quota limit (429 / ResourceExhausted),
the module automatically retries with the backup key (GEMMA_API_KEY_BACKUP).

Usage:
    from src.gemini_client import gemini_generate
    response_text = gemini_generate(model="gemma-3-27b-it", contents=prompt)
"""

import os
import time
from google import genai

# ---------------------------------------------------------------------------
# Load API keys from environment (keys are in .env / GitHub Secrets)
# ---------------------------------------------------------------------------
_PRIMARY_KEY = os.environ.get("GEMMA_API_KEY")
_BACKUP_KEY = os.environ.get("GEMMA_API_KEY_BACKUP")

if not _PRIMARY_KEY:
    raise ValueError("Environment variable GEMMA_API_KEY is not set.")

_primary_client = genai.Client(api_key=_PRIMARY_KEY)
_backup_client = genai.Client(api_key=_BACKUP_KEY) if _BACKUP_KEY else None

_active_client = _primary_client
_active_label = "PRIMARY"


def gemini_generate(model: str, contents: str) -> str:
    """
    Call the Gemini API with automatic key cascading.

    1. Try the primary key.
    2. If quota is exhausted (429), switch to the backup key and retry.
    3. If no backup exists, raise the error.

    Returns the response text.
    """
    global _active_client, _active_label

    for attempt in range(2):  # At most 2 attempts (primary → backup)
        try:
            response = _active_client.models.generate_content(
                model=model,
                contents=contents,
            )
            return response.text

        except Exception as e:
            error_str = str(e).lower()
            is_quota_error = any(keyword in error_str for keyword in [
                "429", "resource_exhausted", "quota", "rate limit",
                "resourceexhausted", "too many requests",
            ])

            if is_quota_error and _backup_client and _active_client is _primary_client:
                print(f"\n[gemini_client] ⚠️  PRIMARY key quota exhausted. Switching to BACKUP key...")
                _active_client = _backup_client
                _active_label = "BACKUP"
                time.sleep(2)  # Brief pause before retrying
                continue
            elif is_quota_error and _active_client is _backup_client:
                print(f"[gemini_client] ⚠️  BACKUP key also exhausted. Waiting 60s before retry...")
                time.sleep(60)
                # Reset to primary for next call (quota may have refreshed)
                _active_client = _primary_client
                _active_label = "PRIMARY"
                raise
            else:
                raise

    raise RuntimeError("[gemini_client] All API keys exhausted after cascading attempts.")
