# Backend - LangGraph Agent API

FastAPI backend for the AI Agent Builder with LangGraph integration.

## Features

- REST API for agent management
- LangGraph integration for complex agent workflows
- Support for multiple LLM providers (OpenAI, Anthropic, Groq)
- Encrypted storage of user API keys
- WebSocket streaming support
- SQLite database for persistence

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GROQ_API_KEY=your_groq_api_key
   SECRET_KEY=your_secret_key_for_encryption
   ```

## Running the Server

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/v1/agents` - Create a new agent
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `DELETE /api/v1/agents/{agent_id}` - Delete an agent
- `POST /api/v1/agents/{agent_id}/execute` - Execute an agent
- `POST /api/v1/agents/{agent_id}/chat` - Chat with an agent
- `WebSocket /api/v1/agents/{agent_id}/stream` - Stream agent responses

## Supported LLM Providers

The backend currently supports the following LLM providers:

1. **OpenAI**: Uses `langchain-openai` integration
2. **Anthropic**: Uses `langchain-anthropic` integration
3. **Groq**: Uses `langchain-groq` integration for fast inference

To use any provider, you need to set the corresponding API key in your environment variables.

## Database

The application uses SQLite for data persistence. The database is automatically initialized when you run the application.

To initialize the database manually:
```bash
python init_db.py
```

## Testing

Run the test suite:
```bash
python -m pytest
```

Run specific tests:
```bash
python test_agent_service.py
python test_chat.py
python test_db.py
python test_encryption.py
python test_retrieve.py
```

## Security

- User API keys are encrypted before storage using Fernet symmetric encryption
- Each agent uses the user's decrypted API key for LLM initialization
- The SECRET_KEY environment variable is used for encryption (default provided for development)

## Extending Providers

To add support for additional LLM providers:

1. Add the provider's langchain integration to `requirements.txt`
2. Update the `_initialize_llm` method in `services/agent_service.py`
3. Add the provider to the frontend's `LLM_PROVIDERS` list
4. Add appropriate models to the frontend's `MODELS` configuration
5. Add the API key environment variable to `core/config.py`