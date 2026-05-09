# OpenDockerWebUI

A Docker Compose demo that recreates a Docker Desktop-like UI with:

- FastAPI backend
- Vue 3 frontend
- Docker Desktop-style navigation
- Containers table
- Images page
- Volumes page
- Builds page placeholder
- Settings page
- Docker Engine status API

## Start

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

## API

```text
GET /health
GET /docker/info
GET /docker/containers
GET /docker/images
GET /docker/volumes
```

## Security

This demo mounts the Docker socket:

```yaml
/var/run/docker.sock:/var/run/docker.sock
```

Do not expose this backend publicly without authentication and authorization.
# open-dockerui
