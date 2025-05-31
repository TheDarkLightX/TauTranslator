import { useState } from 'react';
import styles from '../styles/MenuBar.module.css';

export default function MenuBar({ 
  onNewProject, 
  onOpenProject, 
  onImportFiles, 
  onExportResults,
  onProjectSettings,
  onShowHelp,
  projectName 
}) {
  const [activeMenu, setActiveMenu] = useState(null);

  const menuItems = {
    file: {
      label: 'File',
      items: [
        { label: 'New Project', action: onNewProject, shortcut: 'Ctrl+N' },
        { label: 'Open Project...', action: onOpenProject, shortcut: 'Ctrl+O' },
        { type: 'separator' },
        { label: 'Import Files...', action: onImportFiles, shortcut: 'Ctrl+I' },
        { label: 'Export Results...', action: onExportResults, shortcut: 'Ctrl+E' },
        { type: 'separator' },
        { label: 'Project Settings', action: onProjectSettings },
        { label: 'Exit', action: () => window.close() }
      ]
    },
    edit: {
      label: 'Edit',
      items: [
        { label: 'Undo', action: () => {}, shortcut: 'Ctrl+Z' },
        { label: 'Redo', action: () => {}, shortcut: 'Ctrl+Y' },
        { type: 'separator' },
        { label: 'Find', action: () => {}, shortcut: 'Ctrl+F' },
        { label: 'Replace', action: () => {}, shortcut: 'Ctrl+H' },
        { type: 'separator' },
        { label: 'Preferences', action: () => {} }
      ]
    },
    view: {
      label: 'View',
      items: [
        { label: 'Toggle File Explorer', action: () => {}, shortcut: 'Ctrl+Shift+E' },
        { label: 'Toggle Properties Panel', action: () => {}, shortcut: 'Ctrl+Shift+P' },
        { type: 'separator' },
        { label: 'Zoom In', action: () => {}, shortcut: 'Ctrl+=' },
        { label: 'Zoom Out', action: () => {}, shortcut: 'Ctrl+-' },
        { label: 'Reset Zoom', action: () => {}, shortcut: 'Ctrl+0' },
        { type: 'separator' },
        { label: 'Dark Theme', action: () => {} },
        { label: 'Light Theme', action: () => {} }
      ]
    },
    project: {
      label: 'Project',
      items: [
        { label: 'Add Grammar File...', action: () => onImportFiles('grammar') },
        { label: 'Add CNL File...', action: () => onImportFiles('cnl') },
        { label: 'Add Config File...', action: () => onImportFiles('config') },
        { type: 'separator' },
        { label: 'Validate Project', action: () => {}, shortcut: 'F7' },
        { label: 'Build All', action: () => {}, shortcut: 'Ctrl+F9' },
        { type: 'separator' },
        { label: 'Project Settings', action: onProjectSettings }
      ]
    },
    tools: {
      label: 'Tools',
      items: [
        { label: 'Translation Engine...', action: () => {} },
        { label: 'Grammar Validator', action: () => {}, shortcut: 'F8' },
        { label: 'Syntax Checker', action: () => {} },
        { type: 'separator' },
        { label: 'Batch Translation...', action: () => {} },
        { label: 'Export to Different Formats...', action: () => {} },
        { type: 'separator' },
        { label: 'Manage Models...', action: () => {} },
        { label: 'Plugin Manager...', action: () => {} }
      ]
    },
    help: {
      label: 'Help',
      items: [
        { label: 'Documentation', action: onShowHelp },
        { label: 'Tutorials', action: () => {} },
        { label: 'Keyboard Shortcuts', action: () => {}, shortcut: 'Ctrl+?' },
        { type: 'separator' },
        { label: 'Check for Updates', action: () => {} },
        { label: 'About TauTranslator', action: () => {} }
      ]
    }
  };

  const handleMenuClick = (menuKey) => {
    setActiveMenu(activeMenu === menuKey ? null : menuKey);
  };

  const handleItemClick = (item) => {
    if (item.action) {
      item.action();
    }
    setActiveMenu(null);
  };

  const handleClickOutside = () => {
    setActiveMenu(null);
  };

  return (
    <>
      {activeMenu && (
        <div 
          className={styles.overlay} 
          onClick={handleClickOutside}
        />
      )}
      
      <div className={styles.menuBar}>
        <div className={styles.projectInfo}>
          {projectName ? (
            <span className={styles.projectName}>📁 {projectName}</span>
          ) : (
            <span className={styles.noProject}>TauTranslator</span>
          )}
        </div>

        <nav className={styles.menuNav}>
          {Object.entries(menuItems).map(([key, menu]) => (
            <div key={key} className={styles.menuContainer}>
              <button
                className={`${styles.menuButton} ${activeMenu === key ? styles.active : ''}`}
                onClick={() => handleMenuClick(key)}
              >
                {menu.label}
              </button>
              
              {activeMenu === key && (
                <div className={styles.dropdown}>
                  {menu.items.map((item, index) => (
                    item.type === 'separator' ? (
                      <div key={index} className={styles.separator} />
                    ) : (
                      <button
                        key={index}
                        className={styles.menuItem}
                        onClick={() => handleItemClick(item)}
                        disabled={!item.action}
                      >
                        <span className={styles.itemLabel}>{item.label}</span>
                        {item.shortcut && (
                          <span className={styles.shortcut}>{item.shortcut}</span>
                        )}
                      </button>
                    )
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>

        <div className={styles.actionButtons}>
          <button 
            className={styles.iconButton}
            onClick={() => onImportFiles('any')}
            title="Quick Import"
          >
            📁
          </button>
          <button 
            className={styles.iconButton}
            onClick={onProjectSettings}
            title="Project Settings"
          >
            ⚙️
          </button>
          <button 
            className={styles.iconButton}
            onClick={onShowHelp}
            title="Help"
          >
            ❓
          </button>
        </div>
      </div>
    </>
  );
}