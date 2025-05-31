import { useState, useEffect } from 'react';
import styles from '../../styles/LLMConfig.module.css';

export default function HuggingFaceModelManager({ onModelDownloaded }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [downloadedModels, setDownloadedModels] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [hfToken, setHfToken] = useState('');
  const [showToken, setShowToken] = useState(false);

  // Load downloaded models on component mount
  useEffect(() => {
    fetchDownloadedModels();
  }, []);

  const fetchDownloadedModels = async () => {
    try {
      const response = await fetch('/api/huggingface-models');
      if (response.ok) {
        const models = await response.json();
        setDownloadedModels(models);
      }
    } catch (error) {
      console.error('Error fetching downloaded models:', error);
    }
  };

  const searchModels = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const response = await fetch(`/api/huggingface-models?search=${encodeURIComponent(searchQuery)}`);
      if (response.ok) {
        const results = await response.json();
        setSearchResults(results);
      } else {
        alert('Search failed');
      }
    } catch (error) {
      console.error('Search error:', error);
      alert('Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  const downloadModel = async (modelId) => {
    if (!modelId) return;

    setIsDownloading(true);
    try {
      const response = await fetch('/api/huggingface-models', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_id: modelId,
          hf_token: hfToken || undefined
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Model ${modelId} download started successfully!`);
        await fetchDownloadedModels(); // Refresh list
        if (onModelDownloaded) {
          onModelDownloaded(result.model);
        }
      } else {
        const error = await response.json();
        alert(`Download failed: ${error.message}`);
      }
    } catch (error) {
      console.error('Download error:', error);
      alert(`Download failed: ${error.message}`);
    } finally {
      setIsDownloading(false);
    }
  };

  const deleteModel = async (modelId) => {
    if (!confirm(`Are you sure you want to delete model ${modelId}?`)) return;

    try {
      const response = await fetch(`/api/huggingface-models?id=${encodeURIComponent(modelId)}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert('Model deleted successfully!');
        await fetchDownloadedModels(); // Refresh list
      } else {
        const error = await response.json();
        alert(`Delete failed: ${error.message}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert(`Delete failed: ${error.message}`);
    }
  };

  const formatModelSize = (bytes) => {
    if (!bytes) return 'Unknown';
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(2)} GB`;
  };

  return (
    <div className={styles.modelManager}>
      <h3>Hugging Face Model Manager</h3>
      
      {/* Hugging Face Token */}
      <div className={styles.tokenSection}>
        <label>
          Hugging Face Token (optional for public models):
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <input
              type={showToken ? 'text' : 'password'}
              value={hfToken}
              onChange={(e) => setHfToken(e.target.value)}
              placeholder="hf_xxxxxxxxxxxxxxxxxxxx"
              style={{ flex: 1 }}
            />
            <button 
              type="button"
              onClick={() => setShowToken(!showToken)}
              style={{ padding: '5px 10px' }}
            >
              {showToken ? '🙈' : '👁️'}
            </button>
          </div>
        </label>
        <small style={{ color: '#666' }}>
          Required for private models. Get your token from{' '}
          <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noopener noreferrer">
            huggingface.co/settings/tokens
          </a>
        </small>
      </div>

      {/* Model Search */}
      <div className={styles.searchSection}>
        <h4>Search & Download Models</h4>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Enter model name (e.g. google/gemma-2-2b-it, meta-llama/Llama-2-7b-hf)"
            style={{ flex: 1, padding: '8px' }}
            onKeyPress={(e) => e.key === 'Enter' && searchModels()}
          />
          <button 
            onClick={searchModels} 
            disabled={isSearching || !searchQuery.trim()}
            style={{ padding: '8px 15px' }}
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>

        {/* Quick Download */}
        <div style={{ marginBottom: '15px' }}>
          <input
            type="text"
            placeholder="Or paste exact model ID to download directly"
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && e.target.value.trim()) {
                downloadModel(e.target.value.trim());
                e.target.value = '';
              }
            }}
          />
          <small style={{ color: '#666' }}>
            Press Enter to download directly, or use search above to browse models
          </small>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className={styles.searchResults}>
            <h5>Search Results:</h5>
            {searchResults.slice(0, 10).map((model) => (
              <div key={model.id} className={styles.modelItem}>
                <div>
                  <strong>{model.id}</strong>
                  {model.pipeline_tag && <span className={styles.badge}>{model.pipeline_tag}</span>}
                  <br />
                  <small>{model.description || 'No description available'}</small>
                  <br />
                  <small>👍 {model.likes || 0} | 📥 {model.downloads || 0}</small>
                </div>
                <button
                  onClick={() => downloadModel(model.id)}
                  disabled={isDownloading}
                  className={styles.downloadBtn}
                >
                  {isDownloading ? 'Downloading...' : 'Download'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Downloaded Models */}
      <div className={styles.downloadedSection}>
        <h4>Downloaded Models ({downloadedModels.length})</h4>
        {downloadedModels.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>No models downloaded yet</p>
        ) : (
          <div className={styles.modelsList}>
            {downloadedModels.map((model) => (
              <div key={model.id} className={styles.downloadedModel}>
                <div className={styles.modelInfo}>
                  <strong>{model.id}</strong>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {model.type && <span>Type: {model.type}</span>}
                    {model.diskSizeFormatted && <span> | Size: {model.diskSizeFormatted}</span>}
                    <br />
                    Downloaded: {new Date(model.downloadedAt).toLocaleDateString()}
                  </div>
                  {model.description && (
                    <div style={{ fontSize: '12px', marginTop: '5px' }}>
                      {model.description}
                    </div>
                  )}
                </div>
                <div className={styles.modelActions}>
                  <span className={model.exists ? styles.statusReady : styles.statusMissing}>
                    {model.exists ? '✅ Ready' : '❌ Missing'}
                  </span>
                  <button
                    onClick={() => deleteModel(model.id)}
                    className={styles.deleteBtn}
                    style={{ marginLeft: '10px' }}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Popular Models Quick Access */}
      <div className={styles.popularSection}>
        <h4>Popular Models - Quick Download</h4>
        <div className={styles.popularGrid}>
          {[
            { id: 'google/gemma-2-2b-it', name: 'Gemma 2B', desc: 'Compact & efficient' },
            { id: 'meta-llama/Llama-3.1-8B-Instruct', name: 'Llama 3.1 8B', desc: 'High quality reasoning' },
            { id: 'microsoft/DialoGPT-medium', name: 'DialoGPT', desc: 'Conversational' },
            { id: 'huggingface/CodeBERTa-small-v1', name: 'CodeBERTa', desc: 'Code understanding' }
          ].map((model) => (
            <button
              key={model.id}
              onClick={() => downloadModel(model.id)}
              disabled={isDownloading}
              className={styles.popularModel}
            >
              <strong>{model.name}</strong>
              <br />
              <small>{model.desc}</small>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}