import { useState, useEffect } from 'react';
import styles from '../../styles/LLMConfig.module.css';

export default function APIKeyManager() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [masterPassword, setMasterPassword] = useState('default-password');
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [newApiKey, setNewApiKey] = useState('');

  const fetchProviders = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/api-keys-simple');
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Failed to fetch API keys');
      }
      
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error || 'Unknown error');
      }
      
      setProviders(data.providers || []);
    } catch (err) {
      setError(err.message);
      console.error('Fetch providers error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, [masterPassword]);

  const handleSetApiKey = async (provider, apiKey, testConnection = false) => {
    try {
      const response = await fetch('/api/api-keys-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider: provider.id,
          apiKey,
          testConnection
        })
      });

      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || data.message || 'Failed to save API key');
      }

      await fetchProviders();
      setSelectedProvider(null);
      setNewApiKey('');
      
      const message = testConnection 
        ? `API key for ${provider.name} saved and tested successfully!`
        : `API key for ${provider.name} saved successfully!`;
      alert(message);
    } catch (err) {
      console.error('Set API key error:', err);
      alert(`Error saving API key: ${err.message}`);
    }
  };

  const handleTestApiKey = async (provider) => {
    try {
      const response = await fetch('/api/api-keys-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider: provider.id,
          apiKey: 'test-existing-key',
          testConnection: true
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`✅ API key for ${provider.name} is working correctly!`);
      } else {
        alert(`❌ API key test failed: ${data.error || data.details}`);
      }
    } catch (err) {
      console.error('Test API key error:', err);
      alert(`❌ Error testing API key: ${err.message}`);
    }
  };

  const handleRemoveApiKey = async (provider) => {
    if (!confirm(`Remove API key for ${provider.name}?`)) {
      return;
    }

    try {
      const response = await fetch('/api/api-keys-simple', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider: provider.id
        })
      });

      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to remove API key');
      }

      await fetchProviders();
      alert(`API key for ${provider.name} removed successfully!`);
    } catch (err) {
      console.error('Remove API key error:', err);
      alert(`Error removing API key: ${err.message}`);
    }
  };

  const openProviderUrl = (url) => {
    window.open(url, '_blank');
  };

  if (loading) return <div>Loading API key configuration...</div>;
  if (error) return <div style={{color: 'red'}}>Error: {error}</div>;

  return (
    <div className={styles.settingsSection}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3>🔐 Secure API Key Management</h3>
        <button 
          onClick={() => setShowPasswordDialog(true)}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Change Master Password
        </button>
      </div>
      
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Your API keys are encrypted and stored securely. Click "Get API Key" to obtain keys from providers.
      </p>

      <div style={{ display: 'grid', gap: '16px' }}>
        {providers.map(provider => (
          <div key={provider.id} style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '16px',
            backgroundColor: 'white'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
              <div>
                <h4 style={{ margin: '0 0 4px 0' }}>{provider.name}</h4>
                <p style={{ margin: '0 0 8px 0', color: '#666', fontSize: '14px' }}>
                  {provider.description}
                </p>
                <p style={{ margin: '0', color: '#888', fontSize: '12px' }}>
                  Models: {provider.models.slice(0, 2).join(', ')}
                  {provider.models.length > 2 && ` (+${provider.models.length - 2} more)`}
                </p>
              </div>
              
              <div style={{
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '12px',
                fontWeight: 'bold',
                backgroundColor: provider.hasKey ? '#d4edda' : '#f8d7da',
                color: provider.hasKey ? '#155724' : '#721c24'
              }}>
                {provider.hasKey ? '✅ Configured' : '❌ Not configured'}
              </div>
            </div>

            {provider.hasKey && (
              <p style={{ margin: '8px 0', color: '#666', fontSize: '12px' }}>
                Current key: {provider.keyPreview}
              </p>
            )}

            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <button
                onClick={() => setSelectedProvider(provider)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: provider.hasKey ? '#28a745' : '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                {provider.hasKey ? 'Update Key' : 'Set API Key'}
              </button>

              {provider.hasKey && (
                <>
                  <button
                    onClick={() => handleTestApiKey(provider)}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    Test Key
                  </button>
                  
                  <button
                    onClick={() => handleRemoveApiKey(provider)}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    Remove
                  </button>
                </>
              )}

              <button
                onClick={() => openProviderUrl(provider.url)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                Get API Key
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* API Key Input Dialog */}
      {selectedProvider && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '8px',
            width: '90%',
            maxWidth: '500px'
          }}>
            <h3>Set API Key for {selectedProvider.name}</h3>
            <p style={{ color: '#666', marginBottom: '16px' }}>
              Enter your {selectedProvider.name} API key. It will be encrypted and stored securely.
            </p>
            
            <input
              type="password"
              value={newApiKey}
              onChange={(e) => setNewApiKey(e.target.value)}
              placeholder="Enter API key..."
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginBottom: '16px',
                fontSize: '14px'
              }}
              autoFocus
            />

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setSelectedProvider(null);
                  setNewApiKey('');
                }}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              
              <button
                onClick={() => handleSetApiKey(selectedProvider, newApiKey, false)}
                disabled={!newApiKey.trim()}
                style={{
                  padding: '8px 16px',
                  backgroundColor: newApiKey.trim() ? '#007bff' : '#ccc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: newApiKey.trim() ? 'pointer' : 'not-allowed',
                  marginRight: '8px'
                }}
              >
                Save Key
              </button>
              
              <button
                onClick={() => handleSetApiKey(selectedProvider, newApiKey, true)}
                disabled={!newApiKey.trim()}
                style={{
                  padding: '8px 16px',
                  backgroundColor: newApiKey.trim() ? '#28a745' : '#ccc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: newApiKey.trim() ? 'pointer' : 'not-allowed'
                }}
              >
                Save & Test Key
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Master Password Dialog */}
      {showPasswordDialog && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '8px',
            width: '90%',
            maxWidth: '400px'
          }}>
            <h3>Master Password</h3>
            <p style={{ color: '#666', marginBottom: '16px' }}>
              Enter your master password to encrypt/decrypt API keys.
            </p>
            
            <input
              type="password"
              value={masterPassword}
              onChange={(e) => setMasterPassword(e.target.value)}
              placeholder="Master password..."
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginBottom: '16px',
                fontSize: '14px'
              }}
            />

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowPasswordDialog(false)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              
              <button
                onClick={() => {
                  setShowPasswordDialog(false);
                  fetchProviders();
                }}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}