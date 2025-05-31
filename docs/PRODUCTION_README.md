# TauTranslator Production Deployment Guide
==========================================

## Overview

TauTranslator is now production-ready with the following improvements:

- ✅ Consolidated production translator (`production_translator.py`)
- ✅ Comprehensive dependency management (`production_requirements.txt`)
- ✅ Docker containerization support
- ✅ Production logging configuration
- ✅ Proper error handling and fallback mechanisms
- ✅ Removed debug code and TODO comments
- ✅ Fixed NotImplementedError cases

## Quick Start

### 1. Local Deployment

```bash
# Install dependencies and start all services
./start_production.sh

# Or start specific components:
./start_production.sh api    # API server only
./start_production.sh web    # Web interface only
./start_production.sh test   # Run tests
```

### 2. Docker Deployment

```bash
# Build and start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Command Line Usage

```bash
# Install dependencies
pip install -r production_requirements.txt

# Translate Tau to TCE
python production_translator.py "always x & y" -d tau_to_tce

# Translate TCE to Tau
python production_translator.py "Always x AND y." -d tce_to_tau

# Translate from file
python production_translator.py -f input.tau -o output.tce

# JSON output
python production_translator.py "r o1[t] = i1[t] & i2[t]" --json
```

## Production Features

### 1. Error Handling
- Graceful fallback when LMQL is not available
- Pattern-based translation as backup
- Comprehensive error logging
- Input validation

### 2. Logging
- Structured logging with rotation
- Separate error logs
- JSON format support
- Configurable log levels

### 3. Security
- API key encryption support
- Environment variable configuration
- Non-root Docker user
- Health checks

### 4. Deployment Options
- Standalone CLI
- Web interface (Flask)
- REST API (FastAPI)
- Docker containers
- Kubernetes-ready

## Configuration

### Environment Variables

```bash
export TAU_LOG_LEVEL=INFO          # Log level (DEBUG, INFO, WARNING, ERROR)
export TAU_DEFAULT_MODEL=gpt-3.5-turbo  # Default LLM model
export TAU_API_TIMEOUT=30          # API timeout in seconds
export TAU_LOG_JSON=true           # Enable JSON logging
```

### API Endpoints

- **Health Check**: `GET /health`
- **Translate**: `POST /translate`
  ```json
  {
    "text": "always x & y",
    "direction": "tau_to_tce"
  }
  ```

### Web Interface

Access at `http://localhost:5000` after starting the web service.

## Monitoring

### Logs
- Application logs: `logs/tau_translator.log`
- Error logs: `logs/tau_translator_error.log`
- Docker logs: `docker-compose logs`

### Health Checks
- API: `curl http://localhost:8000/health`
- Web: `curl http://localhost:5000/`

## Troubleshooting

### Missing Dependencies
```bash
pip install -r production_requirements.txt
```

### LMQL Not Available
The system will automatically fall back to pattern-based translation.

### Port Conflicts
Change ports in `docker-compose.yml` or use environment variables:
```bash
API_PORT=8001 WEB_PORT=5001 ./start_production.sh
```

## Performance Considerations

1. **Caching**: Redis is configured in docker-compose.yml for caching
2. **Workers**: Configure Gunicorn/Uvicorn workers based on CPU cores
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Monitoring**: Prometheus metrics endpoint available

## Security Best Practices

1. Always use HTTPS in production (nginx configured)
2. Set strong API keys and rotate regularly
3. Enable authentication for sensitive endpoints
4. Regular security updates

## Support

For issues or questions:
- GitHub Issues: [Report issues](https://github.com/tau-translator/issues)
- Documentation: See `/docs` directory
- API Docs: `http://localhost:8000/docs` (when API is running)