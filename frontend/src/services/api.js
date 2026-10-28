/**
 * API service for FloodSafe AI backend communication
 */

const API_BASE = '/api';

export async function getScenarios() {
  const response = await fetch(`${API_BASE}/scenarios`);
  if (!response.ok) {
    throw new Error(`Failed to fetch scenarios (Status ${response.status})`);
  }
  return response.json();
}

export async function getScenarioDetails(scenarioId) {
  const response = await fetch(`${API_BASE}/scenarios/${encodeURIComponent(scenarioId)}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch scenario details for ${scenarioId} (Status ${response.status})`);
  }
  return response.json();
}

export async function compareRoutes(payload) {
  const response = await fetch(`${API_BASE}/routes/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorDetail = `Status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return response.json();
}
