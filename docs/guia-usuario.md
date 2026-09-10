# Guía de usuario

ServerSetup CLI (`serverforge-cli`) es una herramienta de línea de comandos escrita
en Python para automatizar la configuración inicial y el hardening de servidores
Linux (Ubuntu/Debian): actualización del sistema, SSH, Git, personalización del
prompt, zona horaria, firewall (UFW), fail2ban, hostname, usuarios, tareas cron y
swap.

## 1. Instalación

El paquete está publicado en PyPI como
[`serverforge-cli`](https://pypi.org/project/serverforge-cli/) y requiere
Python 3.11 o superior.

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

El repositorio incluye también dos scripts de conveniencia que ejecutan ese
mismo comando de instalación: `install.sh` (Linux/macOS) e `install.bat`
(Windows).

> ⚠️ **Importante**: el paquete se puede instalar en cualquier sistema
> operativo, pero los módulos ejecutan herramientas propias de Ubuntu/Debian
> (`apt`, `ufw`, `systemctl`, `fail2ban`...). Instalarlo en Windows o macOS
> solo sirve para explorar la CLI o para conectarte a un servidor remoto por
> SSH: para aplicar la configuración hace falta ejecutar `sforge` **en el
> propio servidor Linux**.

### Instalación para desarrollo

Si vas a modificar el código, instala el proyecto en modo editable desde el
repositorio clonado (ver [`arquitectura.md`](arquitectura.md#7-cómo-contribuir-modo-desarrollo)
para más detalle):

```bash
git clone https://github.com/Manueh9/ServerSetup_CLI
cd ServerSetup_CLI
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

## 2. Uso básico

El comando principal es `sforge`. Puede usarse de dos formas:

```bash
sforge --all              # Flujo guiado completo (recomendado en un servidor nuevo)
sforge <flags>            # Ejecutar acciones concretas, una a una
```

Muchas operaciones requieren privilegios de root porque modifican el sistema
(instalar paquetes, editar `/etc/ssh/sshd_config`, gestionar el firewall,
crear usuarios...). En esos casos antepón `sudo`:

```bash
sudo sforge --ssh --ssh-port 2222
sudo sforge --all
```

## 3. Ayuda de dos niveles

`sforge` no vuelca los más de 70 flags disponibles de golpe. La ayuda tiene
dos niveles:

```bash
sforge --help            # resumen: los 11 módulos con una descripción de una línea
sforge --help ssh        # detalle completo de un módulo: todos sus flags
sforge --help git
```

El resumen (`sforge --help` sin argumentos) muestra esta tabla de módulos:

| Módulo     | Qué hace |
|------------|----------|
| `system`   | `apt update` / `upgrade` / `full-upgrade` |
| `ssh`      | Instalar y configurar OpenSSH, cambiar el puerto |
| `git`      | Instalar, configurar usuario/editor/rama, generar clave SSH |
| `prompt`   | Personalizar el prompt de bash (rama git, hora, virtualenv) |
| `timezone` | Zona horaria y sincronización NTP |
| `ufw`      | Reglas del firewall |
| `fail2ban` | Protección contra fuerza bruta |
| `hostname` | Gestión del nombre de host |
| `users`    | Crear/gestionar usuarios, claves SSH, sudo |
| `cron`     | Tareas cron programadas |
| `swap`     | Gestión del archivo de swap |

## 4. El flujo `--all`

```bash
sudo sforge --all
```

Ejecuta 10 fases en orden, de forma **idempotente** (no repite lo que ya está
hecho). Cada fase se muestra en un panel numerado (`PHASE 1/10`, `PHASE
2/10`...) separado del siguiente por una línea divisoria, para seguir el
progreso de un vistazo. Las fases con configuración específica del servidor
(hostname, usuarios, swap) son **interactivas**: preguntan antes de actuar y
continúan sin problema si respondes que no.

| Fase | Módulo | Comportamiento |
|------|--------|-----------------|
| 1 | Sistema | Actualiza paquetes (`apt update && upgrade`) |
| 2 | SSH | Instala y asegura SSH |
| 3 | Git | Instala y aplica configuración base |
| 4 | Prompt | Aplica personalizaciones del prompt |
| 5 | Timezone & NTP | *(ver nota)* |
| 6 | UFW | Instala, permite el puerto SSH y activa el firewall |
| 7 | fail2ban | Instala y protege SSH |
| 8 | Hostname | Pregunta si quieres cambiarlo (interactivo) |
| 9 | Usuarios | Pregunta si quieres crear uno (interactivo) |
| 10 | Swap | Pregunta si quieres crear uno (interactivo) |

**Timezone y Cron se gestionan de forma manual**, fuera de `--all`: la zona
horaria es demasiado específica del servidor como para asumir un valor por
defecto, y las tareas cron son demasiado particulares como para
automatizarlas en un flujo genérico. `cron` ni siquiera aparece como fase
propia de `--all`.

Durante `--all`, UFW permite el puerto SSH **antes** de activar el firewall,
para no bloquear el acceso remoto al servidor mientras se configura.

## 5. Módulos, flags y ejemplos

### 5.1 Sistema
```bash
sforge --update          # apt update
sforge --upgrade         # apt upgrade -y
sforge --full-upgrade    # apt full-upgrade -y
```

### 5.2 SSH
```bash
sudo sforge --ssh                    # instalar, habilitar y verificar
sudo sforge --ssh --ssh-port 2222    # instalar y cambiar el puerto
```
`--ssh-port` requiere `--ssh`; usarlo solo no tiene efecto.

### 5.3 Git
```bash
sforge --install-git
sforge --git-config --git-name "Nombre" --git-email "mail@ejemplo.com"
sforge --git-config --git-scope system --git-name "..." --git-email "..."
sforge --git-config --git-editor nano --git-branch main --git-pull rebase
sforge --git-ssh --git-email "mail@ejemplo.com" --ssh-key-type ed25519
sforge --git-show
```

### 5.4 Personalización del prompt
```bash
sforge --show-branch     # rama git + estado del repo en el prompt
sforge --show-time       # timestamp [HH:MM:SS] en el prompt
sforge --show-venv       # nombre del virtualenv activo en el prompt
sforge --prompt-status   # ver qué personalizaciones están activas
sforge --remove-branch   # (también --remove-time, --remove-venv)
```

### 5.5 Timezone
```bash
sforge --show-timezone
sforge --list-timezones-region Europe
sudo sforge --set-timezone Europe/Madrid
sudo sforge --enable-ntp        # sincronización automática del reloj
sforge --show-ntp
```

### 5.6 UFW (firewall)
```bash
sudo sforge --install-ufw
sudo sforge --allow-port 22 --protocol tcp
sudo sforge --enable-ufw
sudo sforge --ufw-status --ufw-verbose
sudo sforge --deny-port 8080
sudo sforge --delete-rule 22
```
Se avisa al abrir puertos por debajo de 1024 (puertos privilegiados).

### 5.7 fail2ban
```bash
sudo sforge --install-fail2ban
sudo sforge --protect-ssh --max-retry 3 --ban-time 30m
sudo sforge --enable-fail2ban
sudo sforge --fail2ban-status --jail sshd
```

### 5.8 Hostname
```bash
sforge --show-hostname
sudo sforge --set-hostname web-prod-01
```

### 5.9 Usuarios
```bash
sudo sforge --create-user devuser --user-password "..."
sudo sforge --grant-sudo devuser
sudo sforge --revoke-sudo devuser
sudo sforge --add-ssh-key devuser --ssh-key "ssh-ed25519 AAAA..."
sudo sforge --list-users
sudo sforge --user-info devuser
sudo sforge --delete-user devuser --keep-home
```

### 5.10 Cron
```bash
sforge --add-cron "0 3 * * *" --cron-command "/home/devuser/backup.sh" --cron-comment "Daily backup"
sforge --list-cron
sforge --list-cron-cli          # solo tareas gestionadas por la CLI
sforge --remove-cron 1
sforge --remove-cron-cli
sforge --clear-cron             # elimina TODAS las tareas de cron, con cuidado
```

### 5.11 Swap
```bash
sudo sforge --create-swap          # 2G por defecto
sudo sforge --create-swap 1G
sudo sforge --swap-status
sudo sforge --swappiness 10        # valor recomendado para servidores
sudo sforge --disable-swap
sudo sforge --remove-swap
```

## 6. Interfaz y salida

Toda la salida está construida con [Rich](https://github.com/Textualize/rich):

- **Ejecución de comandos**: mientras corre un comando del sistema se muestra
  un spinner animado con el comando en gris; al terminar se reemplaza en el
  sitio por un `✔` verde o un `✘` rojo (con el `stderr` debajo si falló).
- **Estados** (`--swap-status`, `--ufw-status`, `--fail2ban-status`,
  `--show-ntp`): se muestran como tablas clave/valor.
- **Listados** (`--list-users`, `--list-cron`, reglas de `--ufw-status`): se
  muestran como tablas con columnas.
- **Uso de swap**: `--swap-status` incluye una barra de progreso coloreada
  (verde/amarillo/rojo según el porcentaje usado).
- **Mensajes**: `✔` éxito, `ℹ` información, `⚠` aviso, `✘` error —
  consistentes en todos los módulos.

## 7. Seguridad

- **UFW**: el flujo `--all` permite el puerto SSH *antes* de activar el
  firewall, para no bloquear el acceso remoto.
- **Puertos privilegiados**: se avisa al abrir puertos por debajo de 1024.
- **Validación**: nombres de usuario, hostnames, puertos, tamaños de swap y
  expresiones cron se validan antes de aplicarse.
- **Detección del usuario real tras `sudo`**: cuando se ejecuta con `sudo`,
  los módulos que configuran cosas a nivel de usuario (Git, prompt) detectan
  el usuario real mediante la variable `SUDO_USER` y actúan sobre su
  configuración, no sobre la de root. Más detalle en
  [`arquitectura.md`](arquitectura.md#6-detección-del-usuario-real-tras-sudo).
