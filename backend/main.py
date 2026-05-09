from __future__ import annotations

import html
import os
from typing import Any

import docker
from docker.errors import DockerException, ImageNotFound, NotFound
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


class RunImageRequest(BaseModel):
    image: str
    name: str | None = None
    detach: bool = True


def cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [item.strip() for item in raw.split(",") if item.strip()]


app = FastAPI(title="OpenDockerWebUI API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_docker_client():
    try:
        return docker.from_env()
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=f"Docker unavailable: {exc}") from exc


def get_container_or_404(container_id: str):
    client = get_docker_client()
    try:
        return client.containers.get(container_id)
    except NotFound as exc:
        raise HTTPException(status_code=404, detail=f"Container not found: {container_id}") from exc
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def image_name(container: Any) -> str:
    try:
        tags = container.image.tags
        if tags:
            return tags[0]
        return container.image.short_id
    except Exception:
        return "unknown"


def image_display_parts(tags: list[str]) -> tuple[str, str]:
    if not tags:
        return "<none>", "<none>"
    tag = tags[0]
    if ":" in tag:
        name, version = tag.rsplit(":", 1)
        return name, version
    return tag, "latest"


def project_name(container: Any) -> str | None:
    labels = container.attrs.get("Config", {}).get("Labels") or {}
    return labels.get("com.docker.compose.project")


def service_name(container: Any) -> str | None:
    labels = container.attrs.get("Config", {}).get("Labels") or {}
    return labels.get("com.docker.compose.service")


def port_links(ports: dict[str, Any] | None) -> list[dict[str, str]]:
    if not ports:
        return []

    links: list[dict[str, str]] = []
    for container_port, bindings in ports.items():
        if not bindings:
            continue
        for binding in bindings:
            host_ip = binding.get("HostIp") or "localhost"
            host_port = binding.get("HostPort")
            if not host_port:
                continue
            display_ip = "localhost" if host_ip in {"0.0.0.0", "::"} else host_ip
            links.append(
                {
                    "host": display_ip,
                    "host_port": str(host_port),
                    "container_port": container_port,
                    "label": f"{host_port}:{container_port.split('/')[0]}",
                    "url": f"http://{display_ip}:{host_port}",
                }
            )
    return links


def port_summary(ports: dict[str, Any] | None) -> str:
    links = port_links(ports)
    return ", ".join(item["label"] for item in links) if links else "-"


def format_bytes(size: int | None) -> str:
    if not size:
        return "0 Bytes"
    units = ["Bytes", "kB", "MB", "GB", "TB"]
    value = float(size)
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    return f"{value:.1f} {units[unit_index]}"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/docker/info")
def docker_info() -> dict[str, Any]:
    client = get_docker_client()

    try:
        info = client.info()
        version = client.version()

        return {
            "status": "online",
            "server_version": version.get("Version"),
            "api_version": version.get("ApiVersion"),
            "os": info.get("OperatingSystem"),
            "architecture": info.get("Architecture"),
            "containers": info.get("Containers", 0),
            "containers_running": info.get("ContainersRunning", 0),
            "containers_paused": info.get("ContainersPaused", 0),
            "containers_stopped": info.get("ContainersStopped", 0),
            "images": info.get("Images", 0),
            "cpus": info.get("NCPU", 0),
            "memory_total": info.get("MemTotal", 0),
            "docker_root_dir": info.get("DockerRootDir"),
            "kernel_version": info.get("KernelVersion"),
        }
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/docker/containers")
def docker_containers() -> list[dict[str, Any]]:
    client = get_docker_client()

    try:
        containers = client.containers.list(all=True)
        result = []

        for container in containers:
            attrs = container.attrs or {}
            state = attrs.get("State", {})
            network_settings = attrs.get("NetworkSettings", {})
            ports = network_settings.get("Ports") or {}

            result.append(
                {
                    "id": container.short_id,
                    "full_id": container.id,
                    "name": container.name,
                    "image": image_name(container),
                    "status": container.status,
                    "created": attrs.get("Created"),
                    "ports": ports,
                    "port_links": port_links(ports),
                    "ports_text": port_summary(ports),
                    "console_url": f"/docker/containers/{container.id}/console",
                    "project": project_name(container),
                    "service": service_name(container),
                    "cpu_percent": 0,
                    "memory_usage": None,
                    "last_started": state.get("StartedAt"),
                    "state": {
                        "running": state.get("Running", False),
                        "paused": state.get("Paused", False),
                        "restarting": state.get("Restarting", False),
                        "started_at": state.get("StartedAt"),
                        "finished_at": state.get("FinishedAt"),
                        "exit_code": state.get("ExitCode"),
                    },
                }
            )

        return result

    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/docker/containers/{container_id}/start")
