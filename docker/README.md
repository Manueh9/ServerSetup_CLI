# Probar `sforge` en Docker (sin VM, sin tocar el Mac)

Este contenedor levanta un Ubuntu 24.04 con **systemd real** como PID 1
(`apt`, `systemctl`, `ufw`, `fail2ban-client`, `sshd`... funcionan de
verdad), para poder ejecutar `sforge` tal cual se ejecutaría en un servidor,
sin instalar nada en el host y sin levantar una máquina virtual.

## Requisitos

- Docker Desktop (o Docker Engine) con `docker compose`.

## Uso

```bash
# desde la raíz del repo
docker compose -f docker/docker-compose.yml up -d --build

# abrir una shell dentro del contenedor
docker compose -f docker/docker-compose.yml exec sforge-test bash
```

Dentro del contenedor:

```bash
sforge --help
sudo sforge --all
sudo sforge --protect-ssh --max-retry 3

# comprobar servicios reales
systemctl status fail2ban
ufw status verbose

# o correr la suite de tests (mockeada, no toca el sistema del contenedor)
pytest tests/ -v --cov=serverforge_cli --cov-report=term-missing
```

El repo está montado dentro del contenedor (`/opt/serverforge-cli`), así que
los cambios que hagas en tu editor en el Mac se reflejan sin rebuild —
basta con volver a invocar `sforge` en la shell del contenedor.

## Limpiar todo

```bash
docker compose -f docker/docker-compose.yml down -v
```

Esto elimina el contenedor y sus volúmenes anónimos; no queda ningún rastro
en el Mac más allá de la imagen Docker (bórrala con `docker image rm
docker-sforge-test` si quieres liberar espacio también ahí).
