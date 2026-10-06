import json
import os

import requests

from exercises import LABEL_SECTIONS, MEDICATION_FLAGS

# openFDA drug labels. Free; an optional key (env var) raises the daily limit.
DRUG_API = "https://api.fda.gov/drug/label.json"
OPENFDA_API_KEY = os.environ.get("OPENFDA_API_KEY")


def check_medication_exercise_flags(drug_name: str) -> str:
    """Look up a drug's FDA label and flag warnings that matter in a Pilates session."""
    drug_name = drug_name.strip().replace('"', "")
    if not drug_name:
        return json.dumps({"error": "drug_name is empty. Pass one medication name, e.g. 'metoprolol'."})

    # Match the generic or the brand name (a space between terms means OR)
    params = {
        "search": f'openfda.generic_name:"{drug_name}" openfda.brand_name:"{drug_name}"',
        "limit": 1,
    }
    if OPENFDA_API_KEY:
        params["api_key"] = OPENFDA_API_KEY

    try:
        data = requests.get(DRUG_API, params=params, timeout=10).json()
    except requests.RequestException as e:
        # The model cannot see an exception. Return something it can reason about.
        return json.dumps({"error": f"FDA label service failed: {e}. Try again shortly."})

    # openFDA answers "no match" with an error object instead of an empty list
    error = data.get("error", {})
    if error.get("code") == "NOT_FOUND" or (not error and not data.get("results")):
        return json.dumps({
            "error": f"No FDA label found for '{drug_name}'. Check the spelling, try the "
            "generic name (e.g. 'atorvastatin' for Lipitor), and look up one drug at a time."
        })
    if error:
        return json.dumps({"error": f"FDA label service error: {error.get('message', error)}. Try again shortly."})

    label = data["results"][0]
    text = " ".join(" ".join(label.get(section, [])) for section in LABEL_SECTIONS)
    lowered = text.lower()

    # Each flag fires on its first matching keyword; quote the label around it as evidence
    flags = []
    for flag in MEDICATION_FLAGS:
        for keyword in flag["keywords"]:
            i = lowered.find(keyword)
            if i != -1:
                flags += [{
                    "flag": flag["flag"],
                    "matched": keyword,
                    "label_excerpt": "..." + " ".join(text[max(0, i - 120):i + 180].split()) + "...",
                    "pilates_caution": flag["pilates_caution"],
                    "plan_around_conditions": flag["related_conditions"],
                }]
                break

    return json.dumps({
        "drug": drug_name,
        "matched_label": {
            "generic_name": label.get("openfda", {}).get("generic_name", []),
            "brand_name": label.get("openfda", {}).get("brand_name", []),
        },
        "flags": flags,
        "summary": f"{len(flags)} exercise-relevant flag(s) found." if flags
        else "No exercise-relevant warnings found in this label.",
        "note": "From the FDA label, not medical advice. Discuss concerns with the client's provider.",
    })



def build_class_plan(duration_min, level, equipment, focus, conditions):
    """ build class exercise sequence"""


def suggest_modification(exercise, reason):
    """ suggest exercise modification"""





"""The tools the harness can run, and the JSON that describes them to the model."""


# What the model sees: the "set notes" in the screenplay.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_medication_exercise_flags",
            "description": (
                "Look up one medication's FDA label and flag warnings that matter in a Pilates "
                "session (dizziness, slowed heart rate, low blood sugar, tendon or bone risks, "
                "bleeding, drowsiness, muscle pain). Returns each flag with the label excerpt "
                "that triggered it, a Pilates caution, and conditions to pass to build_class_plan. "
                "Call once per medication."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {
                        "type": "string",
                        "description": "One medication, generic or brand name, without dose, e.g. 'metoprolol' or 'Lipitor'.",
                    },
                },
                "required": ["drug_name"],
            },
        },
    },
]

# What the harness runs: tool name -> Python function.
TOOL_MAP = {"check_medication_exercise_flags": check_medication_exercise_flags}


def run_tool(name: str, args: dict) -> str:
    """Run one tool call. Models invent tool names and arguments; never let that crash the loop."""
    if name not in TOOL_MAP:
        return json.dumps({"error": f"Unknown tool '{name}'. Available: {list(TOOL_MAP)}"})
    try:
        return TOOL_MAP[name](**args)
    except TypeError as e:
        return json.dumps({"error": f"Bad arguments for {name}: {e}"})
