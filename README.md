# CrewAI Enterprise Chatbot

This project demonstrates a CrewAI flow for building chatbots with CrewAI Enterprise. It integrates a single crew/agent to handle conversational routing and a Streamlit-based chatbot interface for demonstration purposes.

## Project Overview

The project includes:

- A CrewAI flow with a configured crew/agent for handling chat messages.
- A Streamlit app (`demo/streamlit_app.py`) that provides an interactive chatbot interface.
- Backend API endpoints that showcase CrewAI Enterprise functionalities.

## Installation

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd demo-conversational-crew
   ```

2. Install dependencies:

   ```bash
   crewai install
   ```

   or

   ```bash
   uv sync
   ```

3. Configure all required environment variables in `.env` file.

## Usage

### Running the Terminal Chat

A script named `terminal_chat.py` is provided to run a terminal-based chat session. To run it, execute:

```bash
.venv/bin/python terminal_chat.py
```

This script demonstrates how to interact with the CrewAI flow through the terminal.

### Running the Streamlit Chatbot

**Your crew needs to be deployed to CrewAI Enterprise for this demo to work.**

To launch the interactive chatbot demo using Streamlit, run:

For secure handling of your crew URLs and API keys, this project uses `secrets.toml`. 
Follow these steps to set up your environment:

1. Create a `secrets.toml` file in the `.streamlit` directory:

   ```bash
   mkdir -p demo/.streamlit && touch demo/.streamlit/secrets.toml
   ```

2. Add your environment variables to `secrets.toml`:

   ```toml
   # demo/.streamlit/secrets.toml
   base_url = "https://YOUR-CREWAI-DEPLOYMENT-URL.crewai.com"
   bearer_token = "YOUR-BEARER-TOKEN-HERE"
   # Add any other necessary environment variables
   ```

3. Ensure `secrets.toml` is listed in your `.gitignore` file to prevent accidental commits of sensitive information.

When deploying to production, use the appropriate method for your hosting platform to set these environment variables securely.

```bash
streamlit run demo/streamlit_app.py
```

### Run some automated tests

You can run some automated tests with two consecutive messages by executing:

```bash
.venv/bin/python test_chat.py
```

## API Calls

The project utilizes CrewAI Enterprise API calls to manage chat sessions and process messages. Key API interactions include:

- **Initiating a Chat Session:** A POST request is sent to the designated endpoint with a JSON payload specifying the chat context, starting the conversation.

- **Processing Chat Messages:** User inputs are routed through the configured crew/agent. API calls handle routing, processing, and returning responses in a structured format.

For detailed implementation, review the configuration files in `src/conversational_routing/crews/assistant_crew/config/` and the Crew files.

The API is a standard CrewAI Enterprise API, so refer to the [CrewAI Enterprise API documentation](https://help.crewai.com/using-your-crews-api-in-crewai) for more information.

The first message sends the following JSON payload to the `/kickoff` endpoint:

```json
{
    "current_message": "Hello, I am a chatbot. How can I help you today?"
}
```

In response, the API will respond with a `kickoff_id`:

```json
{
    "id": "UNIQUE-KICKOFF-ID"
}
```

In order to get the chatbot response, keep polling the `/status/{kickoff_id}` endpoint. The response will include the `response` and `id` fields.

```json
{
    "state": "SUCCESS",
    "result": "{ \"response\": \"Assistant response here.\", \"id\": \"UNIQUE-CONVERSATION-ID\" }"
}
```

The Crew is using [@persist](https://docs.crewai.com/concepts/flows#flow-persistence) to store the conversation history and uses `UNIQUE-CONVERSATION-ID` as a key.

Consecutive messages should be sent to the `/kickoff` endpoint with the following payload:

```json
{
    "current_message": "I need help with something.",
    "id": "UNIQUE-CONVERSATION-ID"
}
```

## Additional Information

- Verify that any required environment variables are set.
- Check the source code for additional comments and developer notes regarding API endpoints and operation.
- Contributions and issues are welcome. Feel free to open a pull request or issue on the repository.