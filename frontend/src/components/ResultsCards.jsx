import React from 'react';
import { ALGO_COLORS } from './MapView';

export default function ResultsCards({ results = [], loading = false }) {
  if (loading) {
    return (
      <div
        style={{
          padding: '32px',
          textAlign: 'center',
          backgroundColor: '#ffffff',
          borderRadius: '8px',
          border: '1px solid #e2e8f0',
          color: '#64748b',
          fontSize: '15px',
        }}
      >
        Running selected search algorithms...
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div
        style={{
          padding: '24px',
          textAlign: 'center',
          backgroundColor: '#ffffff',
          borderRadius: '8px',
          border: '1px solid #e2e8f0',
          color: '#64748b',
          fontSize: '14px',
        }}
      >
        Configure your parameters and click <strong>Compare Routes</strong> to evaluate algorithm performance.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0f172a', margin: 0 }}>
          Algorithm Comparison
        </h2>
        <span style={{ fontSize: '13px', color: '#64748b' }}>
          {results.length} algorithm{results.length > 1 ? 's' : ''} evaluated
        </span>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))',
          gap: '16px',
        }}
      >
        {results.map((res) => {
          const algoKey = res.algorithm.toLowerCase();
          const themeColor = ALGO_COLORS[algoKey] || '#0d9488';
          const hopCount = res.path_node_ids ? Math.max(res.path_node_ids.length - 1, 0) : 0;

          return (
            <div
              key={res.algorithm}
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                borderTop: `4px solid ${themeColor}`,
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
              }}
            >
              {/* Card Header */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  paddingBottom: '12px',
                  borderBottom: '1px solid #f1f5f9',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span
                    style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '50%',
                      backgroundColor: themeColor,
                      display: 'inline-block',
                    }}
                  />
                  <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '700', color: '#0f172a', textTransform: 'uppercase' }}>
                    {res.algorithm}
                  </h3>
                </div>

                <span
                  style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    backgroundColor: res.found ? '#f0fdf4' : '#fef2f2',
                    color: res.found ? '#15803d' : '#b91c1c',
                    border: `1px solid ${res.found ? '#bbf7d0' : '#fecaca'}`,
                  }}
                >
                  {res.found ? 'Route Found' : 'No Route'}
                </span>
              </div>

              {/* Metrics Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                }}
              >
                <div style={{ backgroundColor: '#f8fafc', padding: '10px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>Total Cost</div>
                  <div style={{ fontSize: '18px', fontWeight: '700', color: themeColor, marginTop: '2px' }}>
                    {res.found ? `${res.total_cost} m` : '—'}
                  </div>
                </div>

                <div style={{ backgroundColor: '#f8fafc', padding: '10px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>Distance</div>
                  <div style={{ fontSize: '18px', fontWeight: '700', color: '#0f172a', marginTop: '2px' }}>
                    {res.found ? `${res.total_distance_m} m` : '—'}
                  </div>
                </div>

                <div style={{ backgroundColor: '#f8fafc', padding: '10px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>Hops (Segments)</div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#1e293b', marginTop: '2px' }}>
                    {res.found ? `${hopCount} hops` : '—'}
                  </div>
                </div>

                <div style={{ backgroundColor: '#f8fafc', padding: '10px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>Risk Penalty</div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: res.total_risk_penalty > 0 ? '#d97706' : '#64748b', marginTop: '2px' }}>
                    {res.found ? `+${res.total_risk_penalty} m` : '—'}
                  </div>
                </div>

                <div style={{ backgroundColor: '#f8fafc', padding: '10px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>Explored Nodes</div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#1e293b', marginTop: '2px' }}>
                    {res.nodes_explored}
                  </div>
                </div>

                <div style={{ backgroundColor: '#f8fafc', padding: '10px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>Runtime</div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#1e293b', marginTop: '2px' }}>
                    {res.time_ms} ms
                  </div>
                </div>
              </div>

              {/* Compact Path Sequence */}
              {res.found && res.path_node_ids && res.path_node_ids.length > 0 && (
                <div
                  style={{
                    padding: '8px 10px',
                    backgroundColor: '#f8fafc',
                    borderRadius: '6px',
                    border: '1px solid #f1f5f9',
                    fontSize: '13px',
                  }}
                >
                  <span style={{ fontWeight: '600', color: '#475569', marginRight: '6px' }}>Path:</span>
                  <span
                    style={{
                      fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
                      color: '#0f172a',
                      fontWeight: '500',
                      wordBreak: 'break-word',
                    }}
                  >
                    {res.path_node_ids.join(' → ')}
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
