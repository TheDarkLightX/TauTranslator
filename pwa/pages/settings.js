import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function SettingsPage() {
  const router = useRouter();
  const [grammarFiles, setGrammarFiles] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedGrammar, setSelectedGrammar] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      // Load available grammars and models
      const response = await fetch('/api/settings');
      if (response.ok) {
        const data = await response.json();
        setGrammarFiles(data.grammarFiles || []);
        setModels(data.models || []);
        setSelectedGrammar(data.selectedGrammar || '');
        setSelectedModel(data.selectedModel || '');
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleFileUpload = async (event, type) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        loadSettings(); // Refresh the lists
        alert(`${type} file uploaded successfully!`);
      } else {
        alert(`Failed to upload ${type} file`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const saveSettings = async () => {
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selectedGrammar,
          selectedModel,
        }),
      });

      if (response.ok) {
        alert('Settings saved successfully!');
      } else {
        alert('Failed to save settings');
      }
    } catch (error) {
      console.error('Save error:', error);
      alert('Save failed');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      {/* Navigation Header */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginBottom: '20px',
        padding: '10px 0',
        borderBottom: '1px solid #eee'
      }}>
        <button
          onClick={() => router.push('/')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          ← Back to Translator
        </button>
        
        <h1 style={{ margin: '0 0 0 20px', fontSize: '24px', fontWeight: 'bold' }}>
          Settings
        </h1>
      </div>


      {/* Grammar Files Section */}
      <div style={{ marginBottom: '40px' }}>
        <h2>📝 Grammar Files (.ebnf, .lark, .tgf)</h2>
        <p>Upload grammar files to define parsing rules for Tau Language, CNL, or custom formats.</p>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Upload Grammar File:
          </label>
          <input
            type="file"
            accept=".ebnf,.lark,.tgf,.bnf"
            onChange={(e) => handleFileUpload(e, 'grammar')}
            disabled={uploading}
            style={{
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              width: '100%',
              maxWidth: '400px'
            }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Active Grammar:
          </label>
          <select
            value={selectedGrammar}
            onChange={(e) => setSelectedGrammar(e.target.value)}
            style={{
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              width: '100%',
              maxWidth: '400px'
            }}
          >
            <option value="">Select a grammar file...</option>
            {grammarFiles.map((file, index) => (
              <option key={index} value={file.name}>
                {file.name} ({file.type})
              </option>
            ))}
          </select>
        </div>

        {grammarFiles.length > 0 && (
          <div style={{
            background: '#f8f9fa',
            padding: '12px',
            borderRadius: '4px',
            border: '1px solid #dee2e6'
          }}>
            <h4>Available Grammar Files:</h4>
            <ul>
              {grammarFiles.map((file, index) => (
                <li key={index}>
                  <strong>{file.name}</strong> - {file.type} ({file.size})
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Models Section */}
      <div style={{ marginBottom: '40px' }}>
        <h2>🤖 Language Models</h2>
        <p>Configure LLM models for enhanced translation quality.</p>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Upload Model File:
          </label>
          <input
            type="file"
            accept=".bin,.gguf,.safetensors"
            onChange={(e) => handleFileUpload(e, 'model')}
            disabled={uploading}
            style={{
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              width: '100%',
              maxWidth: '400px'
            }}
          />
          <small style={{ color: '#666' }}>
            Supports GGUF, GGML, SafeTensors formats
          </small>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Active Model:
          </label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            style={{
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              width: '100%',
              maxWidth: '400px'
            }}
          >
            <option value="">Pattern-based only (default)</option>
            <option value="gemma3">Gemma 3 (if installed)</option>
            {models.map((model, index) => (
              <option key={index} value={model.name}>
                {model.name} ({model.type})
              </option>
            ))}
          </select>
        </div>

        {models.length > 0 && (
          <div style={{
            background: '#f8f9fa',
            padding: '12px',
            borderRadius: '4px',
            border: '1px solid #dee2e6'
          }}>
            <h4>Available Models:</h4>
            <ul>
              {models.map((model, index) => (
                <li key={index}>
                  <strong>{model.name}</strong> - {model.type} ({model.status})
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* File Import Section */}
      <div style={{ marginBottom: '40px' }}>
        <h2>📁 File Import</h2>
        <p>Import CNL files, example files, or Tau programs for testing.</p>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Import Files:
          </label>
          <input
            type="file"
            accept=".cnl,.tau,.tce,.txt"
            multiple
            onChange={(e) => handleFileUpload(e, 'examples')}
            disabled={uploading}
            style={{
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              width: '100%',
              maxWidth: '400px'
            }}
          />
          <small style={{ color: '#666' }}>
            Supports .cnl, .tau, .tce, .txt files
          </small>
        </div>
      </div>

      {/* Save Settings */}
      <div style={{ marginBottom: '40px' }}>
        <button
          onClick={saveSettings}
          disabled={uploading}
          style={{
            padding: '12px 24px',
            border: 'none',
            background: '#28a745',
            color: 'white',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
          }}
        >
          {uploading ? '⏳ Saving...' : '💾 Save Settings'}
        </button>
      </div>

      {/* Quick Setup */}
      <div style={{
        background: '#e7f3ff',
        padding: '16px',
        borderRadius: '4px',
        border: '1px solid #b3d7ff'
      }}>
        <h3>🚀 Quick Setup</h3>
        <p>To get started quickly:</p>
        <ol>
          <li>Upload the included <code>tce_tau_accurate.ebnf</code> grammar file</li>
          <li>Select it as the active grammar</li>
          <li>Optionally install Gemma 3 for enhanced translation</li>
          <li>Import example .tce files to test translation</li>
        </ol>
        
        <div style={{ marginTop: '12px' }}>
          <strong>Grammar Files Location:</strong><br/>
          <code>grammars/tce_tau_accurate.ebnf</code><br/>
          <code>src/tau_translator_omega/core_engine/cnl_parser/grammars/</code>
        </div>
      </div>
    </div>
  );
}