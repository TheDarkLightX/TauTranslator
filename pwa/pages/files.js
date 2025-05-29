import { useState, useEffect } from 'react';
import styles from '../styles/Files.module.css';

export default function FilesPage() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // For now, just store file metadata. Content reading can be added.
      const newFile = {
        id: Date.now().toString(),
        name: file.name,
        type: file.type,
        size: file.size,
        lastModified: file.lastModifiedDate.toLocaleDateString(),
        // rawFile: file // Storing the raw file object for later use
      };
      setUploadedFiles(prevFiles => [...prevFiles, newFile]);

      // If it's a text-based file, attempt to read and display its content
      if (file.type.startsWith('text/') || file.type === 'application/json' || file.name.endsWith('.cfg') || file.name.endsWith('.ebnf') || file.name.endsWith('.cnl') || file.name.endsWith('.tgf')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setFileContent(e.target.result);
          setSelectedFile(newFile);
        };
        reader.readAsText(file);
      } else {
        setFileContent('Cannot display content for this file type.');
        setSelectedFile(newFile);
      }
    }
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    // If we stored rawFile, we could read its content here on demand
    // For now, if content was read on upload, it's already in fileContent if it was the last uploaded & readable.
    // This part needs refinement to load content for any selected file.
    if (file.type.startsWith('text/') || file.type === 'application/json' || file.name.endsWith('.cfg') || file.name.endsWith('.ebnf') || file.name.endsWith('.cnl') || file.name.endsWith('.tgf')) {
        // Placeholder: Re-read or fetch content if not already loaded
        // This is a simplified version. A real app might fetch from a stored location or re-read if needed.
        setFileContent(`Content for ${file.name} would be shown here. (Implement full content loading)`);
    } else {
        setFileContent('Cannot display content for this file type.');
    }
  };

  const handleDeleteFile = (fileId) => {
    setUploadedFiles(prevFiles => prevFiles.filter(f => f.id !== fileId));
    if (selectedFile && selectedFile.id === fileId) {
      setSelectedFile(null);
      setFileContent('');
    }
  };

  return (
    <div className={styles.pageContainer}>
      <h1 className={styles.title}>File Management</h1>
      
      <div className={styles.uploadSection}>
        <label htmlFor="fileUpload">Upload New File:</label>
        <input type="file" id="fileUpload" onChange={handleFileUpload} className={styles.uploadInput} />
      </div>

      <div className={styles.layout}>
        <div className={styles.listColumn}>
          <h2 className={styles.columnHeader}>Uploaded Files</h2>
          {uploadedFiles.length === 0 && <p className={styles.emptyStateMessage}>No files uploaded yet.</p>}
          <ul className={styles.fileList}>
            {uploadedFiles.map(file => (
              <li 
                key={file.id} 
                className={`${styles.fileItem} ${selectedFile?.id === file.id ? styles.selected : ''}`}
                onClick={() => handleFileSelect(file)}
              >
                <div>
                  <span className={styles.fileName}>{file.name}</span>
                  <span className={styles.fileMeta}>({file.type}, {(file.size / 1024).toFixed(2)} KB)</span>
                </div>
                <button onClick={(e) => { e.stopPropagation(); handleDeleteFile(file.id); }} className={styles.deleteButton}>Delete</button>
              </li>
            ))}
          </ul>
        </div>

        <div className={styles.viewColumn}>
          <h2 className={styles.columnHeader}>File Content Viewer</h2>
          {selectedFile ? (
            <div className={styles.fileViewerHeader}>
              <h3>{selectedFile.name}</h3>
              <p><strong>Type:</strong> {selectedFile.type}</p>
              <p><strong>Size:</strong> {(selectedFile.size / 1024).toFixed(2)} KB</p>
              <p><strong>Last Modified:</strong> {selectedFile.lastModified}</p>
              <h4>Content:</h4>
              <pre className={styles.fileContentPre}>{fileContent}</pre>
            </div>
          ) : (
            <p className={styles.emptyStateMessage}>Select a file to view its content.</p>
          )}
        </div>
      </div>
    </div>
  );
}
