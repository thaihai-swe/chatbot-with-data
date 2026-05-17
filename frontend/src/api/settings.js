const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const getSettings = async () => {
  const response = await fetch(`${BASE_URL}/settings`);
  if (!response.ok) {
    throw new Error('Failed to fetch settings');
  }
  return response.json();
};

export const updateSettings = async (settings) => {
  const response = await fetch(`${BASE_URL}/settings`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(settings),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update settings');
  }
  return response.json();
};
