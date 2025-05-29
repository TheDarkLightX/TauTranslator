import React from 'react';
import { useTheme } from '../context/ThemeContext';

const ThemeToggleButton = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button 
      onClick={toggleTheme}
      style={{
        padding: '4px 8px', /* Smaller padding */
        fontSize: '0.8rem', /* Smaller font size */
        // Basic styling, can be enhanced with icons or module CSS
        backgroundColor: 'var(--secondary-color)', 
        color: 'var(--nav-text-color)',
        border: '1px solid var(--border-color)',
        cursor: 'pointer',
        borderRadius: '4px'
      }}
    >
      {theme === 'light' ? 'Dark' : 'Light'} Mode
    </button>
  );
};

export default ThemeToggleButton;
