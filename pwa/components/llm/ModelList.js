import React from 'react';
import ModelListItem from './ModelListItem';
import styles from '../../styles/LLMConfig.module.css'; // Reusing styles

export default function ModelList({
  gemmaModels,
  systemResources,
  onDownloadModel,
  onDeleteModel,
}) {
  if (!gemmaModels || gemmaModels.length === 0) {
    return <p>No Gemma models available or found.</p>;
  }

  return (
    <div className={styles.modelListContainer}> {/* You might want a specific style */}
      <h3 className={styles.subSectionTitle}>Available Gemma Models</h3>
      {gemmaModels.map((model) => (
        <ModelListItem
          key={model.id}
          model={model}
          systemResources={systemResources}
          onDownload={onDownloadModel}
          onDelete={onDeleteModel}
        />
      ))}
    </div>
  );
}
