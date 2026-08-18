# ServerSetup CLI

![Tests](https://github.com/Manueh9/ServerSetup_CLI/actions/workflows/tests.yml/badge.svg)
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

## Instalación

```bash
git clone https://github.com/Manueh9/ServerSetup_CLI
cd ServerSetup_CLI
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Setup completo

```bash
sudo python3 cli.py --all
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
python3 cli.py --help            # resumen de los 11 módulos disponibles
python3 cli.py --help ssh        # todos los flags de un módulo concreto
python3 cli.py --help git
```

`--help` sin argumentos muestra solo la lista de módulos con una descripción de una
línea cada uno, en vez de volcar los ~70 flags de golpe. Para ver el detalle
completo de un módulo (todos sus flags con su descripción) se pide explícitamente
con `--help <módulo>`.

## Módulos

### 1. Sistema
```bash
python3 cli.py --update          # apt update
python3 cli.py --upgrade         # apt upgrade -y
python3 cli.py --full-upgrade    # apt full-upgrade -y
```

### 2. SSH
```bash
sudo python3 cli.py --ssh                    # instalar, habilitar y verificar
sudo python3 cli.py --ssh --ssh-port 2222    # instalar y cambiar el puerto
```

### 3. Git
```bash
python3 cli.py --install-git
python3 cli.py --git-config --git-name "Nombre" --git-email "mail@ejemplo.com"
python3 cli.py --git-config --git-scope system --git-name "..." --git-email "..."
python3 cli.py --git-config --git-editor nano --git-branch main --git-pull rebase
python3 cli.py --git-ssh --git-email "mail@ejemplo.com" --ssh-key-type ed25519
python3 cli.py --git-show
```

### 4. Personalización del prompt
```bash
python3 cli.py --show-branch     # rama git + estado del repo
python3 cli.py --show-time       # timestamp [HH:MM:SS]
python3 cli.py --show-venv       # nombre del virtualenv activo
python3 cli.py --prompt-status   # ver qué personalizaciones están activas
python3 cli.py --remove-branch   # (y --remove-time, --remove-venv)
```

### 5. Timezone
```bash
python3 cli.py --show-timezone
python3 cli.py --list-timezones-region Europe
sudo python3 cli.py --set-timezone Europe/Madrid
sudo python3 cli.py --enable-ntp        # sincronización automática del reloj
python3 cli.py --show-ntp
```

### 6. UFW (firewall)
```bash
sudo python3 cli.py --install-ufw
sudo python3 cli.py --allow-port 22 --protocol tcp
sudo python3 cli.py --enable-ufw
sudo python3 cli.py --ufw-status --ufw-verbose
sudo python3 cli.py --deny-port 8080
sudo python3 cli.py --delete-rule 22
```

### 7. fail2ban (protección contra fuerza bruta)
```bash
sudo python3 cli.py --install-fail2ban
sudo python3 cli.py --protect-ssh --max-retry 3 --ban-time 30m
sudo python3 cli.py --enable-fail2ban
sudo python3 cli.py --fail2ban-status --jail sshd
```

### 8. Hostname
```bash
python3 cli.py --show-hostname
sudo python3 cli.py --set-hostname web-prod-01
```

### 9. Usuarios
```bash
sudo python3 cli.py --create-user devuser --user-password "..."
sudo python3 cli.py --grant-sudo devuser
sudo python3 cli.py --revoke-sudo devuser
sudo python3 cli.py --add-ssh-key devuser --ssh-key "ssh-ed25519 AAAA..."
sudo python3 cli.py --list-users
sudo python3 cli.py --user-info devuser
sudo python3 cli.py --delete-user devuser --keep-home
```

### 10. Cron
```bash
python3 cli.py --add-cron "0 3 * * *" --cron-command "/home/devuser/backup.sh" --cron-comment "Daily backup"
python3 cli.py --list-cron
python3 cli.py --list-cron-cli          # solo tareas gestionadas por la CLI
python3 cli.py --remove-cron 1
python3 cli.py --remove-cron-cli
python3 cli.py --clear-cron             # elimina TODAS las tareas, con cuidado
```

### 11. Swap
```bash
sudo python3 cli.py --create-swap          # 2G por defecto
sudo python3 cli.py --create-swap 1G
sudo python3 cli.py --swap-status
sudo python3 cli.py --swappiness 10        # recomendado para servidores
sudo python3 cli.py --disable-swap
sudo python3 cli.py --remove-swap
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
cli.py                  → punto de entrada, orquesta --all por fases y
                           resuelve --help (resumen + detalle por módulo)
commands/                → parsea argumentos y decide qué ejecutar
  ├── system.py
  ├── ssh.py
  ├── git.py
  ├── command_line_custom.py
  ├── timezone.py
  ├── ufw.py
  ├── fail2ban.py
  ├── hostname.py
  ├── users.py
  ├── cron.py
  └── swap.py
modules/                 → lógica real, ejecuta comandos del sistema
  └── (un archivo por cada comando anterior)
utils.py                 → helpers compartidos basados en Rich (mensajes con
                           iconos, tablas de estado/listados, barra de uso,
                           spinner de ejecución, detección del usuario real
                           tras sudo)
tests/                   → suite de tests con pytest + mocks
```

Cada capa tiene una única responsabilidad. `cli.py` no sabe qué hace cada módulo;
`commands/` no sabe cómo se ejecutan los comandos del sistema; `modules/` no sabe
nada de argparse ni de la CLI. Añadir un módulo nuevo consiste en crear su par
`commands/x.py` + `modules/x.py` y registrarlo en `commands/__init__.py`, sin tocar
el resto.

Un detalle de diseño importante: cuando la CLI se ejecuta con `sudo`, los módulos
que configuran cosas a nivel de usuario (Git, Cron) detectan el usuario real
mediante `SUDO_USER` y actúan sobre su configuración, no sobre la de root.

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=modules --cov-report=term-missing
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
