# Studio Rx

A chat agent for **Pilates instructors who teach clients with health conditions
or medications**.

A new client's intake form often says something like "takes metoprolol and
prednisone, has osteopenia." Most instructors don't know what that means for
their programming. Studio Rx reads the FDA label for each medication, flags
what matters in a Pilates session (dizziness when standing up, blunted heart
rate, tendon or bone risks), and builds a class plan that leaves out
exercises that conflict with the client's conditions.

> Studio Rx is a teaching aid, not medical advice. Medication findings are
> things to discuss with the client's healthcare provider.

## Tools

| Tool | What it does | Data |
| --- | --- | --- |
| `check_medication_exercise_flags(drug_name)` | Looks up the drug's FDA label and scans its warnings and adverse reactions for exercise-relevant risks. Returns each flag, the label text that triggered it, and the Pilates caution. | **External:** [openFDA drug label API](https://open.fda.gov/apis/drug/label/) |
| `build_class_plan(duration_min, level, equipment, focus, conditions)` | Sequences a warm-up, main block, and cool-down that fits the time, skipping exercises whose movement tags conflict with the client's conditions. | `exercises.py` library |
| `suggest_modification(exercise, reason)` | Returns regressions, props, and progressions for one exercise, matched to the reason (a condition or "too hard"). | `exercises.py` library |

`exercises.py` holds the domain data: about 35 mat and reformer exercises tagged
with movement properties (`spinal_flexion`, `inversion`, `wrist_loading`, ...),
14 conditions mapped to the tags they rule out, and the medication flag keywords
the label checker searches for.

The tools chain together. A medication flag such as "bone loss" from prednisone
points to the `osteoporosis` condition, which `build_class_plan` uses to drop
the Roll Up, Rolling Like a Ball, and Rollover.

## Sample queries

1. **My client takes metoprolol. Anything I should watch for in class?**
   It should call `check_medication_exercise_flags` and report slowed heart
   rate (use perceived exertion instead of heart rate) and dizziness.
2. **Plan a 45-minute beginner mat class for a client with osteopenia who takes prednisone.**
   It should check prednisone, then call `build_class_plan` with `osteoporosis`
   and return a plan with no loaded spinal flexion or rolling.
3. **The Hundred bothers her neck. What can she do instead?** (send in the same session as #2)
   It should remember the client and call `suggest_modification` for the
   Hundred with `neck_pain`, recommending the head-down Hundred, which also
   fits her osteopenia.

## Run locally

1. A GCP project with billing and the Vertex AI (Agent Platform) API enabled.
2. `gcloud auth application-default login`
3. `uv run app.py`, then open http://localhost:8000

## Project layout

- `app.py`: FastAPI server, the tool-calling loop, and in-memory sessions.
  `/chat` returns `response`, `session_id`, and `tool_calls` (name, args,
  and result of every call).
- `tools.py`: the tool functions, their JSON schemas (`TOOLS`), and `run_tool`.
- `exercises.py`: the exercise, condition, and medication-flag library.
- `index.html`: the chat UI, which shows each tool call as a collapsible card
  above the answer.
