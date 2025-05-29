import { useState, useEffect } from 'react';

export default function BackendStatusChecker() {
  const [status, setStatus] = useState({
    mainBackend: 'checking',
    llmService: 'checking',
    proxy: 'checking'
  });

  useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    // Check main backend through proxy
    try {
      const response = await fetch('/health');
      if (response.ok) {
        setStatus(prev => ({ ...prev, mainBackend: 'online', proxy: 'working' }));
      } else {
        setStatus(prev => ({ ...prev, mainBackend: 'error', proxy: 'working' }));
      }
    } catch (error) {
      setStatus(prev => ({ ...prev, mainBackend: 'offline', proxy: 'error' }));
    }

    // Check LLM service through proxy
    try {
      const response = await fetch('/api/system/resources');
      if (response.ok) {
        setStatus(prev => ({ ...prev, llmService: 'online' }));
      } else {
        setStatus(prev => ({ ...prev, llmService: 'error' }));
      }
    } catch (error) {
      setStatus(prev => ({ ...prev, llmService: 'offline' }));
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online': return '✅';
      case 'offline': return '❌';
      case 'error': return '⚠️';
      case 'checking': return '🔄';
      default: return '❓';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'online': return 'Online';
      case 'offline': return 'Offline';
      case 'error': return 'Error';
      case 'checking': return 'Checking...';
      default: return 'Unknown';
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'white',
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '12px',
      fontSize: '12px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      zIndex: 9999,
      minWidth: '200px'
    }}>
      <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>Backend Status</h4>
      
      <div style={{ marginBottom: '4px' }}>
        {getStatusIcon(status.mainBackend)} Main Backend (Port 8000): {getStatusText(status.mainBackend)}
      </div>
      
      <div style={{ marginBottom: '4px' }}>
        {getStatusIcon(status.llmService)} LLM Service (Port 45311): {getStatusText(status.llmService)}
      </div>
      
      <div style={{ marginBottom: '8px' }}>
        {getStatusIcon(status.proxy)} PWA Proxy: {getStatusText(status.proxy)}
      </div>
      
      <button 
        onClick={checkBackendStatus}
        style={{
          padding: '4px 8px',
          border: '1px solid #007bff',
          background: '#007bff',
          color: 'white',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '11px'
        }}
      >
        Refresh Status
      </button>
      
      {(status.mainBackend === 'offline' || status.llmService === 'offline') && (
        <div style={{
          marginTop: '8px',
          padding: '8px',
          background: '#fff3cd',
          border: '1px solid #ffeaa7',
          borderRadius: '4px',
          fontSize: '11px'
        }}>
          <strong>To start backends:</strong><br/>
          <code>python3 start_all_backends.py</code>
        </div>
      )}
    </div>
  );
}
