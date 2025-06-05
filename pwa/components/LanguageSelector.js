/**
 * Language Selector Component
 * ==========================
 * Reusable language selection dropdown
 * 
 * Author: DarkLightX/Dana Edwards
 */

import styles from '../styles/Editor.module.css';

const LANGUAGE_OPTIONS = {
  PLAIN_ENGLISH: 'Plain English',
  ILR: 'ILR (Intermediate Logic Representation)',
  CNL: 'CNL (Controlled Natural Language)',
  TAU: 'Tau Language Code',
};

export default function LanguageSelector({ 
  value, 
  onChange, 
  disabled = false,
  className = styles.languageSelector 
}) {
  return (
    <select 
      value={value} 
      onChange={(e) => onChange(e.target.value)} 
      className={className}
      disabled={disabled}
    >
      {Object.entries(LANGUAGE_OPTIONS).map(([key, label]) => (
        <option key={key} value={key}>{label}</option>
      ))}
    </select>
  );
}

// Export language options for reuse
export { LANGUAGE_OPTIONS };