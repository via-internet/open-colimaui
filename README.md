# OpenDockerWebUI Actions UI

Docker Desktop-style Vue/FastAPI demo.

## Added actions

- Containers:
  - Ports are links and open in a new tab.
  - Container names open a browser page with `docker exec` console commands.
  - Running containers can be stopped.
  - Stopped containers can be started.

- Images:
  - Image rows have a Run action.

## Start

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

## Security

The backend mounts `/var/run/docker.sock`, which gives privileged Docker host access.
