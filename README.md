# Mech Agent - AI Agent Builder

Build and configure custom AI agents with advanced LangGraph capabilities. Select LLM providers, tools, and execution settings.

## Features

- **Multi-Provider Support**: OpenAI, Anthropic, Groq, and more
- **Agent Architectures**: ReAct, Plan & Execute, Reflection, and Custom Graphs
- **Tool Integration**: Tavily Search, Python REPL, Wikipedia, and more
- **Real-time Streaming**: Stream agent responses via WebSocket
- **Persistent Memory**: SQLite, PostgreSQL, and Redis support
- **Theme Toggling**: Light/dark mode support

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mech-agent
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the backend directory with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GROQ_API_KEY=your_groq_api_key
   SECRET_KEY=your_secret_key_for_encryption
   ```

### Running the Application

Start both frontend and backend concurrently:
```bash
npm run dev
```

Or run them separately:

**Frontend:**
```bash
cd frontend
npm run dev
```

**Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Supported LLM Providers

- **OpenAI**: GPT-4, GPT-3.5, and newer models
- **Anthropic**: Claude Sonnet, Opus, and Haiku models
- **Groq**: Llama 3, Mixtral, and other fast inference models
- **Google**: Gemini models
- **OpenRouter**: Access to multiple providers through a single API
- **Together AI**: Llama, Mistral, and other models
- And more...

## Usage

1. Navigate to the agent builder interface
2. Configure your agent:
   - Select an LLM provider and model
   - Choose an agent architecture
   - Set system prompt and temperature
   - Select tools to include
   - Configure memory and streaming options
3. Provide your API key for the selected provider
4. Create and test your agent

## API Endpoints

- `POST /api/v1/agents` - Create a new agent
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `DELETE /api/v1/agents/{agent_id}` - Delete an agent
- `POST /api/v1/agents/{agent_id}/execute` - Execute an agent
- `POST /api/v1/agents/{agent_id}/chat` - Chat with an agent
- `WebSocket /api/v1/agents/{agent_id}/stream` - Stream agent responses

## Development

### Frontend

Built with React, TypeScript, Vite, and shadcn/ui components.

### Backend

Built with FastAPI, LangGraph, and SQLAlchemy.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.