import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet's default marker icons in bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

function createNodeIcon(nodeId, type) {
  let cssClass = 'custom-node-icon node-normal';
  if (type === 'start') cssClass = 'custom-node-icon node-start';
  else if (type === 'shelter') cssClass = 'custom-node-icon node-shelter';

  return L.divIcon({
    className: cssClass,
    html: `<span>${nodeId}</span>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
}

export const ALGO_COLORS = {
  bfs: '#9333ea',    // Clear Purple
  greedy: '#ea580c', // Warm Amber/Orange
  astar: '#0d9488',  // Refined Teal
};

export default function MapView({
  nodes = [],
  edges = [],
  hazards = { blocked: [], risky: [] },
  startNode,
  destinationNode,
  routes = [],
  onSelectNode,
}) {
  const defaultCenter = [12.948, 77.625];
  const defaultZoom = 13;

  const nodeMap = React.useMemo(() => {
    const map = {};
    nodes.forEach((n) => {
      map[n.id] = [n.lat, n.lon];
    });
    return map;
  }, [nodes]);

  const hazardStatus = React.useMemo(() => {
    const blockedSet = new Set(
      (hazards.blocked || []).map(([u, v]) => `${u}-${v}`).concat(
        (hazards.blocked || []).map(([u, v]) => `${v}-${u}`)
      )
    );
    const riskySet = new Set(
      (hazards.risky || []).map(([u, v]) => `${u}-${v}`).concat(
        (hazards.risky || []).map(([u, v]) => `${v}-${u}`)
      )
    );
    return { blockedSet, riskySet };
  }, [hazards]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ width: '100%', height: '100%', minHeight: '520px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Base Road Network Edges */}
        {edges.map((edge) => {
          const fromCoords = nodeMap[edge.from];
          const toCoords = nodeMap[edge.to];
          if (!fromCoords || !toCoords) return null;

          const key = `${edge.from}-${edge.to}`;
          const isBlocked = hazardStatus.blockedSet.has(key);
          const isRisky = hazardStatus.riskySet.has(key);

          let color = '#64748b'; // Slate 500
          let weight = 3.5;
          let dashArray = null;

          if (isBlocked) {
            color = '#dc2626'; // Red
            weight = 4.5;
            dashArray = '6, 8';
          } else if (isRisky) {
            color = '#d97706'; // Amber
            weight = 4.5;
          }

          return (
            <Polyline
              key={edge.id || key}
              positions={[fromCoords, toCoords]}
              pathOptions={{ color, weight, dashArray, opacity: 0.85 }}
            >
              <Tooltip sticky>
                <div style={{ fontSize: '13px', lineHeight: 1.4 }}>
                  <span style={{ fontWeight: '600' }}>{edge.label || `${edge.from} ↔ ${edge.to}`}</span><br />
                  Distance: {edge.length_m} m<br />
                  Condition: {isBlocked ? 'Blocked (Flooded)' : isRisky ? 'Risky (+500m penalty)' : 'Open / Normal'}
                </div>
              </Tooltip>
            </Polyline>
          );
        })}

        {/* Algorithm Route Polylines */}
        {routes.map((route, idx) => {
          if (!route.found || !route.path_coords || route.path_coords.length < 2) return null;
          const color = ALGO_COLORS[route.algorithm.toLowerCase()] || '#0d9488';
          const offsetWeight = 6 - idx * 1.5;

          return (
            <Polyline
              key={`route-${route.algorithm}-${idx}`}
              positions={route.path_coords}
              pathOptions={{
                color,
                weight: Math.max(offsetWeight, 3.5),
                opacity: 0.95,
              }}
            >
              <Tooltip sticky>
                <div style={{ fontSize: '13px', lineHeight: 1.4 }}>
                  <span style={{ fontWeight: '600', color }}>{route.algorithm.toUpperCase()} Route</span><br />
                  Hops: {route.path_node_ids.length - 1}<br />
                  Total Cost: {route.total_cost} m<br />
                  Physical Distance: {route.total_distance_m} m
                </div>
              </Tooltip>
            </Polyline>
          );
        })}

        {/* Node Markers */}
        {nodes.map((node) => {
          let nodeType = 'normal';
          if (node.id === startNode) nodeType = 'start';
          else if (node.id === destinationNode || node.is_shelter) nodeType = 'shelter';

          const icon = createNodeIcon(node.id, nodeType);

          return (
            <Marker
              key={node.id}
              position={[node.lat, node.lon]}
              icon={icon}
              eventHandlers={{
                click: () => {
                  if (onSelectNode) onSelectNode(node.id);
                },
              }}
            >
              <Popup>
                <div style={{ color: '#0f172a', fontSize: '13px', minWidth: '170px' }}>
                  <div style={{ fontWeight: '700', fontSize: '14px', marginBottom: '2px' }}>
                    {node.id}: {node.label}
                  </div>
                  {node.is_shelter && (
                    <div style={{ color: '#15803d', fontWeight: '600', marginBottom: '4px' }}>
                      Designated Shelter
                    </div>
                  )}
                  {node.note && (
                    <div style={{ color: '#64748b', fontSize: '12px', marginBottom: '8px' }}>
                      {node.note}
                    </div>
                  )}
                  <div style={{ display: 'flex', gap: '6px', marginTop: '6px' }}>
                    <button
                      onClick={() => onSelectNode && onSelectNode(node.id, 'start')}
                      style={{
                        padding: '4px 10px',
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: '#2563eb',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '4px',
                      }}
                    >
                      Set Start
                    </button>
                    <button
                      onClick={() => onSelectNode && onSelectNode(node.id, 'dest')}
                      style={{
                        padding: '4px 10px',
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: '#15803d',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '4px',
                      }}
                    >
                      Set Shelter
                    </button>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
