import os
import re
import subprocess

# Paths relative to project root
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "template.tex")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


# ------------------------------------------------------------------
# LaTeX sanitisation
# ------------------------------------------------------------------

# Order matters: backslash must NOT be escaped here because the
# template itself is valid LaTeX - we only escape characters that
# the LLM might inject in free-text bullet strings.
_LATEX_SPECIAL = {
    "%": r"\%",
    "&": r"\&",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
}

_LATEX_RE = re.compile("|".join(re.escape(k) for k in _LATEX_SPECIAL))


def escape_latex(text: str) -> str:
    """
    Escape reserved LaTeX characters in *text* so it compiles safely.
    Handles: % & $ # _ { }
    """
    return _LATEX_RE.sub(lambda m: _LATEX_SPECIAL[m.group()], text)


# ------------------------------------------------------------------
# PDF generation
# ------------------------------------------------------------------

def generate_pdf(company_name: str, tailored_bullets_list: list) -> dict:
    """
    Inject *tailored_bullets_list* into the LaTeX template,
    and save the resulting .tex file.

    Parameters
    ----------
    company_name : str
        Used for creating a unique filename.
    tailored_bullets_list : list[str]
        Exactly 5 bullet-point strings to inject.

    Returns
    -------
    dict
        ``{"status": "success", "tex_path": ...}``
    """
    # --- 1.  Read template ------------------------------------------------
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tex = f.read()

    # --- 2.  Sanitise & inject -------------------------------------------
    for i, bullet in enumerate(tailored_bullets_list[:5], start=1):
        placeholder = f"[[BULLET{i}]]"
        tex = tex.replace(placeholder, escape_latex(bullet))

    # --- 3.  Clean company name for filename -----------------------------
    safe_company_name = re.sub(r'[^A-Za-z0-9_-]', '_', company_name)
    file_name = f"resume_{safe_company_name}.tex"

    # --- 4.  Write modified .tex -----------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tex_path = os.path.join(OUTPUT_DIR, file_name)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)

    print(f"[pdf_generator] Wrote modified template -> {tex_path}")
    
    return {"status": "success", "tex_path": tex_path}

# ======================================================================
# CLI entry-point
# ======================================================================

if __name__ == "__main__":
    test_bullets = [
        "Engineered a Python-based automation framework that reduced ticket resolution latency by 250%, saving approximately 40 engineering hours per week.",
        "Optimized complex SQL queries on MS SQL Server for datasets exceeding 10M+ rows, achieving a 40% improvement in query execution time.",
        "Designed & deployed 12+ automated SAP workflows using Python and ABAP, eliminating manual data entry for finance teams.",
        "Strengthened enterprise data security by conducting rigorous audit cycles, reducing system vulnerabilities by 25% across 3 SAP modules.",
        "Collaborated with a cross-functional team of 8 engineers across 3 time zones to deliver quarterly platform upgrades on schedule.",
    ]

    outcome = generate_pdf("TestCorp", test_bullets)
    print(f"\nResult: {outcome}")
