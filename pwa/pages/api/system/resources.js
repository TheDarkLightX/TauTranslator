import os from 'os';
import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    // Get system resources
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const usedMemory = totalMemory - freeMemory;
    
    const cpus = os.cpus();
    const cpuCount = cpus.length;
    const cpuModel = cpus[0]?.model || 'Unknown';
    
    // Check available disk space
    let diskSpace = null;
    try {
      const stats = fs.statSync(process.cwd());
      diskSpace = {
        total: 'Unknown',
        free: 'Unknown',
        used: 'Unknown'
      };
    } catch (error) {
      diskSpace = {
        total: 'Unknown',
        free: 'Unknown', 
        used: 'Unknown'
      };
    }

    // Check for GPU (basic check)
    const platform = os.platform();
    let gpuInfo = {
      available: false,
      type: 'Unknown',
      memory: 'Unknown'
    };

    // Check if CUDA is available (basic check)
    try {
      // This is a simplified check - in a real implementation, 
      // you'd use proper GPU detection libraries
      gpuInfo = {
        available: false,
        type: 'Detection not implemented',
        memory: 'Unknown'
      };
    } catch (error) {
      // GPU detection failed
    }

    // Check for model storage directory
    const modelsDir = path.join(process.cwd(), '../models');
    let modelStorage = {
      path: modelsDir,
      exists: fs.existsSync(modelsDir),
      size: 0
    };

    if (modelStorage.exists) {
      try {
        const getDirectorySize = (dirPath) => {
          let totalSize = 0;
          const files = fs.readdirSync(dirPath);
          
          for (const file of files) {
            const filePath = path.join(dirPath, file);
            const stats = fs.statSync(filePath);
            
            if (stats.isDirectory()) {
              totalSize += getDirectorySize(filePath);
            } else {
              totalSize += stats.size;
            }
          }
          
          return totalSize;
        };

        modelStorage.size = getDirectorySize(modelsDir);
      } catch (error) {
        modelStorage.size = 0;
      }
    }

    const systemResources = {
      memory: {
        total: Math.round(totalMemory / 1024 / 1024 / 1024 * 100) / 100, // GB
        used: Math.round(usedMemory / 1024 / 1024 / 1024 * 100) / 100,   // GB
        free: Math.round(freeMemory / 1024 / 1024 / 1024 * 100) / 100,   // GB
        usage: Math.round((usedMemory / totalMemory) * 100)               // %
      },
      cpu: {
        count: cpuCount,
        model: cpuModel,
        platform: platform,
        arch: os.arch()
      },
      disk: diskSpace,
      gpu: gpuInfo,
      modelStorage,
      uptime: Math.round(os.uptime()),
      nodeVersion: process.version,
      timestamp: new Date().toISOString()
    };

    res.status(200).json(systemResources);

  } catch (error) {
    console.error('System resources API error:', error);
    res.status(500).json({ 
      error: 'Failed to get system resources',
      message: error.message 
    });
  }
}