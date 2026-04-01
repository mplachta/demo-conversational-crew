# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the flow directly (entry point defined in pyproject.toml)
crewai run

# Interactive terminal chat (local, no deployment required)
uv run python terminal_chat.py

# Run automated multi-turn test
uv run python test_chat.py

# Generate flow diagram
uv run python -c "from src.conversational_routing.main import plot; plot()"

# Run Streamlit demo (requires deployed CrewAI Enterprise instance)
streamlit run demo_streamlit_poll/streamlit_app.py

# Run Flask webhook demo (requires deployed CrewAI Enterprise instance)
python demo_webhooks/app.py
```

## Environment Variables

Required in `.env`:
- `MODEL_FAMILY` — `gemini` (default), `vertex`, or `openai`
- `GEMINI_API_KEY` — when using `gemini` or `vertex` model families
- `MODEL` — optional override, defaults to `gemini/gemini-2.5-flash-lite`

## Architecture

### Core Flow (`src/conversational_routing/`)

The main entry point is `main.py`, which defines `ChatFlow` — a `@persist()`-decorated CrewAI Flow that maintains multi-turn conversation state via `ChatState` (Pydantic model).

**Flow routing logic:**
1. `@start` → `initial_processing` (no-op, triggers routing)
2. `@router` → `classify_message` uses an inline Agent to classify the message into `pleasantries`, `question`, or `non-chase-question`
3. `@listen` handlers branch to `answer_pleasantries`, `answer_question`, or `answer_non_chase_question`
4. `@listen(or_(...))` → `send_response` consolidates all branches and returns a JSON string with `{id, response, current_agent, classification}`

**Conversation persistence:** The `@persist()` decorator on `ChatFlow` enables multi-turn sessions. Pass `id` from a previous flow run's `state.id` into `inputs` to resume a conversation.

### AssistantCrew (`crews/assistant_crew/`)

Handles `question`-classified messages using a `benefits_expert_agent` backed by a PDF knowledge source (`knowledge/freedom_benefits.pdf`). The agent uses RAG with configurable embedders.

Model selection is done at import time via the `MODEL_FAMILY` env var — each model module in `models/` exports `llm` and `embedder_configuration`.

### Demo Frontends

| Directory | Description |
|---|---|
| `demo_streamlit_poll/` | Streamlit UI; polls CrewAI Enterprise `/kickoff` + `/status/{id}` endpoints |
| `demo_webhooks/` | Flask app with SSE; receives results via webhook from CrewAI Enterprise |
| `demo_slackbot/` | Slack Bolt app using Socket Mode; maps Slack threads to flow session IDs |

All three demos require a **deployed CrewAI Enterprise instance** and use the same API pattern: POST to `/kickoff` with `{current_message, id?}`, then retrieve the result.

### Knowledge Base

`knowledge/freedom_benefits.pdf` is the source document for the RAG-powered `AssistantCrew`. The `prepare_vecdb/` directory contains tooling for pre-building the vector database.
