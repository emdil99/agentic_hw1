import json
import os
import uuid
from pathlib import Path

import litellm
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from tools import TOOLS, run_tool

# --- Config ---

SYSTEM_PROMPT = (
    "You are Studio Rx, an assistant for Pilates instructors whose clients have "
    "health conditions or take medications.\n"
    "- When the instructor mentions a medication, call check_medication_exercise_flags "
    "for each one before giving advice.\n"
    "- When asked for a class or session plan, call build_class_plan with the "
    "conditions the instructor has described.\n"
    "- When the instructor says an exercise is too hard, hurts, or doesn't suit a "
    "client, call suggest_modification.\n"
    "- Remember the client details shared earlier in the conversation and reuse them.\n"
    "- Base your answers on tool results, and use only exercises the tools return. "
    "If a tool returns an error, call it again with corrected arguments. Never write "
    "a plan or modification from your own knowledge when the tool call failed.\n"
    "- You are not a doctor. Present medication findings as things to discuss with "
    "the client's healthcare provider, not as medical advice.\n"
    "- Keep answers short and practical, formatted for reading at a glance."
)
MODEL = "vertex_ai/gemini-3.5-flash-lite"
MAX_TOOL_ROUNDS = 6

# --- The Harness ---


def run_agent(messages: list[dict]) -> tuple[str, list[dict]]:
    """Complete until the model answers without asking for a tool.

    Returns the final text and a record of every tool call made along the way.
    """
    tool_calls = []

    for _ in range(MAX_TOOL_ROUNDS):
        reply = litellm.completion(
            model=MODEL,
            vertex_location="global",
            messages=messages,
            tools=TOOLS,
        ).choices[0].message

        # Append assistant's reply (text, tool calls, or both) to the context.
        # model_dump() keeps it a plain dict: the raw object carries provider-specific
        # fields that trip Pydantic when LiteLLM re-serializes it next round.
        messages += [reply.model_dump()]

        if not reply.tool_calls:
            return reply.content or "(The model returned an empty answer.)", tool_calls

        # The harness, not the model, runs each tool and appends the result.
        # Every tool call must get a result, or the next round is rejected.
        for call in reply.tool_calls:
            try:
                args = json.loads(call.function.arguments or "{}")
                result = run_tool(call.function.name, args)
            except Exception as e:
                args = call.function.arguments
                result = json.dumps({"error": f"Tool {call.function.name} failed: {type(e).__name__}: {e}"})
            tool_calls += [{"name": call.function.name, "args": args, "result": result}]

            messages += [{"role": "tool", "tool_call_id": call.id, "content": result}]

    return "Sorry, I hit my tool-call limit before finishing.", tool_calls


# --- Session Store ---

# session_id -> list of messages. In-memory, single process.
sessions: dict[str, list] = {}

# --- FastAPI App ---

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    tool_calls: list[dict]


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "index.html")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Get or create the session
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    history = sessions[session_id]
    turn_start = len(history)

    # Append user's message to the context
    history += [{"role": "user", "content": request.message}]

    try:
        response, tool_calls = run_agent(history)
    except Exception as e:
        # Auth, billing, a model that is not running: show it in the chat, not as a 500.
        # Drop the half-finished turn so the session stays usable.
        del history[turn_start:]
        response, tool_calls = f"Model call failed: {type(e).__name__}: {str(e)[:300]}", []

    return ChatResponse(response=response, session_id=session_id, tool_calls=tool_calls)


@app.post("/clear")
def clear(session_id: str | None = None):
    sessions.pop(session_id, None)
    return {"status": "ok"}


if __name__ == "__main__":
    # Cloud Run sets PORT and needs 0.0.0.0; locally, stay on localhost:8000.
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if "PORT" in os.environ else "127.0.0.1"
    uvicorn.run(app, host=host, port=port)
