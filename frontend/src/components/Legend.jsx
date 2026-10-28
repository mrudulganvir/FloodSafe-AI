import React from 'react';
import { ALGO_COLORS } from './MapView';

export default function Legend() {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        padding: '12px 18px',
        borderRadius: '6px',
        border: '1px solid #e2e8f0',
        fontSize: '13px',
        color: '#334155',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '20px',
        alignItems: 'center',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}
    >
      <span style={{ fontWeight: '600', color: '#0f172a', marginRight: '4px' }}>Legend:</span>

      {/* Nodes */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: '#2563eb',
            border: '2px solid #bfdbfe',
            display: 'inline-block',
          }}
        />
        <span>Start Origin</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: '#15803d',
            border: '2px solid #bbf7d0',
            display: 'inline-block',
          }}
        />
        <span>Shelter</span>
      </div>

      {/* Roads */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            width: '20px',
            height: '3px',
            backgroundColor: '#64748b',
            display: 'inline-block',
          }}
        />
        <span>Normal Road</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            width: '20px',
            height: '3px',
            backgroundColor: '#d97706',
            display: 'inline-block',
          }}
        />
        <span>Risky Road</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            width: '20px',
            height: '3px',
            borderTop: '2px dashed #dc2626',
            display: 'inline-block',
          }}
        />
        <span>Blocked Road</span>
      </div>

      {/* Algorithms */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            width: '18px',
            height: '4px',
            backgroundColor: ALGO_COLORS.bfs,
            display: 'inline-block',
            borderRadius: '2px',
          }}
        />
        <span>BFS</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            width: '18px',
            height: '4px',
            backgroundColor: ALGO_COLORS.greedy,
            display: 'inline-block',
            borderRadius: '2px',
          }}
        />
        <span>Greedy</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            width: '18px',
            height: '4px',
            backgroundColor: ALGO_COLORS.astar,
            display: 'inline-block',
            borderRadius: '2px',
          }}
        />
        <span>A* Optimal</span>
      </div>
    </div>
  );
}
