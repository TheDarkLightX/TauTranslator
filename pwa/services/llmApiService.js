const API_BASE_URL = '/api'; // Adjust if your API is hosted elsewhere or has a different prefix

async function fetchAPI(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'An unknown error occurred' }));
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
  }

  if (response.status === 204) { // No Content
    return null;
  }
  return response.json();
}

export const getLLMServices = () => {
  return fetchAPI(`${API_BASE_URL}/llm-services`);
};

export const createLLMService = (serviceData) => {
  return fetchAPI(`${API_BASE_URL}/llm-services`, {
    method: 'POST',
    body: JSON.stringify(serviceData),
  });
};

export const updateLLMService = (serviceId, serviceData) => {
  return fetchAPI(`${API_BASE_URL}/llm-services/${serviceId}`, {
    method: 'PUT',
    body: JSON.stringify(serviceData),
  });
};

export const deleteLLMService = (serviceId) => {
  return fetchAPI(`${API_BASE_URL}/llm-services/${serviceId}`, {
    method: 'DELETE',
  });
};

export const setDefaultLLMService = (serviceId) => {
  return fetchAPI(`${API_BASE_URL}/llm-services?id=set-default&serviceId=${encodeURIComponent(serviceId)}`, {
    method: 'POST',
  });
};

// --- Model Management API Calls ---

export const getSystemResources = () => {
  return fetchAPI(`${API_BASE_URL}/system/resources`);
};

export const getGemmaModels = () => {
  return fetchAPI(`${API_BASE_URL}/gemma-models`);
};

export const downloadGemmaModel = (modelId, hfToken) => {
  return fetchAPI(`${API_BASE_URL}/gemma-models`, {
    method: 'POST',
    body: JSON.stringify({ model_id: modelId, hf_token: hfToken }),
  });
};

export const deleteGemmaModel = (modelId) => {
  // The backend expects slashes in modelId (e.g., 'google/gemma-3-2b-it'),
  // so direct inclusion is generally fine. fetch should handle encoding if needed.
  return fetchAPI(`${API_BASE_URL}/gemma-models?id=${encodeURIComponent(modelId)}`, {
    method: 'DELETE',
  });
};
