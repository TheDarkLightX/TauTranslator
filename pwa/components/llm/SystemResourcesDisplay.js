import React from 'react';
import styles from '../../styles/LLMConfig.module.css'; // Assuming we can reuse some styles

// Helper to format bytes into GB with one decimal place
const formatBytesToGB = (bytes) => {
  if (bytes === undefined || bytes === null) return 'N/A';
  return (bytes / (1024 * 1024 * 1024)).toFixed(1);
};

export default function SystemResourcesDisplay({ systemResources }) {
  if (!systemResources) {
    return <p>System resource information is not available.</p>;
  }

  const { total_ram, available_ram, total_disk, available_disk } = systemResources;

  return (
    <div className={styles.systemResourcesContainer}> {/* You might want a specific style */}
      <h3 className={styles.subSectionTitle}>System Resources</h3>
      <div className={styles.resourceItem}>
        <strong>RAM:</strong> {formatBytesToGB(available_ram)} GB available / {formatBytesToGB(total_ram)} GB total
      </div>
      <div className={styles.resourceItem}>
        <strong>Disk:</strong> {formatBytesToGB(available_disk)} GB available / {formatBytesToGB(total_disk)} GB total
      </div>
    </div>
  );
}
