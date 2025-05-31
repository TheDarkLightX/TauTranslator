import { useState, useEffect } from 'react';
import styles from '../styles/FileExplorer.module.css';

const FILE_ICONS = {
  '.cnl': '📝',
  '.ebnf': '🔧',
  '.tgf': '⚙️',
  '.cfg': '🔧',
  '.tau': '💎',
  '.tce': '📋',
  '.json': '📄',
  '.txt': '📄',
  'folder': '📁',
  'project': '📁'
};

const FILE_TYPES = {
  '.cnl': 'CNL File',
  '.ebnf': 'EBNF Grammar',
  '.tgf': 'TGF Grammar',
  '.cfg': 'Configuration',
  '.tau': 'Tau Language',
  '.tce': 'TCE File',
  '.json': 'JSON Data',
  '.txt': 'Text File'
};

export default function FileExplorer({ 
  projectFiles = [], 
  selectedFile, 
  onFileSelect, 
  onFileAdd, 
  onFileRemove,
  projectName 
}) {
  const [expandedFolders, setExpandedFolders] = useState(new Set(['root']));
  const [contextMenu, setContextMenu] = useState(null);

  const getFileIcon = (filename) => {
    const ext = '.' + filename.split('.').pop().toLowerCase();
    return FILE_ICONS[ext] || '📄';
  };

  const getFileType = (filename) => {
    const ext = '.' + filename.split('.').pop().toLowerCase();
    return FILE_TYPES[ext] || 'File';
  };

  const organizeFilesByType = (files) => {
    const organized = {
      grammar: [],
      cnl: [],
      config: [],
      examples: [],
      other: []
    };

    files.forEach(file => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      if (['.ebnf', '.tgf', '.lark'].includes(ext)) {
        organized.grammar.push(file);
      } else if (ext === '.cnl') {
        organized.cnl.push(file);
      } else if (['.cfg', '.json'].includes(ext)) {
        organized.config.push(file);
      } else if (['.tau', '.tce', '.txt'].includes(ext)) {
        organized.examples.push(file);
      } else {
        organized.other.push(file);
      }
    });

    return organized;
  };

  const handleFolderToggle = (folderId) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  const handleContextMenu = (event, file) => {
    event.preventDefault();
    setContextMenu({
      x: event.clientX,
      y: event.clientY,
      file
    });
  };

  const handleClickOutside = () => {
    setContextMenu(null);
  };

  useEffect(() => {
    if (contextMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [contextMenu]);

  const organizedFiles = organizeFilesByType(projectFiles);

  const renderFolder = (title, files, folderId, icon = '📁') => {
    const isExpanded = expandedFolders.has(folderId);
    
    return (
      <div key={folderId} className={styles.folder}>
        <div 
          className={styles.folderHeader}
          onClick={() => handleFolderToggle(folderId)}
        >
          <span className={styles.folderIcon}>
            {isExpanded ? '📂' : '📁'}
          </span>
          <span className={styles.folderName}>{title}</span>
          <span className={styles.fileCount}>({files.length})</span>
        </div>
        
        {isExpanded && (
          <div className={styles.folderContent}>
            {files.length === 0 ? (
              <div className={styles.emptyFolder}>
                <span>No files</span>
                <button 
                  className={styles.addButton}
                  onClick={() => onFileAdd(folderId)}
                  title={`Add ${title.toLowerCase()}`}
                >
                  +
                </button>
              </div>
            ) : (
              files.map((file, index) => (
                <div
                  key={index}
                  className={`${styles.fileItem} ${selectedFile?.name === file.name ? styles.selected : ''}`}
                  onClick={() => onFileSelect(file)}
                  onContextMenu={(e) => handleContextMenu(e, file)}
                >
                  <span className={styles.fileIcon}>
                    {getFileIcon(file.name)}
                  </span>
                  <div className={styles.fileInfo}>
                    <div className={styles.fileName}>{file.name}</div>
                    <div className={styles.fileType}>{getFileType(file.name)}</div>
                  </div>
                  {file.size && (
                    <div className={styles.fileSize}>{file.size}</div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={styles.fileExplorer}>
      <div className={styles.header}>
        <div className={styles.title}>
          <span className={styles.projectIcon}>📁</span>
          {projectName || 'No Project'}
        </div>
        <div className={styles.actions}>
          <button 
            className={styles.actionButton}
            onClick={() => onFileAdd('any')}
            title="Add File"
          >
            +
          </button>
          <button 
            className={styles.actionButton}
            onClick={() => {/* refresh */}}
            title="Refresh"
          >
            🔄
          </button>
        </div>
      </div>

      <div className={styles.content}>
        {projectFiles.length === 0 ? (
          <div className={styles.emptyProject}>
            <div className={styles.emptyIcon}>📂</div>
            <div className={styles.emptyText}>No files in project</div>
            <button 
              className={styles.primaryButton}
              onClick={() => onFileAdd('any')}
            >
              Add Files
            </button>
          </div>
        ) : (
          <>
            {renderFolder('Grammar Files', organizedFiles.grammar, 'grammar', '🔧')}
            {renderFolder('CNL Files', organizedFiles.cnl, 'cnl', '📝')}
            {renderFolder('Configuration', organizedFiles.config, 'config', '⚙️')}
            {renderFolder('Examples', organizedFiles.examples, 'examples', '💎')}
            {organizedFiles.other.length > 0 && 
              renderFolder('Other Files', organizedFiles.other, 'other', '📄')}
          </>
        )}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <div 
          className={styles.contextMenu}
          style={{ 
            left: contextMenu.x, 
            top: contextMenu.y 
          }}
        >
          <button 
            className={styles.contextItem}
            onClick={() => {
              onFileSelect(contextMenu.file);
              setContextMenu(null);
            }}
          >
            Open
          </button>
          <button 
            className={styles.contextItem}
            onClick={() => {
              navigator.clipboard.writeText(contextMenu.file.name);
              setContextMenu(null);
            }}
          >
            Copy Name
          </button>
          <div className={styles.contextSeparator} />
          <button 
            className={styles.contextItem}
            onClick={() => {
              onFileRemove(contextMenu.file);
              setContextMenu(null);
            }}
          >
            Remove from Project
          </button>
        </div>
      )}
    </div>
  );
}