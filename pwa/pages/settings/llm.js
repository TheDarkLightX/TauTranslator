import { useState, useEffect } from 'react';
import LLMConfigForm from '../../components/llm/LLMConfigForm';
import LLMServiceListItem from '../../components/llm/LLMServiceListItem';
import styles from '../../styles/LLMConfig.module.css';
import {
  getLLMServices,
  createLLMService,
  updateLLMService,
  deleteLLMService,
  setDefaultLLMService,
  getSystemResources, // Added for Model Management
  getGemmaModels,     // Added for Model Management
  deleteGemmaModel,   // Added for Model Management
  downloadGemmaModel  // Added for Model Management
} from '../../services/llmApiService'; // Import API service functions
import SystemResourcesDisplay from '../../components/llm/SystemResourcesDisplay'; // Added for Model Management
import ModelList from '../../components/llm/ModelList'; // Added for Model Management

export default function LLMConfigurationPage() {
  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [isLoading, setIsLoading] = useState(true); // Added loading state
  const [error, setError] = useState(null); // Added error state

  // State for Model Management
  const [systemResources, setSystemResources] = useState(null);
  const [gemmaModels, setGemmaModels] = useState([]);
  const [modelManagementLoading, setModelManagementLoading] = useState(true);
  const [modelManagementError, setModelManagementError] = useState(null);

  const fetchServices = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getLLMServices();
      setServices(data || []); // Ensure services is an array
    } catch (err) {
      setError(err.message || 'Failed to fetch LLM services.');
      setServices([]); // Clear services on error or set to empty array
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchServices();
  }, []);

  // Fetch Model Management Data (System Resources and Gemma Models)
  const fetchModelManagementData = async () => {
    setModelManagementLoading(true);
    setModelManagementError(null);
    try {
      const resourcesData = await getSystemResources();
      setSystemResources(resourcesData);
      const modelsData = await getGemmaModels();
      setGemmaModels(modelsData || []); // Ensure gemmaModels is an array
    } catch (err) {
      setModelManagementError(err.message || 'Failed to fetch model management data.');
      setSystemResources(null);
      setGemmaModels([]);
    } finally {
      setModelManagementLoading(false);
    }
  };

  useEffect(() => {
    fetchModelManagementData();
  }, []);

  // --- Model Management Handlers ---
  const handleDownloadModel = async (modelId) => {
    // Basic prompt for HF token. In a real app, this might be stored or handled more securely.
    const hfToken = prompt('Enter your Hugging Face API token (optional for public models, press Enter to skip):', '');
    
    setModelManagementLoading(true);
    setModelManagementError(null);
    try {
      await downloadGemmaModel(modelId, hfToken || undefined); // Pass undefined if token is empty
      await fetchModelManagementData(); // Refresh model list and resources
      alert('Model download started/completed successfully!'); // Basic feedback
    } catch (err) {
      setModelManagementError(err.message || 'Failed to download model.');
      alert(`Error downloading model: ${err.message}`); // Basic feedback
    } finally {
      setModelManagementLoading(false);
    }
  };

  const handleDeleteModel = async (modelId) => {
    if (confirm(`Are you sure you want to delete model ${modelId}?`)) {
      setModelManagementLoading(true);
      setModelManagementError(null);
      try {
        await deleteGemmaModel(modelId);
        await fetchModelManagementData(); // Refresh model list and resources
        alert('Model deleted successfully!'); // Basic feedback
      } catch (err) {
        setModelManagementError(err.message || 'Failed to delete model.');
        alert(`Error deleting model: ${err.message}`); // Basic feedback
      } finally {
        setModelManagementLoading(false);
      }
    }
  };

  const handleAddNew = () => {
    setSelectedService(null);
    setIsAddingNew(true);
  };

  const handleSelectService = (service) => {
    setSelectedService(service);
    setIsAddingNew(false);
  };

  const handleSaveService = async (serviceToSave) => {
    setIsLoading(true);
    setError(null);
    try {
      if (serviceToSave.id) {
        await updateLLMService(serviceToSave.id, serviceToSave);
      } else {
        await createLLMService(serviceToSave);
      }
      await fetchServices(); // Re-fetch services to get the latest state
      setSelectedService(null);
      setIsAddingNew(false);
    } catch (err) {
      setError(err.message || 'Failed to save LLM service.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteService = async (serviceId) => {
    if (confirm('Are you sure you want to delete this LLM service?')) {
      setIsLoading(true);
      setError(null);
      try {
        await deleteLLMService(serviceId);
        await fetchServices(); // Re-fetch services
        if (selectedService && selectedService.id === serviceId) {
          setSelectedService(null);
          setIsAddingNew(false);
        }
      } catch (err) {
        setError(err.message || 'Failed to delete LLM service.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleSetDefault = async (serviceId) => {
    setIsLoading(true);
    setError(null);
    try {
      await setDefaultLLMService(serviceId);
      await fetchServices(); // Re-fetch services to reflect the change
    } catch (err) {
      setError(err.message || 'Failed to set default LLM service.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <h1 className={styles.title}>LLM Configuration</h1>
      {error && <p className={styles.errorMessage} style={{color: 'red', border: '1px solid red', padding: '10px', borderRadius: '4px'}}>Error: {error}</p>}
      {isLoading && <p>Loading LLM services...</p>}
      {!isLoading && !error && (
        <div className={styles.configLayout}>
        <div className={styles.listColumn}>
          <h2 className={styles.listHeader}>Configured LLM Services</h2>
          {services.map(service => (
            <LLMServiceListItem
              key={service.id}
              service={service}
              isSelected={selectedService?.id === service.id && !isAddingNew}
              onSelect={() => handleSelectService(service)}
              onDelete={() => handleDeleteService(service.id)}
              onSetDefault={() => handleSetDefault(service.id)}
            />
          ))}
          <button onClick={handleAddNew} className={styles.addNewButton}>
            + Add New LLM Service
          </button>
        </div>
        <div className={styles.formColumn}>
          {(isAddingNew || selectedService) ? (
            <LLMConfigForm
              key={selectedService ? selectedService.id : 'new'}
              initialServiceData={isAddingNew ? {} : selectedService}
              onSave={handleSaveService}
              onCancel={() => { setSelectedService(null); setIsAddingNew(false); }}
            />
          ) : (
            <p>Select a service to edit or add a new one.</p>
          )}
        </div>
      </div>
      )}

      <hr className={styles.sectionDivider} />

      {/* Model Management Section */}
      <div className={styles.settingsSection}>
        <h2 className={styles.sectionTitle}>Model Management</h2>
        {modelManagementLoading && <p>Loading model management data...</p>}
        {modelManagementError && <p className={styles.errorMessage} style={{color: 'red', border: '1px solid red', padding: '10px', borderRadius: '4px'}}>Error: {modelManagementError}</p>}
        {!modelManagementLoading && !modelManagementError && (
          <div>
            {systemResources && <SystemResourcesDisplay systemResources={systemResources} />}
            <ModelList 
              gemmaModels={gemmaModels}
              systemResources={systemResources}
              onDownloadModel={handleDownloadModel}
              onDeleteModel={handleDeleteModel}
            />
          </div>
        )}
      </div>

      <hr className={styles.sectionDivider} />

      <div className={styles.settingsSection}>
        <h2 className={styles.sectionTitle}>Grammar Configuration</h2>
        <p className={styles.placeholderText}>Interface for loading and managing .tgf files or other grammar definitions will go here.</p>
        {/* Placeholder for grammar upload/selection components */}
      </div>

      <hr className={styles.sectionDivider} />

      <div className={styles.settingsSection}>
        <h2 className={styles.sectionTitle}>Translation Engine Parameters</h2>
        <p className={styles.placeholderText}>Controls for LMQL, steering, temperature, max tokens, etc., will go here.</p>
        {/* Placeholder for parameter control components */}
      </div>
    </div>
  );
}
