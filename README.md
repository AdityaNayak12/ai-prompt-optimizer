# Prompt Advisor Monorepo

Production-grade monorepo containing the Chrome Extension frontend and the FastAPI backend for the **Prompt Advisor** application.

## Structure

```
├── apps/
│   ├── extension/     # React + TS + Vite Chrome Extension (MV3)
│   └── backend/       # FastAPI + Python 3.12 + Pydantic v2 Backend
├── package.json       # Root scripts and npm workspace config
└── README.md          # Project documentation
```

## Quick Start

### 1. Prerequisites
- **Node.js**: `v22` or higher (includes `npm v10`)
- **Python**: `3.12` or higher (includes `venv` module)

### 2. Setup Environment
Clone the repository and run the root setup script to bootstrap both the Python virtual environment and NPM workspace dependencies:

```bash
npm run setup
```

### 3. Set Up API Keys
Copy the example environment file for the backend and set your `GROQ_API_KEY`:

```bash
cp apps/backend/.env.example apps/backend/.env
```
Edit `apps/backend/.env` to configure your `GROQ_API_KEY`:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Running Locally
Start both the backend server and the extension watcher concurrently:

```bash
npm run dev
```

- **Backend**: Live-reloaded API server running at `http://localhost:8000`.
- **Extension**: Vite compiles files in watch mode to `apps/extension/dist/`.

### 5. Load Extension in Chrome
1. Open Chrome and go to `chrome://extensions/`.
2. Turn on **Developer mode** (top-right toggle).
3. Click **Load unpacked** (top-left button).
4. Select the `apps/extension/dist` directory from this project workspace.

---

## Shared API Contract Type Generation

If you modify request or response schemas in the Python backend (`apps/backend/app/schemas/contract.py`), regenerate the TypeScript interface typings in the extension by running:

```bash
npm run generate-types
```
This automatically exports the current OpenAPI schema from the FastAPI application and compiles it to `apps/extension/src/types/api.ts` using `openapi-typescript`.

---

## Code Quality & Testing

### Python Backend
Lint, format, and run unit tests for the backend application:
```bash
# Lint code using Ruff
npm run lint:backend

# Autoformat code using Ruff
npm run format:backend

# Run pytest unit test suite
npm run test:backend
```
