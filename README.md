# ServerSetup CLI

![Tests](https://github.com/Manueh9/ServerSetup_CLI/actions/workflows/tests.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/serverforge-cli)](https://pypi.org/project/serverforge-cli/)
![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

🇪🇸 Español · [🇬🇧 English](README.en.md)

CLI en Python para automatizar la configuración y el hardening inicial de servidores
Linux (Ubuntu Server). Reduce el tiempo de puesta a punto de un servidor nuevo de
horas a minutos, con configuración reproducible, validada y sin pasos manuales
olvidados.

## El problema que resuelve

Preparar un servidor Linux desde cero implica repetir siempre los mismos pasos:
actualizar el sistema, instalar y asegurar SSH, configurar Git, crear usuarios con
permisos, levantar un firewall, proteger contra fuerza bruta, ajustar la zona
horaria... Hacerlo a mano es lento y propenso a errores. ServerSetup CLI empaqueta
todo ese proceso en comandos claros y en un flujo `--all` que deja el servidor
listo en una sola ejecución.

## Instalación rápida

El paquete está publicado en PyPI como [`serverforge-cli`](https://pypi.org/project/serverforge-cli/)
(requiere Python 3.11+).

**Linux / macOS**
```bash
python3 -m pip install --user serverforge-cli
```

**Windows** (PowerShell o CMD)
```powershell
python -m pip install --user serverforge-cli
```

Comprueba la instalación:
```bash
sforge --help
```

El repositorio incluye también `install.sh` (Linux/macOS) e `install.bat`
(Windows), que ejecutan ese mismo comando.

> ⚠️ El paquete se puede instalar en cualquier sistema operativo, pero los
> módulos ejecutan herramientas propias de Ubuntu/Debian (`apt`, `ufw`,
> `systemctl`, `fail2ban`...). Instalarlo en Windows o macOS solo sirve para
> explorar la CLI o para gestionar un servidor remoto por SSH: para aplicar
> la configuración hace falta ejecutar `sforge` **en el propio servidor
> Linux**.

## Setup completo

```bash
sudo sforge --all
```

El flujo `--all` ejecuta por fases y de forma idempotente (no repite lo que ya está
hecho). Las fases con configuración específica del usuario (hostname, usuarios, swap)
son interactivas: preguntan antes de actuar y continúan si respondes que no. Cada
fase se muestra en un panel numerado (`PHASE 1/10`, `PHASE 2/10`...) y queda separada
de la siguiente por una línea divisoria, para poder seguir el progreso de un vistazo.

## Interfaz

Toda la salida está construida con [Rich](https://github.com/Textualize/rich):

- **Ejecución de comandos**: mientras corre un comando del sistema se muestra un
  spinner animado con el comando en gris; al terminar se reemplaza en el sitio por
  un `✔` verde o un `✘` rojo (con el `stderr` debajo si falló).
- **Estados** (`--swap-status`, `--ufw-status`, `--fail2ban-status`, `--show-ntp`):
  se muestran como tablas clave/valor en vez de líneas de texto sueltas.
- **Listados** (`--list-users`, `--list-cron`, reglas de `--ufw-status`): se
  muestran como tablas con columnas.
- **Uso de swap**: `--swap-status` incluye una barra de progreso coloreada
  (verde/amarillo/rojo según el porcentaje usado).
- **Mensajes**: `✔` éxito, `ℹ` información, `⚠` aviso, `✘` error — consistentes en
  todos los módulos.

## Ayuda

```bash
sforge --help            # resumen de los 11 módulos disponibles
sforge --help ssh        # todos los flags de un módulo concreto
sforge --help git
```

`--help` sin argumentos muestra solo la lista de módulos con una descripción de una
línea cada uno, en vez de volcar los ~70 flags de golpe. Para ver el detalle
completo de un módulo (todos sus flags con su descripción) se pide explícitamente
con `--help <módulo>`.

## Módulos

### 1. Sistema
```bash
sforge --update          # apt update
sforge --upgrade         # apt upgrade -y
sforge --full-upgrade    # apt full-upgrade -y
```

### 2. SSH
```bash
sudo sforge --ssh                    # instalar, habilitar y verificar
sudo sforge --ssh --ssh-port 2222    # instalar y cambiar el puerto
```

### 3. Git
```bash
sforge --install-git
sforge --git-config --git-name "Nombre" --git-email "mail@ejemplo.com"
sforge --git-config --git-scope system --git-name "..." --git-email "..."
sforge --git-config --git-editor nano --git-branch main --git-pull rebase
sforge --git-ssh --git-email "mail@ejemplo.com" --ssh-key-type ed25519
sforge --git-show
```

### 4. Personalización del prompt
```bash
sforge --show-branch     # rama git + estado del repo
sforge --show-time       # timestamp [HH:MM:SS]
sforge --show-venv       # nombre del virtualenv activo
sforge --prompt-status   # ver qué personalizaciones están activas
sforge --remove-branch   # (y --remove-time, --remove-venv)
```

### 5. Timezone
```bash
sforge --show-timezone
sforge --list-timezones-region Europe
sudo sforge --set-timezone Europe/Madrid
sudo sforge --enable-ntp        # sincronización automática del reloj
sforge --show-ntp
```

### 6. UFW (firewall)
```bash
sudo sforge --install-ufw
sudo sforge --allow-port 22 --protocol tcp
sudo sforge --enable-ufw
sudo sforge --ufw-status --ufw-verbose
sudo sforge --deny-port 8080
sudo sforge --delete-rule 22
```

### 7. fail2ban (protección contra fuerza bruta)
```bash
sudo sforge --install-fail2ban
sudo sforge --protect-ssh --max-retry 3 --ban-time 30m
sudo sforge --enable-fail2ban
sudo sforge --fail2ban-status --jail sshd
```

### 8. Hostname
```bash
sforge --show-hostname
sudo sforge --set-hostname web-prod-01
```

### 9. Usuarios
```bash
sudo sforge --create-user devuser --user-password "..."
sudo sforge --grant-sudo devuser
sudo sforge --revoke-sudo devuser
sudo sforge --add-ssh-key devuser --ssh-key "ssh-ed25519 AAAA..."
sudo sforge --list-users
sudo sforge --user-info devuser
sudo sforge --delete-user devuser --keep-home
```

### 10. Cron
```bash
sforge --add-cron "0 3 * * *" --cron-command "/home/devuser/backup.sh" --cron-comment "Daily backup"
sforge --list-cron
sforge --list-cron-cli          # solo tareas gestionadas por la CLI
sforge --remove-cron 1
sforge --remove-cron-cli
sforge --clear-cron             # elimina TODAS las tareas, con cuidado
```

### 11. Swap
```bash
sudo sforge --create-swap          # 2G por defecto
sudo sforge --create-swap 1G
sudo sforge --swap-status
sudo sforge --swappiness 10        # recomendado para servidores
sudo sforge --disable-swap
sudo sforge --remove-swap
```

## Qué incluye el flujo `--all`

| Fase | Módulo | Comportamiento |
|------|--------|----------------|
| 1 | Sistema | Actualiza paquetes |
| 2 | SSH | Instala y asegura SSH |
| 3 | Git | Instala + configuración base |
| 4 | Prompt | Aplica personalizaciones |
| 5 | UFW | Instala, permite SSH y activa |
| 6 | fail2ban | Instala y protege SSH |
| 7 | Hostname | Pregunta si cambiar (interactivo) |
| 8 | Usuarios | Pregunta si crear uno (interactivo) |
| 9 | Swap | Pregunta si crear (interactivo) |

Timezone y Cron se gestionan de forma manual: la zona horaria es demasiado
específica para asumir un valor por defecto, y las tareas cron son demasiado
particulares como para automatizarlas dentro de `--all`.

## Arquitectura

```
src/serverforge_cli/
├── cli.py               → punto de entrada (sforge), orquesta --all por
│                           fases y resuelve --help (resumen + detalle)
├── commands/             → parsea argumentos y decide qué ejecutar
│   ├── system.py
│   ├── ssh.py
│   ├── git.py
│   ├── command_line_custom.py
│   ├── timezone.py
│   ├── ufw.py
│   ├── fail2ban.py
│   ├── hostname.py
│   ├── users.py
│   ├── cron.py
│   └── swap.py
├── modules/              → lógica real, ejecuta comandos del sistema
│   └── (un archivo por cada comando anterior)
└── utils.py              → helpers compartidos basados en Rich (mensajes
                            con iconos, tablas de estado/listados, barra de
                            uso, spinner de ejecución, detección del
                            usuario real tras sudo)
pyproject.toml           → metadatos del paquete, dependencias y el
                            entry point `sforge`
tests/                    → suite de tests con pytest + mocks
```

Cada capa tiene una única responsabilidad. `cli.py` no sabe qué hace cada módulo;
`commands/` no sabe cómo se ejecutan los comandos del sistema; `modules/` no sabe
nada de argparse ni de la CLI. Añadir un módulo nuevo consiste en crear su par
`commands/x.py` + `modules/x.py` y registrarlo en `commands/__init__.py`, sin tocar
el resto.

Un detalle de diseño importante: cuando la CLI se ejecuta con `sudo`, los módulos
que configuran cosas a nivel de usuario (Git, Cron) detectan el usuario real
mediante `SUDO_USER` y actúan sobre su configuración, no sobre la de root.

## Desarrollo

Para modificar el código o contribuir, instala el proyecto en modo editable
desde el repositorio clonado:

```bash
git clone https://github.com/Manueh9/ServerSetup_CLI
cd ServerSetup_CLI
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

Esto instala `serverforge-cli` en modo editable junto con las dependencias de
desarrollo (`pytest`, `pytest-mock`, `pytest-cov`).

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=serverforge_cli --cov-report=term-missing
```

Los tests mockean todas las llamadas al sistema (`apt`, `systemctl`, `git config`,
`crontab`, `swapon`...) para poder ejecutarse en cualquier máquina sin privilegios
root y sin modificar el sistema real. La lógica pura (validación de puertos,
hostnames, esquemas cron, parseo de archivos de configuración) se testea de forma
directa. El CI en GitHub Actions ejecuta la suite completa en Python 3.11 y 3.12
en cada push a `main` y `develop`.

## Seguridad

- **UFW**: el flujo `--all` permite el puerto SSH *antes* de activar el firewall,
  para no bloquear el acceso remoto al servidor.
- **Puertos privilegiados**: se avisa al abrir puertos por debajo de 1024.
- **Validación**: usernames, hostnames, puertos, tamaños de swap y esquemas cron
  se validan antes de aplicarse.
