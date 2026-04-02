# Moot Court Tabulation System (MCTS)

A local-first tournament management platform for competitive moot court. Supports customizable rulesets, real-time judge scoring via a web portal, automated Swiss/random pairing with side rotation, elimination brackets, and PDF report generation.

## Tech Stack

- **Backend**: Python 3.12+ / FastAPI / SQLAlchemy 2.0 / SQLite
- **Frontend**: React 18 / TypeScript / Vite / TailwindCSS
- **Real-time**: WebSockets
- **PDF**: ReportLab
- **Network**: LAN server with optional ngrok tunneling

## Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd client && npm install && cd ..

# Run both servers (development)
# Terminal 1 – backend
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 – frontend
cd client && npm run dev
```

The admin UI is served at `http://localhost:5173`. Judges connect to the server's LAN IP (displayed in the admin dashboard) on port 8000.

## Project Layout

```
server/          Python backend (FastAPI)
  models/        SQLAlchemy ORM models
  schemas/       Pydantic request/response schemas
  api/           Route modules
  services/      Business logic (pairing, tabulation, PDF, email)
  ws/            WebSocket connection manager
client/          React frontend (Vite + TypeScript)
  src/pages/     Admin and Judge portal pages
  src/components Shared UI components
  src/api/       Typed API client
  src/types/     TypeScript interfaces
```

## Contact

- Santiago Galan
- santigalan04@gmail.com
- galansantiago@uchicago.edu
