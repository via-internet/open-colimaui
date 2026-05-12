# OpenColimaUI

Colima-powered container management UI — Vue/FastAPI, styled after Docker Desktop.

## Prerequisites

Install and start [Colima](https://github.com/abiosoft/colima):

```bash
brew install colima        # macOS
colima start               # starts the Lima VM + container runtime
```

Set the socket path (add to your shell profile):

```bash
export COLIMA_SOCKET_PATH="$HOME/.colima/default/docker.sock"
```

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

## Colima socket

The backend mounts the Colima socket into the container via the `COLIMA_SOCKET_PATH`
environment variable (defaults to `$HOME/.colima/default/docker.sock`).

```bash
# override if you use a named Colima profile
export COLIMA_SOCKET_PATH="$HOME/.colima/myprofile/docker.sock"
docker compose up --build
```

The `DOCKER_HOST` env var is set automatically inside the backend container so the
Python Docker SDK connects to Colima's socket.

## Justfile shortcuts

```bash
just colima-start   # colima start
just colima-stop    # colima stop
just colima-status  # colima status
just up             # docker compose up --build
just api-info       # curl /colima/info
```

## Security

The backend mounts the Colima socket, which gives privileged access to the container runtime.
