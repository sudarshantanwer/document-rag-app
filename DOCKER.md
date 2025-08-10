# Docker Setup for Document RAG App

This directory contains Docker configuration files to run the entire Document RAG application stack.

## Services

- **Frontend**: React application (port 3000)
- **Backend**: FastAPI application (port 8000)
- **Database**: PostgreSQL with pgvector extension (port 5432)

## Quick Start

1. **Set up environment variables:**
   ```bash
   cp .env.docker .env
   # Edit .env file and add your OpenAI API key and other required values
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Mode

For development with hot reload:

```bash
docker-compose up --build
```

The volumes are configured to mount your local code, so changes will be reflected automatically.

## Production Build

For a production build of the frontend:

1. Update the frontend Dockerfile to use a multi-stage build
2. Set appropriate environment variables
3. Use production-ready database credentials

## Database

The PostgreSQL database includes the pgvector extension for vector operations. The database data is persisted using Docker volumes.

## Stopping Services

```bash
docker-compose down
```

To also remove volumes (this will delete all data):

```bash
docker-compose down -v
```

## Troubleshooting

1. **Database connection issues**: Ensure the database service is healthy before backend starts
2. **CORS issues**: Check that the backend CORS settings match your frontend URL
3. **Environment variables**: Verify all required environment variables are set in `.env`

## Environment Variables

Required:
- `OPENAI_API_KEY`: Your OpenAI API key

Optional:
- `HUGGINGFACEHUB_API_TOKEN`: For HuggingFace embeddings
