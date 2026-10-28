import React from 'react';

export default function ControlPanel({
  scenarios = [],
  selectedScenarioId,
  onSelectScenario,
  nodes = [],
  startNode,
  destinationNode,
  onChangeStart,
  onChangeDestination,
  selectedAlgorithms = [],
  onToggleAlgorithm,
  onCompare,
  loading = false,
  hazardCounts = { normal: 0, risky: 0, blocked: 0 },
}) {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        padding: '24px',
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
        display: 'flex',
        flexDirection: 'column',
        gap: '22px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
      }}
    >
      {/* 1. Scenario Selection */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <label
          htmlFor="scenario-select"
          style={{
            fontSize: '13px',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#475569',
          }}
        >
          Flood Scenario
        </label>
        <select
          id="scenario-select"
          value={selectedScenarioId}
          onChange={(e) => onSelectScenario(e.target.value)}
          disabled={loading}
          style={{
            width: '100%',
            padding: '10px 12px',
            backgroundColor: '#f8fafc',
            color: '#0f172a',
            border: '1px solid #cbd5e1',
            borderRadius: '6px',
            fontSize: '14px',
            outline: 'none',
          }}
        >
          {scenarios.map((sc) => (
            <option key={sc.id} value={sc.id}>
              {sc.name}
            </option>
          ))}
        </select>
      </div>

      {/* 2. Route Origin & Shelter Destination */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label
            htmlFor="start-node-select"
            style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#1e3a8a',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: '#2563eb',
                display: 'inline-block',
              }}
            />
            Start Location
          </label>
          <select
            id="start-node-select"
            value={startNode}
            onChange={(e) => onChangeStart(e.target.value)}
            disabled={loading}
            style={{
              width: '100%',
              padding: '10px 12px',
              backgroundColor: '#f8fafc',
              color: '#0f172a',
              border: '1px solid #cbd5e1',
              borderRadius: '6px',
              fontSize: '14px',
              outline: 'none',
            }}
          >
            {nodes.map((n) => (
              <option key={`start-${n.id}`} value={n.id}>
                {n.id}: {n.label}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label
            htmlFor="dest-node-select"
            style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#14532d',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: '#15803d',
                display: 'inline-block',
              }}
            />
            Evacuation Shelter
          </label>
          <select
            id="dest-node-select"
            value={destinationNode}
            onChange={(e) => onChangeDestination(e.target.value)}
            disabled={loading}
            style={{
              width: '100%',
              padding: '10px 12px',
              backgroundColor: '#f8fafc',
              color: '#0f172a',
              border: '1px solid #cbd5e1',
              borderRadius: '6px',
              fontSize: '14px',
              outline: 'none',
            }}
          >
            {nodes.map((n) => (
              <option key={`dest-${n.id}`} value={n.id}>
                {n.id}: {n.label} {n.is_shelter ? '(Shelter)' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 3. Algorithm Selection */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <span
          style={{
            fontSize: '13px',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#475569',
          }}
        >
          Algorithms
        </span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {[
            { id: 'bfs', label: 'BFS (Fewest segments)', color: '#9333ea' },
            { id: 'greedy', label: 'Greedy (Heuristic search)', color: '#ea580c' },
            { id: 'astar', label: 'A* (Cost-optimal)', color: '#0d9488' },
          ].map((algo) => (
            <label
              key={algo.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                cursor: 'pointer',
                fontSize: '14px',
                color: '#334155',
                userSelect: 'none',
              }}
            >
              <input
                type="checkbox"
                checked={selectedAlgorithms.includes(algo.id)}
                onChange={() => onToggleAlgorithm(algo.id)}
                disabled={loading}
                style={{ width: '16px', height: '16px', accentColor: algo.color }}
              />
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span
                  style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '2px',
                    backgroundColor: algo.color,
                    display: 'inline-block',
                  }}
                />
                {algo.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* 4. Hazard Summary Strip */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '10px 14px',
          backgroundColor: '#f8fafc',
          borderRadius: '6px',
          border: '1px solid #e2e8f0',
          fontSize: '13px',
          color: '#475569',
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#64748b' }} />
          Open: <strong>{hazardCounts.normal || 0}</strong>
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#d97706' }} />
          Risky: <strong>{hazardCounts.risky || 0}</strong>
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#dc2626' }} />
          Blocked: <strong>{hazardCounts.blocked || 0}</strong>
        </span>
      </div>

      {/* 5. Compare Action Button */}
      <button
        onClick={onCompare}
        disabled={loading || selectedAlgorithms.length === 0}
        style={{
          width: '100%',
          padding: '12px 16px',
          backgroundColor: loading ? '#94a3b8' : '#0d9488',
          color: '#ffffff',
          border: 'none',
          borderRadius: '6px',
          fontSize: '15px',
          fontWeight: '600',
          transition: 'background-color 0.15s ease',
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
        }}
        onMouseEnter={(e) => {
          if (!loading) e.currentTarget.style.backgroundColor = '#0f766e';
        }}
        onMouseLeave={(e) => {
          if (!loading) e.currentTarget.style.backgroundColor = '#0d9488';
        }}
      >
        {loading ? 'Evaluating Paths...' : 'Compare Routes'}
      </button>
    </div>
  );
}