def start_container(container_id: str) -> dict[str, str]:
    container = get_container_or_404(container_id)
    try:
        container.start()
        return {"status": "started", "container": container.name}
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/docker/containers/{container_id}/stop")
def stop_container(container_id: str) -> dict[str, str]:
    container = get_container_or_404(container_id)
    try:
        container.stop(timeout=10)
        return {"status": "stopped", "container": container.name}
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/docker/containers/{container_id}/console", response_class=HTMLResponse)
def container_console(container_id: str) -> str:
    container = get_container_or_404(container_id)
    safe_name = html.escape(container.name)
    safe_id = html.escape(container.id)
    sh_command = html.escape(f"docker exec -it {container.name} sh")
    bash_command = html.escape(f"docker exec -it {container.name} bash")

    return f"""
    <!doctype html>
    <html>
      <head>
        <title>Console - {safe_name}</title>
        <style>
          body {{
            margin: 0;
            padding: 32px;
            background: #0f172a;
            color: #e5e7eb;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
          }}
          .card {{
            max-width: 980px;
            background: #111827;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 24px;
          }}
          h1 {{ margin-top: 0; }}
          code {{
            display: block;
            padding: 16px;
            margin: 12px 0;
            background: #020617;
            border-radius: 10px;
            color: #93c5fd;
            font-size: 18px;
          }}
          p {{ color: #cbd5e1; line-height: 1.6; }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Container console: {safe_name}</h1>
          <p>Browser terminals require a WebSocket exec bridge. For this demo, copy one of these commands into your local terminal:</p>
          <code>{sh_command}</code>
          <code>{bash_command}</code>
          <p>Container ID: {safe_id}</p>
        </div>
      </body>
    </html>
    """


@app.get("/docker/images")
def docker_images() -> list[dict[str, Any]]:
    client = get_docker_client()

    try:
        images = client.images.list()
        result = []

        for image in images:
            name, tag = image_display_parts(image.tags)
            result.append(
                {
                    "id": image.short_id,
                    "full_id": image.id,
                    "name": name,
                    "tag": tag,
                    "tags": image.tags,
                    "created": image.attrs.get("Created"),
                    "size": image.attrs.get("Size"),
                    "size_text": format_bytes(image.attrs.get("Size")),
                }
            )

        return result
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/docker/images/run")
def run_image(payload: RunImageRequest) -> dict[str, Any]:
    client = get_docker_client()

    try:
        container = client.containers.run(
            image=payload.image,
            name=payload.name,
            detach=payload.detach,
        )
        return {
            "status": "running",
            "container_id": container.short_id,
            "container_name": container.name,
        }
    except ImageNotFound as exc:
        raise HTTPException(status_code=404, detail=f"Image not found: {payload.image}") from exc
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/docker/volumes")
def docker_volumes() -> list[dict[str, Any]]:
    client = get_docker_client()

    try:
        volumes = client.volumes.list()
        return [
            {
                "name": volume.name,
                "driver": volume.attrs.get("Driver"),
                "mountpoint": volume.attrs.get("Mountpoint"),
                "created_at": volume.attrs.get("CreatedAt"),
                "labels": volume.attrs.get("Labels") or {},
                "size_text": "0 Bytes",
                "in_use": bool(volume.attrs.get("Labels")),
            }
            for volume in volumes
        ]
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
