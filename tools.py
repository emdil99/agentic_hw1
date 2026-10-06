"""The tools the harness can run, and the JSON that describes them to the model."""

import json

import requests

from exercises import EXERCISES, MEDICATION_FLAGS

# openFDA is free and needs no API key.
DRUG_API = "https://api.fda.gov/drug/label.json"

LEVELS = ["beginner", "intermediate", "advanced"]
CONDITIONS = sorted({c for ex in EXERCISES.values() for c in ex["avoid_for"]})


def check_medication_exercise_flags(drug_name: str) -> str:
    """Look up a drug's FDA label and flag warnings that matter in a Pilates class."""
    try:
        search = f'openfda.generic_name:"{drug_name}" openfda.brand_name:"{drug_name}"'
        data = requests.get(DRUG_API, params={"search": search, "limit": 1}, timeout=10).json()
    except requests.RequestException as e:
        # The model cannot see an exception. Return something it can reason about.
        return json.dumps({"error": f"FDA label service failed: {e}"})

    if not data.get("results"):
        return json.dumps({"error": f"No FDA label found for '{drug_name}'. Try the generic name."})
    label = data["results"][0]

    text = " ".join(label.get("warnings_and_cautions", []) + label.get("warnings", []) + label.get("adverse_reactions", []))
    flags = {word: caution for word, caution in MEDICATION_FLAGS.items() if word in text.lower()}

    return json.dumps({"drug": drug_name, "flags": flags})


def build_class_plan(duration_min: int, level: str = "beginner", conditions: list[str] | None = None) -> str:
    """Pick exercises, in class order, that fit the time and are safe for the client."""
    conditions = conditions or []
    if level not in LEVELS:
        return json.dumps({"error": f"Unknown level '{level}'. Use one of {LEVELS}."})
    unknown = [c for c in conditions if c not in CONDITIONS]
    if unknown:
        return json.dumps({"error": f"Unknown conditions {unknown}. Use any of {CONDITIONS}."})

    plan, skipped, total = [], [], 0
    for name, ex in EXERCISES.items():
        if LEVELS.index(ex["level"]) > LEVELS.index(level):
            continue
        if set(ex["avoid_for"]) & set(conditions):
            skipped += [name]
        elif total + ex["minutes"] <= duration_min:
            plan += [name]
            total += ex["minutes"]

    return json.dumps({"plan": plan, "total_minutes": total, "skipped_as_unsafe": skipped})


def suggest_modification(exercise: str) -> str:
    """Return a safer or easier version of one exercise."""
    match = next((name for name in EXERCISES if name.lower() == exercise.lower()), None)
    if not match:
        return json.dumps({"error": f"Unknown exercise '{exercise}'. Use one of {list(EXERCISES)}."})

    ex = EXERCISES[match]
    return json.dumps({"exercise": match, "modification": ex["modification"], "avoid_for": ex["avoid_for"]})


# What the model sees: the "set notes" in the screenplay.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_medication_exercise_flags",
            "description": "Check one medication's FDA label for side effects that matter in a Pilates class.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "Generic or brand name, e.g. 'metoprolol'"},
                },
                "required": ["drug_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_class_plan",
            "description": "Build a Pilates mat class that fits the time and skips exercises unsafe for the client's conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration_min": {"type": "integer", "description": "Class length in minutes, e.g. 45"},
                    "level": {"type": "string", "enum": LEVELS, "description": "Client level"},
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string", "enum": CONDITIONS},
                        "description": "The client's conditions, if any",
                    },
                },
                "required": ["duration_min"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_modification",
            "description": "Get a safer or easier version of one Pilates exercise.",
            "parameters": {
                "type": "object",
                "properties": {
                    "exercise": {"type": "string", "description": f"One of: {', '.join(EXERCISES)}"},
                },
                "required": ["exercise"],
            },
        },
    },
]

# What the harness runs: tool name -> Python function.
TOOL_MAP = {
    "check_medication_exercise_flags": check_medication_exercise_flags,
    "build_class_plan": build_class_plan,
    "suggest_modification": suggest_modification,
}


def run_tool(name: str, args: dict) -> str:
    """Run one tool call. Models invent tool names and arguments; never let that crash the loop."""
    if name not in TOOL_MAP:
        return json.dumps({"error": f"Unknown tool '{name}'. Available: {list(TOOL_MAP)}"})
    try:
        return TOOL_MAP[name](**args)
    except TypeError as e:
        return json.dumps({"error": f"Bad arguments for {name}: {e}"})
