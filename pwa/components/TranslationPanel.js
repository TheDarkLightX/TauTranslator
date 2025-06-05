/**
 * Translation Panel Component
 * ==========================
 * Reusable text editor panel
 * 
 * Author: DarkLightX/Dana Edwards
 */

import styles from '../styles/Editor.module.css';

export default function TranslationPanel({
  label,
  value,
  onChange,
  placeholder,
  readOnly = false,
  disabled = false
}) {
  return (
    <div className={styles.editorPanel}>
      <div className={styles.panelHeader}>{label}</div>
      <textarea 
        className={styles.textarea}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || `Enter ${label} here...`}
        readOnly={readOnly || disabled}
        disabled={disabled}
      />
    </div>
  );
}