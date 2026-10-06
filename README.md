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
| `check_medication_exercise_flags(drug_name)` | Looks up the drug's FDA label and returns the side effects that matter in class (dizziness, slowed heart rate, tendon or bone risks) with a Pilates caution for each. | **External:** [openFDA drug label API](https://open.fda.gov/apis/drug/label/) |
| `build_class_plan(duration_min, level, conditions)` | Picks mat exercises, in class order, that fit the time and level, and lists the ones skipped as unsafe for the client's conditions. | `exercises.py` |
| `suggest_modification(exercise)` | Returns a safer or easier version of one exercise and the conditions it isn't safe for. | `exercises.py` |

`exercises.py` holds the data: 22 mat exercises, each with a level, time, the
conditions it isn't safe for, and a modification, plus the side-effect words
the label checker looks for.

## Sample queries

1. **My client takes metoprolol. Anything I should watch for in class?**
   It should call `check_medication_exercise_flags` and report slowed heart
   rate (use perceived exertion instead of heart rate) and dizziness.
2. **Plan a 45-minute beginner mat class for a client with osteopenia.**
   It should call `build_class_plan` with `osteoporosis` and return a plan
   that skips the Hundred, Chest Lift, and other spinal-flexion exercises.
3. **The Hundred bothers her neck. What can she do instead?** (send in the same session as #2)
   It should remember the client and call `suggest_modification` for
   The Hundred, recommending keeping the head on the mat.

## Run locally

1. A GCP project with billing and the Vertex AI (Agent Platform) API enabled.
2. `gcloud auth application-default login`
3. `uv run app.py`, then open http://localhost:8000

## Project layout

- `app.py`: FastAPI server, the tool-calling loop, and in-memory sessions.
  `/chat` returns `response`, `session_id`, and `tool_calls` (name, args,
  and result of every call).
- `tools.py`: the tool functions, their JSON schemas (`TOOLS`), and `run_tool`.
- `exercises.py`: the exercises and medication side-effect words.
- `index.html`: the chat UI, which shows each tool call as a collapsible card
  above the answer.
