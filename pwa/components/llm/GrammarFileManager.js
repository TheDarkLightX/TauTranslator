import { useState, useEffect } from 'react';
import styles from '../../styles/LLMConfig.module.css';

export default function GrammarFileManager({ onGrammarSelected }) {
  const [grammarFiles, setGrammarFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    fetchGrammarFiles();
  }, []);

  const fetchGrammarFiles = async () => {
    try {
      const response = await fetch('/api/grammar-files');
      if (response.ok) {
        const files = await response.json();
        setGrammarFiles(files);
      }
    } catch (error) {
      console.error('Error fetching grammar files:', error);
    }
  };

  const uploadFiles = async (files) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    const formData = new FormData();
    
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/grammar-files', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        alert(`${result.files.length} file(s) uploaded successfully!`);
        await fetchGrammarFiles();
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.message}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileSelect = (event) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      uploadFiles(files);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      uploadFiles(files);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const setActiveGrammar = async (fileId) => {
    try {
      const response = await fetch(`/api/grammar-files?id=${fileId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ isActive: true }),
      });

      if (response.ok) {
        await fetchGrammarFiles();
        const activeFile = grammarFiles.find(f => f.id === fileId);
        if (onGrammarSelected && activeFile) {
          onGrammarSelected(activeFile);
        }
      } else {
        alert('Failed to set active grammar');
      }
    } catch (error) {
      console.error('Error setting active grammar:', error);
      alert('Failed to set active grammar');
    }
  };

  const deleteGrammarFile = async (fileId) => {
    const file = grammarFiles.find(f => f.id === fileId);
    if (!confirm(`Are you sure you want to delete ${file?.originalName}?`)) return;

    try {
      const response = await fetch(`/api/grammar-files?id=${fileId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert('File deleted successfully!');
        await fetchGrammarFiles();
      } else {
        const error = await response.json();
        alert(`Delete failed: ${error.message}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert(`Delete failed: ${error.message}`);
    }
  };

  const downloadGrammarFile = async (file) => {
    try {
      const response = await fetch(`/grammars/${file.filename}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.originalName;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        alert('Failed to download file');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file');
    }
  };

  const getFileTypeIcon = (type) => {
    switch (type) {
      case '.ebnf':
      case '.bnf':
        return '📋';
      case '.tgf':
        return '🔧';
      case '.lark':
        return '🌳';
      case '.cnl':
        return '📝';
      case '.cfg':
      case '.json':
        return '⚙️';
      default:
        return '📄';
    }
  };

  const getFileTypeDescription = (type) => {
    switch (type) {
      case '.ebnf':
        return 'Extended Backus-Naur Form';
      case '.bnf':
        return 'Backus-Naur Form';
      case '.tgf':
        return 'Tau Grammar Format';
      case '.lark':
        return 'Lark Parser Grammar';
      case '.cnl':
        return 'Controlled Natural Language';
      case '.cfg':
        return 'Configuration File';
      case '.json':
        return 'JSON Configuration';
      default:
        return 'Text File';
    }
  };

  return (
    <div className={styles.grammarManager}>
      <h3>Grammar & CNL File Manager</h3>
      
      {/* Upload Area */}
      <div
        className={`${styles.uploadArea} ${dragOver ? styles.dragOver : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById('grammar-file-input').click()}
      >
        <input
          id="grammar-file-input"
          type="file"
          multiple
          accept=".ebnf,.tgf,.lark,.bnf,.cnl,.cfg,.json,.txt"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={isUploading}
        />
        <div className={styles.uploadContent}>
          {isUploading ? (
            <div>
              <div className={styles.spinner}>⏳</div>
              <p>Uploading files...</p>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>📁</div>
              <p><strong>Drop files here or click to upload</strong></p>
              <p style={{ fontSize: '12px', color: '#666' }}>
                Supported: .ebnf, .tgf, .lark, .bnf, .cnl, .cfg, .json, .txt
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Supported Formats Info */}
      <div className={styles.formatsInfo}>
        <h4>Supported Grammar Formats:</h4>
        <div className={styles.formatsList}>
          <div><strong>.tgf</strong> - Tau Grammar Format (primary)</div>
          <div><strong>.ebnf/.bnf</strong> - Extended/Backus-Naur Form</div>
          <div><strong>.lark</strong> - Lark Parser Grammar</div>
          <div><strong>.cnl</strong> - Controlled Natural Language</div>
          <div><strong>.cfg/.json</strong> - Configuration files</div>
        </div>
      </div>

      {/* Grammar Files List */}
      <div className={styles.filesSection}>
        <h4>Uploaded Grammar Files ({grammarFiles.length})</h4>
        {grammarFiles.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            No grammar files uploaded yet. Upload your .tgf, .ebnf, or other grammar files to get started.
          </p>
        ) : (
          <div className={styles.filesList}>
            {grammarFiles.map((file) => (
              <div 
                key={file.id} 
                className={`${styles.grammarFile} ${file.isActive ? styles.activeFile : ''}`}
              >
                <div className={styles.fileHeader}>
                  <div className={styles.fileIcon}>
                    {getFileTypeIcon(file.type)}
                  </div>
                  <div className={styles.fileInfo}>
                    <div className={styles.fileName}>
                      <strong>{file.originalName}</strong>
                      {file.isActive && <span className={styles.activeBadge}>ACTIVE</span>}
                    </div>
                    <div className={styles.fileDetails}>
                      <span>{getFileTypeDescription(file.type)}</span>
                      <span>•</span>
                      <span>{file.sizeFormatted}</span>
                      <span>•</span>
                      <span>Uploaded {new Date(file.uploadedAt).toLocaleDateString()}</span>
                    </div>
                    {file.description && (
                      <div className={styles.fileDescription}>{file.description}</div>
                    )}
                  </div>
                </div>
                
                <div className={styles.fileActions}>
                  {!file.isActive && (
                    <button
                      onClick={() => setActiveGrammar(file.id)}
                      className={styles.activateBtn}
                    >
                      Set Active
                    </button>
                  )}
                  <button
                    onClick={() => downloadGrammarFile(file)}
                    className={styles.downloadBtn}
                    title="Download file"
                  >
                    📥
                  </button>
                  <button
                    onClick={() => deleteGrammarFile(file.id)}
                    className={styles.deleteBtn}
                    title="Delete file"
                  >
                    🗑️
                  </button>
                </div>

                <div className={styles.fileStatus}>
                  <span className={file.exists ? styles.statusReady : styles.statusMissing}>
                    {file.exists ? '✅ Available' : '❌ Missing'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Active Grammar Info */}
      {grammarFiles.some(f => f.isActive) && (
        <div className={styles.activeGrammarInfo}>
          <h4>🎯 Active Grammar</h4>
          {grammarFiles.filter(f => f.isActive).map(file => (
            <div key={file.id} className={styles.activeGrammarDetails}>
              <p>
                <strong>{file.originalName}</strong> ({getFileTypeDescription(file.type)})
              </p>
              <p style={{ fontSize: '12px', color: '#666' }}>
                This grammar will be used for translation parsing and validation.
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}