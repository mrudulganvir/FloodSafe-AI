# FloodSafe AI 🌊
### AI-Based Flood Evacuation Route Planning

Flooding can turn an ordinary road into a dangerous one. The shortest route to a shelter isn't always the best option when some roads are blocked or risky.

**FloodSafe AI** is a web-based project that explores how different AI search algorithms can help find routes through a road network under simulated flood conditions. It lets you change the scenario, choose a starting point and destination, and compare the routes suggested by BFS, Greedy Best-First Search, and A*.

## What can you do with it?

- View a road network on an interactive map.
- Try different flood scenarios based on a sample Bengaluru neighbourhood.
- Mark roads as blocked or risky where supported by the interface.
- Compare the routes found by BFS, Greedy Best-First Search, and A*.
- View route details such as distance, cost, explored nodes, and execution time.
- See how changing road conditions affects the route each algorithm finds.

## Built with

| Part | Technologies |
|---|---|
| Frontend | React, Vite, Leaflet |
| Map data | OpenStreetMap |
| Backend | Python, FastAPI |
| Pathfinding | BFS, Greedy Best-First Search, A* |
| Graph handling | NetworkX |
| Testing | pytest |

## How it works

The road network is represented as a graph: intersections are nodes, and roads connecting them are edges. Each road has a length and can be affected by a simulated hazard.

When you select a starting point, destination, and flood scenario, the backend runs the selected algorithms and returns their routes and performance metrics. The frontend displays the results on the map so you can compare how each algorithm behaves.

### The algorithms

**Breadth-First Search (BFS)**

BFS explores the graph level by level and finds a path with the fewest road segments. It doesn't necessarily find the route with the least physical distance or risk-adjusted cost.

**Greedy Best-First Search**

Greedy search uses a heuristic to prioritise nodes that appear closer to the destination. It can find a route quickly, but it doesn't guarantee the lowest-cost route.

**A* Search**

A* considers both the cost accumulated so far and an estimate of the cost remaining. With a suitable admissible heuristic and the project's cost model, it can find a minimum-cost route.

## How road hazards affect routing

The project uses a simple cost model to represent road conditions:

| Road condition | Effect |
|---|---|
| Normal | Cost equals the road length |
| Risky | Road length plus a simulated 500 m penalty |
| Blocked | Road cannot be used |

The 500 m penalty is only a value chosen for this simulation. It does not represent a real measurement of flood danger.

## Project structure

```text
FloodSafe/
├── backend/
│   ├── app/
│   │   ├── algorithms/     # BFS, Greedy and A*
│   │   ├── api/            # API endpoints
│   │   ├── data/           # Road graph and scenarios
│   │   ├── models/         # Request and response models
│   │   ├── services/       # Graph, hazard and route logic
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Getting started

### Requirements

- Python 3.12 or later
- Node.js and npm
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/mrudulganvir/FloodSafe-AI.git
cd FloodSafe-AI
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Set up the backend

Create and activate a virtual environment from the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
pip install -r backend\requirements.txt
```

Start the backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
You can explore its interactive documentation at `http://localhost:8000/docs`.

### 3. Set up the frontend

Open a **second terminal** in the project root and run:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

Keep both terminals running while using the application.

## Running the tests

From the project root, activate the virtual environment if it isn't already active, then run:

```powershell
cd backend
python -m pytest tests/ -v
```

The tests cover the search algorithms, graph handling, route comparison, and API behaviour.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check whether the backend is running |
| GET | `/api/scenarios` | List available scenarios |
| GET | `/api/scenarios/{id}` | Get details for a scenario |
| POST | `/api/routes/compare` | Compare selected algorithms |

## Current limitations

- Flood conditions and road hazards are simulated.
- The sample road network is not a verified live map of road conditions.
- The system does not receive confirmed real-time flood warnings or road closures.
- BFS minimises the number of edges, not physical distance or risk-adjusted cost.
- A route returned by the application is not a guarantee of safety.

## Possible future improvements

- Compare additional algorithms, such as Dijkstra's algorithm.
- Add more road networks and flood scenarios.
- Explore integration with reliable, verified live hazard data.
- Add route export options such as GeoJSON.

## Credits

Map data and map services are provided by [OpenStreetMap](https://www.openstreetmap.org/copyright). OpenStreetMap data is available under the Open Database License (ODbL).

