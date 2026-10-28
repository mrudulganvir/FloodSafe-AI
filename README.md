# FloodSafe AI 🌊

**AI-Based Flood Evacuation Route Planning and Risk-Aware Pathfinding System**

> ⚠️ **Academic Disclaimer:** This is an educational simulation project.
> It does NOT provide verified real-time flood data, real road-closure
> information, or guaranteed-safe evacuation routes. Never rely on this
> system during an actual emergency.

---

## Problem Statement

During flooding, the geographically shortest route to an evacuation shelter
may pass through flooded, blocked, or hazardous roads. Conventional shortest-
distance navigation does not account for such dynamic risks.

FloodSafe AI models a road network as a weighted graph and compares three
AI search algorithms — BFS, Greedy Best-First Search, and A* — to find
evacuation routes under user-defined simulated flood conditions.

---

## Features

- 🗺️ Interactive map (Leaflet + OpenStreetMap) with route overlays
- 🚧 Mark individual road segments as **blocked** or **risky**
- 🔄 Compare BFS, Greedy Best-First Search, and A* side by side
- 📊 Metrics panel: distance, risk cost, nodes explored, execution time
- 🎯 Pre-built sample scenarios (Bengaluru neighbourhood layout)
- 🔁 Reset hazards and re-run instantly
- 🗾 Optional: load a real OpenStreetMap road network (Milestone 7)

---

## Architecture

```
Browser (React + Leaflet)
        │  REST JSON (HTTP)
FastAPI Backend (Python)
        │
    ┌───┴───────────────┐
    │                   │
graph_service      algorithms/
hazard_service     ├── bfs.py
route_service      ├── greedy_best_first.py
                   └── astar.py
        │
  data/sample_graph.json   ← Bengaluru neighbourhood (offline)
  data/scenarios.json      ← Pre-built flood scenarios
```

---

## Folder Structure

```
FloodSafe/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api/
│   │   │   ├── routes.py        # /routes/compare endpoint
│   │   │   └── scenarios.py     # /scenarios endpoints
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response types
│   │   ├── services/
│   │   │   ├── graph_service.py
│   │   │   ├── hazard_service.py
│   │   │   └── route_service.py
│   │   ├── algorithms/
│   │   │   ├── bfs.py
│   │   │   ├── greedy_best_first.py
│   │   │   └── astar.py
│   │   └── data/
│   │       ├── sample_graph.json
│   │       └── scenarios.json
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   └── src/
│       ├── components/
│       ├── services/
│       ├── App.jsx
│       └── main.jsx
├── venv/                        # Python virtual environment (not in Git)
├── .gitignore
└── README.md
```

---

## Windows Installation

### Prerequisites (already on your machine)
- Python 3.12+
- Node.js v24+
- Git

### 1. Clone / open the project
```powershell
cd "c:\Users\heymr\OneDrive\Desktop\mruuuu\5th sem\ai\FloodSafe"
```

### 2. Activate the Python virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```
Your terminal prompt should now start with `(venv)`.

> If you see an error about execution policy, run once:
> `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Install backend packages (first time only)
```powershell
pip install -r backend\requirements.txt
```

### 4. Install frontend packages (first time only)
```powershell
cd frontend
npm install
cd ..
```

---

## Running the Application

### Backend (Terminal 1)
```powershell
.\venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload --port 8000
```
Visit: http://localhost:8000/docs — interactive API documentation

### Frontend (Terminal 2)
```powershell
cd frontend
npm run dev
```
Visit: http://localhost:5173 — the FloodSafe dashboard

---

## Running Tests
```powershell
.\venv\Scripts\Activate.ps1
cd backend
pytest tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health check |
| GET | `/api/scenarios` | List all sample scenarios |
| GET | `/api/scenarios/{id}` | Get a specific scenario |
| POST | `/api/routes/compare` | Compare algorithms on a graph |

### Example: Compare Routes
**POST** `/api/routes/compare`
```json
{
  "scenario_id": "bengaluru_2",
  "start_node": "N1",
  "destination_node": "N12",
  "hazards": {
    "blocked": [["N5", "N6"]],
    "risky":   [["N3", "N7"]]
  },
  "algorithms": ["bfs", "greedy", "astar"]
}
```

---

## Algorithm Explanations

### BFS (Breadth-First Search)
Explores all neighbours at the current hop distance before moving further.
Finds the path with the **fewest road segments**, not the shortest distance.

### Greedy Best-First Search
Always expands the node that looks closest to the destination (straight-line
distance). Fast but can miss optimal routes by following a misleading direction.

### A* Search
Combines real accumulated cost `g(n)` with a heuristic estimate `h(n)`.
Finds the **optimal cost path** when the heuristic never overestimates the
remaining cost (admissibility condition).

---

## Sample Scenarios

*(Filled in during Milestone 2 — Bengaluru neighbourhood graph)*

---

## Cost Model

```
traversal_cost(edge) =
    ∞              if edge is BLOCKED
    length_m + 500 if edge is RISKY      (500 m = simulation penalty)
    length_m       otherwise
```

The 500 m penalty is a simulation constant with no real-world safety meaning.

---

## Known Limitations

- Risk penalties are simulated values, not real flood probability data
- OpenStreetMap data is not real-time (not verified live road closures)
- BFS optimality is for hop count only, not physical distance
- The system is a demonstration tool, not a certified emergency system

---

## Attribution

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright),
available under the [Open Database License](https://opendatacommons.org/licenses/odbl/).

---

## Future Improvements

- Dijkstra's algorithm comparison
- Bidirectional A*
- Real-time flood data integration (via government APIs)
- Mobile-responsive layout
- Route export as GeoJSON / KML

---

*Built as an academic mini-project for the AI course, 5th Semester, Computer Engineering.*
