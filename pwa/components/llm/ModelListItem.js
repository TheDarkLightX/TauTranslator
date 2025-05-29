import React from 'react';
import styles from '../../styles/LLMConfig.module.css'; // Reusing styles

// Helper to format bytes into GB with one decimal place
const formatBytesToGB = (bytes) => {
  if (bytes === undefined || bytes === null || isNaN(bytes)) return 'N/A';
  return (Number(bytes) / (1024 * 1024 * 1024)).toFixed(1);
};

export default function ModelListItem({ model, systemResources, onDownload, onDelete }) {
  if (!model) return null;

  const {
    id,
    name,
    description,
    ram_gb_min,
    disk_gb_min,
    is_downloaded,
    // family, // Not used in this basic display yet
    // num_parameters, // Not used in this basic display yet
    // context_length, // Not used in this basic display yet
  } = model;

  let statusText = '';
  let canDownload = false;
  let canDelete = is_downloaded;

  const requiredRamBytes = ram_gb_min * 1024 * 1024 * 1024;
  const requiredDiskBytes = disk_gb_min * 1024 * 1024 * 1024;

  if (is_downloaded) {
    statusText = 'Downloaded';
  } else if (!systemResources) {
    statusText = 'Resource info pending...';
  } else if (systemResources.available_ram < requiredRamBytes) {
    statusText = `Requires ${ram_gb_min} GB RAM (Not enough)`;
  } else if (systemResources.available_disk < requiredDiskBytes) {
    statusText = `Requires ${disk_gb_min} GB Disk (Not enough)`;
  } else {
    statusText = 'Available for download';
    canDownload = true;
  }

  return (
    <div className={styles.modelListItem}> {/* Create this style */}
      <div className={styles.modelInfo}>
        <h4 className={styles.modelName}>{name}</h4>
        <p className={styles.modelDescription}>{description}</p>
        <p className={styles.modelRequirements}>
          Requires: {ram_gb_min} GB RAM, {disk_gb_min} GB Disk
        </p>
        <p className={styles.modelStatus}>Status: {statusText}</p>
      </div>
      <div className={styles.modelActions}>
        {canDownload && (
          <button
            onClick={() => onDownload(id)}
            className={`${styles.actionButton} ${styles.downloadButton}`} // Create these styles
          >
            Download
          </button>
        )}
        {canDelete && (
          <button
            onClick={() => onDelete(id)}
            className={`${styles.actionButton} ${styles.deleteButton}`} // Create these styles
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}
