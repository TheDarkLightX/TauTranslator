import styles from '../../styles/LLMConfig.module.css';

const LLMServiceListItem = ({ service, isSelected, onSelect, onDelete, onSetDefault }) => {
  return (
    <div
      className={`${styles.serviceItem} ${isSelected ? styles.selected : ''}`}
      onClick={onSelect}
    >
      <div>
        <span className={styles.serviceName}>
          {service.name}
          {service.isDefault && <span className={styles.defaultTag}>(Default)</span>}
          {service.status === 'error' && <span className={styles.errorTag}>(Error)</span>}
        </span>
      </div>
      <div className={styles.serviceActions}>
        {!service.isDefault && (
          <button 
            onClick={(e) => { e.stopPropagation(); onSetDefault(); }} 
            className={`${styles.actionButton} ${styles.setDefaultButton}`}
            title="Set as default"
          >
            Set Default
          </button>
        )}
        <button 
            onClick={(e) => { e.stopPropagation(); onDelete(); }} 
            className={`${styles.actionButton} ${styles.dangerButton}`}
            title="Delete service"
        >
            Delete
        </button>
      </div>
    </div>
  );
};

export default LLMServiceListItem;
