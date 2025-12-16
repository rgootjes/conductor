# Run Guide

This guide explains the prerequisites and steps to run the Conductor backend and frontend locally.

## Prerequisites

- **Python**: 3.11+ (for the FastAPI backend)
- **Node.js**: 18+ (for the Next.js frontend)
- **Package managers**: `pip` for Python and `npm` for Node.js

## Backend (FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```
4. Run the development server from the `src` directory:
   ```bash
   cd src
   uvicorn main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000` by default.

## Frontend (Next.js)
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`.

## Running Both Together
- Start the backend server first to ensure the frontend can communicate with it.
- Keep both terminals running while developing to see live updates.
- If ports `8000` (backend) or `3000` (frontend) are in use, configure alternative ports using `uvicorn --port <port>` or `npm run dev -- --port <port>`.

## Troubleshooting
- If you encounter missing dependencies, ensure you are using the correct Python/Node.js versions.
- For virtual environment issues on Windows, replace the activation command with `\.venv\\Scripts\\activate`.
- Use `npm run lint` in `frontend` to check for linting issues and ensure TypeScript types compile.
