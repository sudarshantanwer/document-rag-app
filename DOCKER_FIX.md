# Fix for ModuleNotFoundError: No module named 'slowapi'

## Problem
When running the FastAPI application in Docker or environments without `slowapi` installed, you may encounter:

```
ModuleNotFoundError: No module named 'slowapi'
```

## Solution

### Option 1: Install Optional Dependencies (Recommended for Production)
```bash
pip install slowapi redis aioredis
```

Or use the production requirements:
```bash
pip install -r requirements-prod.txt
```

### Option 2: Use Without Enhanced Rate Limiting
The application will work without `slowapi` and `redis` dependencies:
- Basic rate limiting will use in-memory storage
- All other performance features remain functional
- Just install basic requirements: `pip install -r requirements.txt`

## Docker Solutions

### Basic Docker Build (without slowapi/redis):
```bash
docker build -t document-rag-backend .
```

### Production Docker Build (with all performance features):
```bash
docker build --build-arg INSTALL_PROD=true -t document-rag-backend-prod .
```

## What Changes Were Made
1. Made `slowapi` and `redis` imports optional with try/except blocks
2. Created fallback implementations for rate limiting
3. Added graceful degradation when dependencies are missing
4. Split requirements into basic and production versions

## Features Available Without Optional Dependencies
✅ Health endpoint  
✅ Performance middleware (timing, CORS, GZIP)  
✅ Async optimization utilities  
✅ Basic rate limiting (in-memory)  
✅ All core API functionality  

## Enhanced Features (require optional dependencies)
🔧 Redis-backed rate limiting  
🔧 SlowAPI decorator-based rate limiting  
🔧 Distributed rate limiting across multiple instances  

The application is fully functional without optional dependencies!
