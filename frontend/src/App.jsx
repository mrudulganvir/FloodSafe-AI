import React, { useState, useEffect } from 'react';
import MapView from './components/MapView';
import ControlPanel from './components/ControlPanel';
import ResultsCards from './components/ResultsCards';
import Legend from './components/Legend';
import { getScenarios, getScenarioDetails, compareRoutes } from './services/api';

export default function App() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState('sample_1');
  const [scenarioDetail, setScenarioDetail] = useState(null);

  const [startNode, setStartNode] = useState('N1');
  const [destinationNode, setDestinationNode] = useState('N12');
  const [selectedAlgorithms, setSelectedAlgorithms] = useState(['bfs', 'greedy', 'astar']);

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadInitial() {
      try {
        setError(null);
        const data = await getScenarios();
        setScenarios(data);
        if (data && data.length > 0) {
          setSelectedScenarioId(data[0].id);
        }
      } catch (err) {
        setError(`Unable to connect to backend: ${err.message}. Ensure backend is running at http://localhost:8000.`);
      }
    }
    loadInitial();
  }, []);

  useEffect(() => {
    if (!selectedScenarioId) return;
    async function loadScenario() {
      try {
        setError(null);
        setResults([]);
        const detail = await getScenarioDetails(selectedScenarioId);
        setScenarioDetail(detail);
        if (detail.default_start) setStartNode(detail.default_start);
        if (detail.default_destination) setDestinationNode(detail.default_destination);
      } catch (err) {
        setError(`Failed to load scenario ${selectedScenarioId}: ${err.message}`);
      }
    }
    loadScenario();
  }, [selectedScenarioId]);

  const handleCompare = async () => {
    if (!selectedScenarioId || !startNode || !destinationNode) return;
    try {
      setLoading(true);
      setError(null);
      const payload = {
        scenario_id: selectedScenarioId,
        start_node: startNode,
        destination_node: destinationNode,
        algorithms: selectedAlgorithms,
        hazards: scenarioDetail ? scenarioDetail.hazards : { blocked: [], risky: [] },
      };
      const response = await compareRoutes(payload);
      setResults(response.results || []);
    } catch (err) {
      setError(`Route planning error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAlgorithm = (algoId) => {
    setSelectedAlgorithms((prev) =>
      prev.includes(algoId) ? prev.filter((id) => id !== algoId) : [...prev, algoId]
    );
  };

  const handleSelectNodeFromMap = (nodeId, asRole) => {
    if (asRole === 'start') setStartNode(nodeId);
    else if (asRole === 'dest') setDestinationNode(nodeId);
    else {
      if (nodeId !== startNode) setDestinationNode(nodeId);
    }
  };

  const nodes = scenarioDetail?.graph?.nodes || [];
  const edges = scenarioDetail?.graph?.edges || [];
  const hazards = scenarioDetail?.hazards || { blocked: [], risky: [] };

  const totalEdges = edges.length;
  const blockedCount = (hazards.blocked || []).length;
  const riskyCount = (hazards.risky || []).length;
  const normalCount = Math.max(totalEdges - blockedCount - riskyCount, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* 1. Header / Navigation */}
      <header
        style={{
          backgroundColor: '#090d16',
          borderBottom: '1px solid #1e293b',
          padding: '14px 28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Subtle GIS/Route Icon */}
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#0d9488"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
            <line x1="9" y1="3" x2="9" y2="18" />
            <line x1="15" y1="6" x2="15" y2="21" />
          </svg>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
            <span style={{ fontSize: '18px', fontWeight: '700', letterSpacing: '-0.02em', color: '#f8fafc' }}>
              FloodSafe AI
            </span>
            <span style={{ fontSize: '13px', color: '#94a3b8', fontWeight: '400' }}>
              Flood-aware pathfinding simulation
            </span>
          </div>
        </div>

        <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>
          Bengaluru Road Network
        </div>
      </header>

      {/* 2. Main Content Container */}
      <main style={{ maxWidth: '1600px', width: '100%', margin: '0 auto', padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {error && (
          <div
            style={{
              backgroundColor: '#fef2f2',
              color: '#991b1b',
              padding: '12px 16px',
              borderRadius: '6px',
              border: '1px solid #fecaca',
              fontSize: '14px',
            }}
          >
            {error}
          </div>
        )}

        {/* Top Section: Sidebar + Map */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(320px, 360px) 1fr',
            gap: '24px',
            alignItems: 'stretch',
          }}
        >
          {/* Left Column: Sidebar Controls */}
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <ControlPanel
              scenarios={scenarios}
              selectedScenarioId={selectedScenarioId}
              onSelectScenario={setSelectedScenarioId}
              nodes={nodes}
              startNode={startNode}
              destinationNode={destinationNode}
              onChangeStart={setStartNode}
              onChangeDestination={setDestinationNode}
              selectedAlgorithms={selectedAlgorithms}
              onToggleAlgorithm={handleToggleAlgorithm}
              onCompare={handleCompare}
              loading={loading}
              hazardCounts={{ normal: normalCount, risky: riskyCount, blocked: blockedCount }}
            />
          </div>

          {/* Right Column: Interactive Map & Map Legend */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div
              style={{
                height: '560px',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                overflow: 'hidden',
                backgroundColor: '#e2e8f0',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
              }}
            >
              <MapView
                nodes={nodes}
                edges={edges}
                hazards={hazards}
                startNode={startNode}
                destinationNode={destinationNode}
                routes={results}
                onSelectNode={handleSelectNodeFromMap}
              />
            </div>

            <Legend />
          </div>
        </div>

        {/* Bottom Section: Comparison Metrics Cards */}
        <ResultsCards results={results} loading={loading} />
      </main>

      {/* 3. Discreet Footer */}
      <footer
        style={{
          marginTop: 'auto',
          padding: '20px 28px',
          textAlign: 'center',
          fontSize: '12px',
          color: '#64748b',
          borderTop: '1px solid #e2e8f0',
          backgroundColor: '#ffffff',
        }}
      >
        Academic simulation — flood hazards are simulated, not live data.
      </footer>
    </div>
  );
}
