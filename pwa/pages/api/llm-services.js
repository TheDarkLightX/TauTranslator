import fs from 'fs';
import path from 'path';

const LLM_SERVICES_FILE = path.join(process.cwd(), '../config/llm-services.json');

// Ensure config directory exists
const ensureConfigDir = () => {
  const configDir = path.dirname(LLM_SERVICES_FILE);
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
};

// Load LLM services from file
const loadServices = () => {
  try {
    if (fs.existsSync(LLM_SERVICES_FILE)) {
      const data = fs.readFileSync(LLM_SERVICES_FILE, 'utf8');
      return JSON.parse(data);
    }
    return [];
  } catch (error) {
    console.error('Error loading LLM services:', error);
    return [];
  }
};

// Save LLM services to file
const saveServices = (services) => {
  try {
    ensureConfigDir();
    fs.writeFileSync(LLM_SERVICES_FILE, JSON.stringify(services, null, 2));
    return true;
  } catch (error) {
    console.error('Error saving LLM services:', error);
    return false;
  }
};

// Generate unique ID
const generateId = () => {
  return Date.now().toString() + Math.random().toString(36).substr(2, 9);
};

export default async function handler(req, res) {
  const { method } = req;
  const { id } = req.query;

  try {
    switch (method) {
      case 'GET':
        // Get all LLM services
        const allServices = loadServices();
        res.status(200).json(allServices);
        break;

      case 'POST':
        if (id === 'set-default') {
          // Set default service
          const defaultServices = loadServices();
          const serviceIndex = defaultServices.findIndex(s => s.id === req.query.serviceId);
          
          if (serviceIndex === -1) {
            return res.status(404).json({ message: 'Service not found' });
          }

          // Remove default from all services
          defaultServices.forEach(service => {
            service.isDefault = false;
          });

          // Set new default
          defaultServices[serviceIndex].isDefault = true;

          if (saveServices(defaultServices)) {
            res.status(200).json({ message: 'Default service updated' });
          } else {
            res.status(500).json({ message: 'Failed to save services' });
          }
        } else {
          // Create new LLM service
          const { name, provider, apiKey, baseUrl, model, description, maxTokens, temperature } = req.body;

          if (!name || !provider) {
            return res.status(400).json({ message: 'Name and provider are required' });
          }

          const currentServices = loadServices();
          const newService = {
            id: generateId(),
            name,
            provider,
            apiKey: apiKey || '',
            baseUrl: baseUrl || '',
            model: model || '',
            description: description || '',
            maxTokens: maxTokens || 2048,
            temperature: temperature || 0.7,
            isDefault: currentServices.length === 0, // First service becomes default
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          };

          currentServices.push(newService);

          if (saveServices(currentServices)) {
            res.status(201).json(newService);
          } else {
            res.status(500).json({ message: 'Failed to save service' });
          }
        }
        break;

      case 'PUT':
        // Update existing LLM service
        if (!id) {
          return res.status(400).json({ message: 'Service ID is required' });
        }

        const updateServices = loadServices();
        const serviceIndex = updateServices.findIndex(s => s.id === id);

        if (serviceIndex === -1) {
          return res.status(404).json({ message: 'Service not found' });
        }

        const { name, provider, apiKey, baseUrl, model, description, maxTokens, temperature } = req.body;

        updateServices[serviceIndex] = {
          ...updateServices[serviceIndex],
          name: name || updateServices[serviceIndex].name,
          provider: provider || updateServices[serviceIndex].provider,
          apiKey: apiKey !== undefined ? apiKey : updateServices[serviceIndex].apiKey,
          baseUrl: baseUrl !== undefined ? baseUrl : updateServices[serviceIndex].baseUrl,
          model: model !== undefined ? model : updateServices[serviceIndex].model,
          description: description !== undefined ? description : updateServices[serviceIndex].description,
          maxTokens: maxTokens !== undefined ? maxTokens : updateServices[serviceIndex].maxTokens,
          temperature: temperature !== undefined ? temperature : updateServices[serviceIndex].temperature,
          updatedAt: new Date().toISOString()
        };

        if (saveServices(updateServices)) {
          res.status(200).json(updateServices[serviceIndex]);
        } else {
          res.status(500).json({ message: 'Failed to update service' });
        }
        break;

      case 'DELETE':
        // Delete LLM service
        if (!id) {
          return res.status(400).json({ message: 'Service ID is required' });
        }

        const deleteServices = loadServices();
        const filteredServices = deleteServices.filter(s => s.id !== id);

        if (filteredServices.length === deleteServices.length) {
          return res.status(404).json({ message: 'Service not found' });
        }

        if (saveServices(filteredServices)) {
          res.status(200).json({ message: 'Service deleted successfully' });
        } else {
          res.status(500).json({ message: 'Failed to delete service' });
        }
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.error('LLM Services API error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}