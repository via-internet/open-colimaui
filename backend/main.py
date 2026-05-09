from __future__ import annotations

import os
from typing import Any

import docker
from docker.errors import DockerException
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


def cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [item.strip() for item in raw.split(",") if item.strip()]


app = FastAPI(title="OpenDockerWebUI API", version="1.0.0")

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


def image_name(container: Any) -> str:
    try:
        tags = container.image.tags
        if tags:
            return tags[0]
        return container.image.short_id
    except Exception:
        return "unknown"


def project_name(container: Any) -> str | None:
    labels = container.attrs.get("Config", {}).get("Labels") or {}
    return labels.get("com.docker.compose.project")


def service_name(container: Any) -> str | None:
    labels = container.attrs.get("Config", {}).get("Labels") or {}
    return labels.get("com.docker.compose.service")


def port_summary(ports: dict[str, Any] | None) -> str:
    if not ports:
        return "-"

    values: list[str] = []
    for container_port, bindings in ports.items():
        if not bindings:
            continue
        for binding in bindings:
            host_port = binding.get("HostPort")
            if host_port:
                values.append(f"{host_port}:{container_port.split('/')[0]}")

    return ", ".join(values) if values else "-"


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
                    "ports_text": port_summary(ports),
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


@app.get("/docker/images")
def docker_images() -> list[dict[str, Any]]:
    client = get_docker_client()

    try:
        images = client.images.list()
        return [
            {
                "id": image.short_id,
                "tags": image.tags,
                "created": image.attrs.get("Created"),
                "size": image.attrs.get("Size"),
            }
            for image in images
        ]
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
            }
            for volume in volumes
        ]
    except DockerException as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
