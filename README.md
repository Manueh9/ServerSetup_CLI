# ServerSetup CLI

![Tests](https://github.com/Manueh9/ServerSetup_CLI/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

CLI en Python para automatizar la configuración inicial de servidores Linux (Ubuntu Server).
Reduce el tiempo de setup de un servidor nuevo de horas a minutos, con configuración
reproducible y sin pasos manuales olvidados.

## El problema que resuelve

Configurar un servidor Linux desde cero implica repetir siempre los mismos pasos:
actualizar el sistema, instalar y asegurar SSH, configurar Git, personalizar el
prompt, ajustar la timezone... Hacerlo a mano es lento y propenso a errores.
ServerSetup CLI automatiza ese proceso completo con un único comando.

## Instalación

```bash
git clone https://github.com/Manueh9/ServerSetup_CLI
cd ServerSetup_CLI
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Uso

### Setup completo del servidor
```bash
sudo python3 cli.py --all
```

### Sistema
```bash
python3 cli.py --update
python3 cli.py --upgrade
python3 cli.py --full-upgrade
```

### SSH
```bash
sudo python3 cli.py --ssh
sudo python3 cli.py --ssh --ssh-port 2222
```

### Git
```bash
python3 cli.py --install-git
python3 cli.py --git-config --git-name "Tu Nombre" --git-email "tu@email.com"
python3 cli.py --git-config --git-editor nano --git-branch main --git-aliases
python3 cli.py --git-ssh --git-email "tu@email.com"
python3 cli.py --git-show
```

### Personalización del prompt
```bash
python3 cli.py --show-branch --show-time --show-venv
python3 cli.py --prompt-status
```

### Timezone
```bash
python3 cli.py --show-timezone
python3 cli.py --list-timezones-region Europe
sudo python3 cli.py --set-timezone Europe/Madrid
sudo python3 cli.py --enable-ntp
```

## Arquitectura

```
cli.py                  → punto de entrada, orquesta --all
commands/                → parsea argumentos y decide qué ejecutar
  ├── system.py
  ├── ssh.py
  ├── git.py
  ├── command_line_custom.py
  └── timezone.py
modules/                 → lógica real, ejecuta comandos del sistema
  ├── system.py
  ├── ssh.py
  ├── git.py
  ├── command_line_custom.py
  └── timezone.py
utils.py                 → helpers compartidos (colores, run_command, detección de usuario real)
tests/                   → suite de tests con pytest + mocks
```

Cada módulo tiene una única responsabilidad. `cli.py` no sabe qué hace SSH ni Git;
`commands/` no sabe cómo se ejecutan los comandos del sistema; `modules/` no sabe
nada de argparse ni de la CLI. Añadir un módulo nuevo no requiere tocar el resto.

## Módulos disponibles

1. **Sistema** — apt update / upgrade / full-upgrade
2. **SSH** — instalación, cambio de puerto, verificación de estado
3. **Git** — instalación, configuración de usuario, aliases, claves SSH
4. **Prompt** — rama git, timestamp, nombre de virtualenv en la terminal
5. **Timezone** — cambio de zona horaria y sincronización NTP

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=modules --cov-report=term-missing
```

Los tests mockean todas las llamadas al sistema (`apt`, `systemctl`, `git config`...)
para poder ejecutarse en cualquier máquina sin necesidad de privilegios root ni
modificar el sistema real.

## Roadmap

- [ ] UFW — gestión de firewall
- [ ] fail2ban — protección contra fuerza bruta
- [ ] Gestión de usuarios y permisos sudo
- [ ] PostgreSQL — instalación y configuración

---
*Proyecto de la Fase 1 — Arquitectura y Sistemas*
