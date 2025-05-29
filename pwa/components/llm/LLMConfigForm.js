import { useState, useEffect } from 'react';
import styles from '../../styles/LLMConfig.module.css';

const LLMConfigForm = ({ initialServiceData = {}, onSave, onCancel }) => {
  const [formData, setFormData] = useState(initialServiceData);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [testResult, setTestResult] = useState(null); // { type: 'success' | 'error', message: string }

  useEffect(() => {
    setFormData(initialServiceData);
    setTestResult(null); // Reset test result when form data changes
  }, [initialServiceData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleProviderTypeChange = (e) => {
    const newProviderType = e.target.value;
    setFormData(prev => ({
      // Reset common fields that might differ or not be applicable
      name: prev.name || '',
      providerType: newProviderType,
      apiKey: '',
      modelId: '',
      modelPath: '',
      localServerEndpoint: '',
      siteUrl: newProviderType === 'OpenRouter API' ? 'https://openrouter.ai/api/v1' : '',
      temperature: prev.temperature || 0.7,
      maxTokens: prev.maxTokens || 2048,
      isDefault: prev.isDefault || false,
    }));
    setTestResult(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  const handleTestConnection = async () => {
    setTestResult({ type: 'info', message: 'Testing connection...' });
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    if (formData.apiKey && (formData.modelId || formData.modelPath || (formData.providerType === 'OpenRouter API' && formData.modelId))) {
        // Simulate a successful test for now
        setTestResult({ type: 'success', message: 'Connection successful!' });
    } else {
        setTestResult({ type: 'error', message: 'Connection failed. Check API key and model details.' });
    }
  };

  const providerTypes = [
    { value: '', label: 'Select Provider Type' },
    { value: 'OpenAI API', label: 'OpenAI API' },
    { value: 'Anthropic API', label: 'Anthropic API' },
    { value: 'Google Generative Language API', label: 'Google Generative Language API (Gemma via API)' },
    { value: 'OpenRouter API', label: 'OpenRouter API' },
    { value: 'Hugging Face Inference API', label: 'Hugging Face Inference API' },
    { value: 'Local Model', label: 'Local Model (e.g., Gemma, Llama)' },
    { value: 'Custom Endpoint', label: 'Custom Endpoint' },
  ];

  return (
    <form onSubmit={handleSubmit} className={styles.formContainer}>
      <h2 className={styles.formTitle}>{formData.id ? 'Edit LLM Service' : 'Add New LLM Service'}</h2>
      
      <div className={styles.formGroup}>
        <label htmlFor="serviceName">Service Name (Alias)</label>
        <input
          type="text"
          id="serviceName"
          name="name"
          value={formData.name || ''}
          onChange={handleChange}
          placeholder="e.g., My OpenAI GPT-4o"
          required
        />
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="providerType">Service Provider Type</label>
        <select
          id="providerType"
          name="providerType"
          value={formData.providerType || ''}
          onChange={handleProviderTypeChange}
          required
        >
          {providerTypes.map(pt => <option key={pt.value} value={pt.value}>{pt.label}</option>)}
        </select>
      </div>

      {formData.providerType && (
        <>
          <div className={styles.formGroup}>
            <label htmlFor="apiKey">API Key</label>
            <input
              type="password"
              id="apiKey"
              name="apiKey"
              value={formData.apiKey || ''}
              onChange={handleChange}
              placeholder={formData.providerType === 'Local Model' ? 'Not required for most local models' : 'Enter your API key'}
              required={formData.providerType !== 'Local Model'}
            />
          </div>

          { (formData.providerType === 'OpenAI API' || 
             formData.providerType === 'Anthropic API' || 
             formData.providerType === 'Google Generative Language API' || 
             formData.providerType === 'Hugging Face Inference API' ||
             formData.providerType === 'OpenRouter API') && (
            <div className={styles.formGroup}>
              <label htmlFor="modelId">Model Identifier</label>
              <input
                type="text"
                id="modelId"
                name="modelId"
                value={formData.modelId || ''}
                onChange={handleChange}
                placeholder={formData.providerType === 'OpenRouter API' ? 'e.g., openai/gpt-4o' : 'e.g., gpt-4-turbo, claude-3-opus-20240229'}
                required
              />
              {formData.providerType === 'OpenRouter API' && 
                <small>Find model identifiers on the OpenRouter models page.</small>
              }
            </div>
          )}

          {formData.providerType === 'OpenRouter API' && (
            <div className={styles.formGroup}>
                <label htmlFor="siteUrl">Site URL / Base URL (Optional)</label>
                <input
                    type="url"
                    id="siteUrl"
                    name="siteUrl"
                    value={formData.siteUrl || 'https://openrouter.ai/api/v1'}
                    onChange={handleChange}
                    placeholder="https://openrouter.ai/api/v1"
                />
                <small>Usually not needed. Change only if you use a proxy or specific OpenRouter instance.</small>
            </div>
          )}

          {formData.providerType === 'Local Model' && (
            <>
              <div className={styles.formGroup}>
                <label htmlFor="modelPath">Model Path / Identifier</label>
                <input
                  type="text"
                  id="modelPath"
                  name="modelPath"
                  value={formData.modelPath || ''}
                  onChange={handleChange}
                  placeholder="e.g., /path/to/gemma-3-weights or ollama/gemma:latest"
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="localServerEndpoint">Local Server Endpoint (Optional)</label>
                <input
                  type="url"
                  id="localServerEndpoint"
                  name="localServerEndpoint"
                  value={formData.localServerEndpoint || ''}
                  onChange={handleChange}
                  placeholder="e.g., http://localhost:11434/api/generate"
                />
              </div>
            </>
          )}
          
          {formData.providerType === 'Custom Endpoint' && (
            <div className={styles.formGroup}>
              <label htmlFor="customEndpointUrl">Custom Endpoint URL</label>
              <input
                type="url"
                id="customEndpointUrl"
                name="customEndpointUrl" // Ensure this matches a state property if you add it
                value={formData.customEndpointUrl || ''}
                onChange={handleChange}
                placeholder="https://your-custom-llm-api.com/invoke"
                required
              />
            </div>
          )}

          <div className={styles.formGroup}>
            <span className={styles.advancedOptionsToggle} onClick={() => setShowAdvanced(!showAdvanced)}>
              {showAdvanced ? 'Hide' : 'Show'} Advanced Options
            </span>
            {showAdvanced && (
              <div className={styles.advancedOptions}>
                <div className={styles.formGroup}>
                  <label htmlFor="temperature">Temperature (0-2, default ~0.7)</label>
                  <input
                    type="number"
                    id="temperature"
                    name="temperature"
                    value={formData.temperature || '0.7'}
                    onChange={handleChange}
                    step="0.1"
                    min="0"
                    max="2"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label htmlFor="maxTokens">Max Tokens (default ~2048)</label>
                  <input
                    type="number"
                    id="maxTokens"
                    name="maxTokens"
                    value={formData.maxTokens || '2048'}
                    onChange={handleChange}
                    step="1"
                    min="1"
                  />
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {testResult && (
        <div className={`${styles.feedback} ${testResult.type === 'success' ? styles.success : (testResult.type === 'error' ? styles.error : '')}`}>
          {testResult.message}
        </div>
      )}

      <div className={styles.formActions}>
        {formData.providerType && <button type="button" onClick={handleTestConnection} className={styles.secondaryButton}>Test Connection</button>}
        <button type="button" onClick={onCancel} className={styles.secondaryButton}>Cancel</button>
        <button type="submit" disabled={!formData.providerType}>Save Configuration</button>
      </div>
    </form>
  );
};

export default LLMConfigForm;
