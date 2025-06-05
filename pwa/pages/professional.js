import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
// import MenuBar from '../components/MenuBar';
// import FileExplorer from '../components/FileExplorer';
// import styles from '../styles/Professional.module.css';

export default function ProfessionalInterface() {
  const router = useRouter();
  const [leftText, setLeftText] = useState('');
  const [rightText, setRightText] = useState('');
  const [machineFormat, setMachineFormat] = useState('TAU');
  const [isLoading, setIsLoading] = useState(false);
  
  // Project state
  const [projectName, setProjectName] = useState('');
  const [projectFiles, setProjectFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  
  // UI state
  const [showFileExplorer, setShowFileExplorer] = useState(false);
  const [showPropertiesPanel, setShowPropertiesPanel] = useState(false);
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionToken, setSessionToken] = useState(null);
  
  // Grammar state
  const [activeGrammar, setActiveGrammar] = useState(null);
  const [grammarValidation, setGrammarValidation] = useState(null);

  const outputFormats = {
    ILR: 'ILR (Intermediate Logic Representation)',
    CNL: 'CNL (Controlled Natural Language)',
    TAU: 'Tau Language Code',
  };

  useEffect(() => {
    // Check for existing authentication
    const storedToken = localStorage.getItem('sessionToken');
    const storedAuth = localStorage.getItem('authenticated');

    if (storedToken && storedAuth === 'true') {
      setSessionToken(storedToken);
      setIsAuthenticated(true);
    }

    // Load last project if exists
    const lastProject = localStorage.getItem('lastProject');
    if (lastProject) {
      try {
        const project = JSON.parse(lastProject);
        setProjectName(project.name);
        setProjectFiles(project.files || []);
      } catch (error) {
        console.error('Failed to load last project:', error);
      }
    }

    // Load active grammar
    loadActiveGrammar();

    // Close settings menu when clicking outside
    const handleClickOutside = () => setShowSettingsMenu(false);
    if (showSettingsMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showSettingsMenu]);

  const loadActiveGrammar = async () => {
    try {
      const response = await fetch('/api/grammar-integration');
      if (response.ok) {
        const data = await response.json();
        if (data.hasActiveGrammar) {
          setActiveGrammar(data.grammar);
        }
      }
    } catch (error) {
      console.error('Failed to load active grammar:', error);
    }
  };

  const validateWithGrammar = async (text) => {
    if (!text.trim() || !activeGrammar) return;

    try {
      const response = await fetch('/api/grammar-integration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: text }),
      });

      if (response.ok) {
        const data = await response.json();
        setGrammarValidation(data);
      }
    } catch (error) {
      console.error('Grammar validation failed:', error);
    }
  };

  const handleTranslate = async () => {
    if (!isAuthenticated) {
      alert('Please authenticate first');
      return;
    }

    setIsLoading(true);

    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionToken}`
      };

      const response = await fetch('/api/translate-unified', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          sourceText: leftText,
          sourceLangKey: 'PLAIN_ENGLISH',
          targetLangKey: machineFormat,
          sourceLangLabel: 'Plain English',
          targetLangLabel: machineFormat,
          forceLocal: false // Use backend if available
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        // Handle backend unavailable errors
        if (response.status === 503 && errorData.details) {
          const { details } = errorData;
          throw new Error(`Backend unavailable. ${details.suggestion || 'Please start the Python backend.'}`);
        }
        
        throw new Error(errorData.message || `Translation failed: ${response.status}`);
      }

      const data = await response.json();
      setRightText(data.translatedText);

    } catch (error) {
      console.error('Translation error:', error);
      setRightText(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAuthenticate = () => {
    const password = prompt('Enter password:');
    if (password) {
      // Mock authentication
      setSessionToken('mock-token');
      setIsAuthenticated(true);
      localStorage.setItem('sessionToken', 'mock-token');
      localStorage.setItem('authenticated', 'true');
    }
  };

  const handleNewProject = () => {
    const name = prompt('Project name:');
    if (name) {
      setProjectName(name);
      setProjectFiles([]);
      setSelectedFile(null);
      setLeftText('');
      setRightText('');
      
      // Save project
      const project = { name, files: [] };
      localStorage.setItem('lastProject', JSON.stringify(project));
    }
  };

  const handleOpenProject = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.ttproject,.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const project = JSON.parse(e.target.result);
            setProjectName(project.name);
            setProjectFiles(project.files || []);
            localStorage.setItem('lastProject', JSON.stringify(project));
          } catch (error) {
            alert('Invalid project file');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const handleImportFiles = (type = 'any') => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    
    switch (type) {
      case 'grammar':
        input.accept = '.ebnf,.tgf,.lark,.bnf';
        break;
      case 'cnl':
        input.accept = '.cnl';
        break;
      case 'config':
        input.accept = '.cfg,.json';
        break;
      default:
        input.accept = '.cnl,.ebnf,.tgf,.cfg,.tau,.tce,.txt,.json';
    }

    input.onchange = (e) => {
      const files = Array.from(e.target.files);
      const newFiles = files.map(file => ({
        name: file.name,
        size: `${Math.round(file.size / 1024)}KB`,
        type: file.type,
        lastModified: file.lastModified,
        content: null // Would load content when needed
      }));

      setProjectFiles(prev => [...prev, ...newFiles]);
      
      // Update saved project
      if (projectName) {
        const project = { 
          name: projectName, 
          files: [...projectFiles, ...newFiles] 
        };
        localStorage.setItem('lastProject', JSON.stringify(project));
      }
    };
    
    input.click();
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    // In a real implementation, load file content
    setLeftText(`// Content of ${file.name}\n// This would load the actual file content`);
  };

  const handleFileRemove = (file) => {
    setProjectFiles(prev => prev.filter(f => f.name !== file.name));
    if (selectedFile?.name === file.name) {
      setSelectedFile(null);
      setLeftText('');
    }
  };

  const handleExportResults = () => {
    if (!rightText) {
      alert('No translation results to export');
      return;
    }

    const blob = new Blob([rightText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `translation_${machineFormat.toLowerCase()}_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setShowSettingsMenu(false);
  };

  const menuItemStyle = {
    width: '100%',
    background: 'none',
    border: 'none',
    padding: '12px 16px',
    textAlign: 'left',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#495057',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#ffffff' }}>
      {/* Clean header with just title and settings */}
      <div style={{ 
        background: '#f8f9fa', 
        borderBottom: '1px solid #dee2e6', 
        padding: '12px 20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => router.push('/')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            ← Back
          </button>
          <h1 style={{ margin: 0, fontSize: '20px', color: '#495057' }}>Tau Translator Professional</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {isAuthenticated ? (
            <span style={{ color: '#28a745', fontWeight: '500', fontSize: '14px' }}>🔓 Authenticated</span>
          ) : (
            <button 
              onClick={handleAuthenticate}
              style={{
                background: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 12px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🔒 Login
            </button>
          )}
          
          <div style={{ position: 'relative' }}>
            <button 
              onClick={() => setShowSettingsMenu(!showSettingsMenu)}
              style={{
                background: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 12px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              ⚙️ Settings
            </button>
            
            {showSettingsMenu && (
              <div style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                background: 'white',
                border: '1px solid #dee2e6',
                borderRadius: '6px',
                boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
                minWidth: '200px',
                zIndex: 1000,
                marginTop: '4px'
              }}>
                <button onClick={handleNewProject} style={menuItemStyle}>📁 New Project</button>
                <button onClick={() => handleImportFiles('grammar')} style={menuItemStyle}>🔧 Import Grammar (.tgf, .ebnf)</button>
                <button onClick={() => handleImportFiles('cnl')} style={menuItemStyle}>📝 Import CNL Files</button>
                <button onClick={() => handleImportFiles('config')} style={menuItemStyle}>⚙️ Import Config Files</button>
                <div style={{ height: '1px', background: '#dee2e6', margin: '4px 0' }} />
                <button onClick={handleExportResults} style={menuItemStyle}>📥 Export Results</button>
                <div style={{ height: '1px', background: '#dee2e6', margin: '4px 0' }} />
                <button onClick={() => setShowFileExplorer(!showFileExplorer)} style={menuItemStyle}>
                  {showFileExplorer ? '📁 Hide File Panel' : '📁 Show File Panel'}
                </button>
                <div style={{ height: '1px', background: '#dee2e6', margin: '4px 0' }} />
                <button 
                  onClick={() => window.open('/settings/llm', '_blank')} 
                  style={menuItemStyle}
                >
                  🤖 LLM Configuration
                </button>
                <div style={{ height: '1px', background: '#dee2e6', margin: '4px 0' }} />
                <div style={{ padding: '8px 16px', fontSize: '12px', color: '#6c757d', fontWeight: '500' }}>
                  Grammar Configuration
                </div>
                <div style={{ padding: '8px 16px', fontSize: '11px', color: '#adb5bd', fontStyle: 'italic' }}>
                  Interface for loading and managing .tgf files or other grammar definitions will go here.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div style={{ flex: 1, display: 'flex' }}>
        {/* Compact File Explorer */}
        {showFileExplorer && (
          <div style={{ 
            width: '250px', 
            background: '#f8f9fa', 
            borderRight: '1px solid #dee2e6',
            padding: '16px'
          }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#495057' }}>📁 Project Files</h3>
            {projectFiles.length === 0 ? (
              <p style={{ color: '#6c757d', fontSize: '12px', fontStyle: 'italic' }}>No files loaded</p>
            ) : (
              <div>
                {projectFiles.map((file, index) => (
                  <div 
                    key={index}
                    onClick={() => handleFileSelect(file)}
                    style={{ 
                      padding: '8px 12px', 
                      border: selectedFile?.name === file.name ? '2px solid #007bff' : '1px solid #dee2e6',
                      borderRadius: '4px',
                      marginBottom: '6px',
                      cursor: 'pointer',
                      background: 'white',
                      fontSize: '13px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    📄 {file.name}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* Simple controls bar like original */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
            background: '#f8f9fa',
            borderBottom: '1px solid #dee2e6',
            gap: '16px'
          }}>
            <div style={{ fontSize: '14px', color: '#495057' }}>
              Plain English
              {activeGrammar && (
                <span style={{ 
                  marginLeft: '10px', 
                  fontSize: '12px', 
                  color: '#28a745',
                  background: '#e7f5e7',
                  padding: '2px 6px',
                  borderRadius: '3px'
                }}>
                  📋 {activeGrammar.originalName}
                </span>
              )}
            </div>
            
            <button 
              onClick={() => {
                const temp = leftText;
                setLeftText(rightText);
                setRightText(temp);
              }}
              style={{
                background: 'none',
                border: '1px solid #ced4da',
                borderRadius: '4px',
                padding: '6px 12px',
                cursor: 'pointer',
                fontSize: '18px'
              }}
              title="Swap languages"
            >
              ↔
            </button>
            
            <select 
              value={machineFormat} 
              onChange={(e) => setMachineFormat(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #ced4da',
                borderRadius: '4px',
                fontSize: '14px',
                minWidth: '180px'
              }}
            >
              {Object.entries(outputFormats).map(([key, label]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
            
            <button 
              onClick={handleTranslate} 
              disabled={isLoading || !leftText.trim() || !isAuthenticated}
              style={{
                background: isLoading || !leftText.trim() || !isAuthenticated ? '#6c757d' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                cursor: isLoading || !leftText.trim() || !isAuthenticated ? 'not-allowed' : 'pointer',
                fontWeight: '500',
                fontSize: '14px'
              }}
            >
              {isLoading ? 'Translating...' : 'Translate'}
            </button>
          </div>

          {/* Clean Editor Panels - just like original */}
          <div style={{ flex: 1, display: 'flex', gap: '1px', background: '#dee2e6' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'white' }}>
              <div style={{
                padding: '12px 16px',
                background: '#f8f9fa',
                borderBottom: '1px solid #dee2e6',
                fontWeight: '500',
                color: '#495057',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span>Plain English</span>
                {selectedFile && (
                  <span style={{ fontSize: '12px', color: '#6c757d' }}>📄 {selectedFile.name}</span>
                )}
              </div>
              <textarea 
                value={leftText}
                onChange={(e) => {
                  setLeftText(e.target.value);
                  // Validate with grammar on input change (debounced)
                  clearTimeout(window.grammarValidationTimeout);
                  window.grammarValidationTimeout = setTimeout(() => {
                    validateWithGrammar(e.target.value);
                  }, 1000);
                }}
                placeholder="Enter plain English text to translate..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  border: 'none',
                  outline: 'none',
                  padding: '20px',
                  fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
                  fontSize: '16px',
                  lineHeight: '1.6',
                  resize: 'none',
                  background: isLoading ? '#f8f9fa' : 'white'
                }}
              />
              
              {/* Grammar validation feedback */}
              {grammarValidation && (
                <div style={{
                  padding: '10px 20px',
                  borderTop: '1px solid #dee2e6',
                  background: grammarValidation.validation?.valid ? '#e7f5e7' : '#fff3cd',
                  color: grammarValidation.validation?.valid ? '#155724' : '#856404',
                  fontSize: '12px'
                }}>
                  <strong>Grammar Check:</strong> {grammarValidation.validation?.message}
                  {grammarValidation.suggestions?.length > 0 && (
                    <div style={{ marginTop: '5px' }}>
                      <strong>Suggestions:</strong>
                      <ul style={{ margin: '5px 0 0 15px', padding: 0 }}>
                        {grammarValidation.suggestions.map((suggestion, index) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'white' }}>
              <div style={{
                padding: '12px 16px',
                background: '#f8f9fa',
                borderBottom: '1px solid #dee2e6',
                fontWeight: '500',
                color: '#495057'
              }}>
                <span>{outputFormats[machineFormat]}</span>
              </div>
              <textarea 
                value={rightText}
                onChange={(e) => setRightText(e.target.value)}
                placeholder="Translation will appear here..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  border: 'none',
                  outline: 'none',
                  padding: '20px',
                  fontFamily: 'Monaco, Menlo, monospace',
                  fontSize: '16px',
                  lineHeight: '1.6',
                  resize: 'none',
                  background: isLoading ? '#f8f9fa' : 'white'
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}