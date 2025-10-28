# Backend - LangGraph Agent API

This is the backend service for the LangGraph Agent Builder application. It provides RESTful APIs and WebSocket endpoints for creating, managing, and executing LangGraph agents.

## Features

- Dynamic creation of LangGraph agents based on user configurations
- Support for multiple LLM providers (OpenAI, Anthropic, etc.)
- RESTful API for agent management
- WebSocket support for real-time streaming
- Database persistence for agent configurations
- Virtual environment for dependency isolation

## Tech Stack

- **FastAPI**: Web framework for building APIs
- **LangGraph**: For creating and executing agent workflows
- **SQLite**: Default database for storing agent configurations
- **Python**: Programming language

## Setup

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables (optional):
   ```bash
   export OPENAI_API_KEY=your_openai_key
   export ANTHROPIC_API_KEY=your_anthropic_key
   ```

5. Run the application:
   ```bash
   python -m uvicorn main:app --reload
   ```

## API Endpoints

### Agent Management

- `POST /api/v1/agents` - Create a new agent
- `GET /api/v1/agents/{agent_id}` - Get agent information
- `DELETE /api/v1/agents/{agent_id}` - Delete an agent

### Agent Execution

- `POST /api/v1/agents/{agent_id}/execute` - Execute an agent with input
- `WebSocket /api/v1/agents/{agent_id}/stream` - Stream agent responses

## Development

To run both frontend and backend in development mode:

```bash
npm run dev
```

This will start both the React frontend and FastAPI backend concurrently.