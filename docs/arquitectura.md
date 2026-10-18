# Arquitectura

Documento para quien vaya a leer, modificar o ampliar el código de
`serverforge-cli`. Describe el patrón de diseño usado, por qué se eligió,
cómo está organizado el árbol de directorios y la convención a seguir para
añadir un módulo nuevo.

## 1. Visión general: patrón de capas (Command Pattern)

El proyecto sigue un **patrón de capas con separación de responsabilidades
tipo Command Pattern**: cada módulo funcional (SSH, UFW, usuarios...) se
divide en dos archivos con un rol muy concreto, más una capa de utilidades
compartida:

```
┌─────────────────────────────────────────────────────────┐
│  cli.py           → punto de entrada, orquestación      │
├─────────────────────────────────────────────────────────┤
│  commands/<x>.py  → capa de CONTROL (argparse, dispatch)│
├─────────────────────────────────────────────────────────┤
│  modules/<x>.py   → capa de LÓGICA (ejecuta el sistema) │
├─────────────────────────────────────────────────────────┤
│  utils.py         → capa de PRESENTACIÓN + run_command()│
└─────────────────────────────────────────────────────────┘
```

- **`commands/<nombre>.py`** — capa de control. Sabe qué flags existen y qué
  hacer cuando el usuario los pasa, pero no sabe *cómo* se ejecuta nada a
  nivel de sistema. Cada archivo expone exactamente tres funciones:
  - `register_args(parser)` — añade sus flags a un `argparse.ArgumentParser`.
  - `handle(args)` — decide, según los argumentos ya parseados, qué función
    de `modules/` invocar.
  - `run_all(...)` — versión usada por el flujo `--all`; normalmente
    reutiliza la misma lógica interna que `handle()`.
- **`modules/<nombre>.py`** — capa de lógica real. Contiene las funciones que
  de verdad ejecutan comandos del sistema (`apt`, `systemctl`, `ufw`,
  `crontab`...), validan datos de entrada y editan archivos de configuración.
  No importa `argparse` ni sabe nada de flags o de la CLI.
- **`utils.py`** — capa de presentación y la única puerta de salida hacia el
  sistema: expone `run_command()` (subprocess con spinner Rich, captura de
  errores y salida consistente) y los helpers de salida (`ok`, `info`,
  `warn`, `error`, tablas, barras de progreso...).
- **`cli.py`** — punto de entrada (`sforge`). No sabe qué hace cada módulo
  internamente: solo recorre `MODULES` para registrar flags y despachar, y
  recorre `PHASES` para el flujo `--all`.

### Por qué este diseño (y no otro)

- **No es MVC clásico**: no hay una capa de "Modelo" persistente — el estado
  que se gestiona es el propio sistema operativo del servidor (archivos de
  configuración, servicios, usuarios del SO), no una base de datos ni objetos
  de dominio en memoria. Forzar un Model/View/Controller aquí añadiría
  abstracción sin beneficio real.
- **No es una arquitectura de plugins**: los módulos no se descubren
  dinámicamente; se registran explícitamente en una única lista
  (`commands/__init__.py::MODULES`). Para una CLI de 11 módulos estables esto
  es más simple y predecible que un sistema de carga dinámica, y sigue
  permitiendo añadir módulos sin tocar el resto del código.
- **Sí es, en esencia, un Command Pattern con separación
  controlador/servicio**: cada módulo es un "comando" autocontenido
  (`register_args` + `handle` + `run_all`) que delega su ejecución real a un
  servicio (`modules/<x>.py`). Esta separación es la que aporta el valor
  real:
  1. **Testabilidad**: los tests (`tests/test_*.py`) importan y mockean
     directamente `modules/*.py`, sin necesitar argparse ni simular
     argumentos de línea de comandos.
  2. **Un único punto de salida al sistema**: casi todo pasa por
     `run_command()` en `utils.py`, lo que centraliza el manejo de errores,
     el uso de `sudo` y el formato de salida (spinner + `✔`/`✘`).
  3. **Regla de adición predecible**: añadir un módulo nuevo es siempre el
     mismo patrón (ver sección 4), sin tener que decidir dónde encaja cada
     pieza.
  4. **Bajo acoplamiento**: `cli.py` no conoce el interior de ningún módulo;
     `commands/` no conoce cómo se ejecutan los comandos del sistema;
     `modules/` no conoce nada de argparse ni de la CLI.

## 2. Estructura de directorios

```
ServerSetup_CLI/
├── README.md, README.en.md         # documentación de referencia (raíz)
├── CHANGELOG.md, CHANGELOG.en.md
├── pyproject.toml                  # metadatos del paquete, dependencias, entry point `sforge`
├── requirements.txt
├── install.sh, install.bat         # scripts de instalación
├── docs/                           # esta documentación en español
├── src/serverforge_cli/
│   ├── cli.py                      # punto de entrada, orquesta --all y --help
│   ├── constants.py                # constantes de rutas de archivos del sistema
│   ├── utils.py                    # helpers Rich + run_command()
│   ├── commands/                   # capa de control (11 archivos + __init__.py)
│   │   └── __init__.py             # MODULES = [system, ssh, git, ...]
│   └── modules/                    # capa de lógica (11 archivos, mismo nombre que commands/)
└── tests/                          # pytest, 11 archivos test_<módulo>.py + conftest.py
```

Los módulos actuales, con el mismo nombre de archivo en `commands/` y
`modules/`: `system`, `ssh`, `git`, `command_line_custom` (expuesto en la CLI
como `prompt`), `timezone`, `ufw`, `fail2ban`, `hostname`, `users`, `cron`,
`swap`.

## 3. Ejemplo completo: el módulo SSH

`commands/ssh.py`:
```python
from serverforge_cli.modules.ssh import install_ssh, enable_ssh, change_ssh_port, restart_ssh, check_ssh_status
from serverforge_cli.utils import step, error

DEFAULT_PORT = 22

def register_args(parser):
    group = parser.add_argument_group("SSH")
    group.add_argument("--ssh", action="store_true", help="Install and configure OpenSSH")
    group.add_argument("--ssh-port", type=int, help="SSH listening port")

def handle(args):
    if args.ssh_port and not args.ssh:
        error("--ssh-port requires --ssh")
        return
    if not args.ssh:
        return
    _install_and_configure(args.ssh_port)

def run_all(port=DEFAULT_PORT):
    _install_and_configure(port)

def _install_and_configure(port=None):
    """Lógica compartida entre handle() y run_all()."""
    step("Installing OpenSSH Server...")
    install_ssh()
    step("Enabling SSH service...")
    enable_ssh()
    if port and port != DEFAULT_PORT:
        step(f"Changing SSH port to {port}...")
        change_ssh_port(port)
        step("Restarting SSH service...")
        restart_ssh()
    step("Checking SSH status...")
    check_ssh_status()
```

`modules/ssh.py` implementa `install_ssh()`, `enable_ssh()`,
`change_ssh_port(port)` (edita `/etc/ssh/sshd_config` usando la constante
`SSH_CONFIG_FILE` de `constants.py`), `restart_ssh()` y
`check_ssh_status()`. Ninguna de estas funciones sabe nada de `argparse`; solo
reciben datos ya validados y ejecutan trabajo real contra el sistema.

Este patrón (control fino en `commands/`, lógica pura en `modules/`) se repite
igual en los 11 módulos, desde el más simple (`system.py`, 3 funciones de una
línea que envuelven `apt update/upgrade/full-upgrade`) hasta el más elaborado.

## 4. Cómo añadir un módulo nuevo

1. Crear `src/serverforge_cli/modules/<nombre>.py` con la lógica real
   (funciones que llaman a `run_command()` de `utils.py` o editan archivos de
   configuración). Añadir las rutas de archivo que necesite a
   `constants.py` si aplica.
2. Crear `src/serverforge_cli/commands/<nombre>.py` con `register_args`,
   `handle` y `run_all`, siguiendo el ejemplo de la sección 3.
3. Registrar el módulo en `src/serverforge_cli/commands/__init__.py`
   (import + añadir a la lista `MODULES`).
4. Si el módulo debe participar en `sforge --all`, añadirlo a `PHASES` en
   `cli.py`, y a `MODULE_HELP` para que aparezca en `sforge --help`.
5. Crear `tests/test_<nombre>.py` con la misma estructura que los tests
   existentes (ver sección 5).
6. Documentar el módulo en `docs/guia-usuario.md` (y opcionalmente en el
   `README.md` de la raíz).

No hace falta tocar `cli.py` más allá de registrarlo en `MODULES`/`PHASES`/
`MODULE_HELP`: el resto del flujo (parseo, despacho, `--help`) es genérico.

## 5. Convenciones de testing

- Los tests viven en `tests/`, un archivo `test_<módulo>.py` por cada
  `modules/<módulo>.py` (11 archivos, correspondencia 1:1), más
  `test_cli.py` (orquestación de `--all`, ayuda de dos niveles) y tests
  dedicados para la capa `commands/` de los módulos `ssh` y `fail2ban`
  (`test_commands_ssh.py`, `test_commands_fail2ban.py`). Al resto de
  `commands/*.py` (system, git, users, ufw, hostname, cron, swap, timezone,
  command_line_custom) todavía les falta ese test dedicado.
- `tests/conftest.py` define dos fixtures:
  - `mock_run_command(module_path)` — parchea `run_command` en el namespace
    del módulo indicado. Uso: `mock_run_command("serverforge_cli.modules.system")`.
  - `mock_subprocess_run` — parchea `subprocess.run` directamente, necesario
    porque algún módulo (ver sección 6.2) no pasa por `run_command()`.
- Para módulos que editan archivos (`ssh`, `hostname`, `swap`...) se usan
  `tmp_path`/`monkeypatch` de pytest para no tocar el sistema real.
- Para verificar mensajes de consola se usa `capsys`.
- Ejecutar la suite:
  ```bash
  pytest tests/ -v
  pytest tests/ -v --cov=serverforge_cli --cov-report=term-missing
  ```
- CI: GitHub Actions ejecuta la suite en Python 3.11 y 3.12 en cada push a
  `main`/`develop` (`.github/workflows/tests.yml`).

## 6. Detalles de diseño relevantes

### 6.1 Detección del usuario real tras `sudo`

Cuando la CLI se ejecuta con `sudo`, los módulos que configuran algo a nivel
de usuario (Git, prompt) necesitan saber si deben actuar sobre la
configuración del usuario real o sobre la de `root`. `utils.py::get_real_user()`
resuelve esto leyendo la variable de entorno `SUDO_USER`; el helper
`utils.py::warn_if_root_for_user_config()` avisa explícitamente si se va a
aplicar una configuración `--global` mientras se ejecuta como root, y pide
confirmación antes de continuar.

### 6.2 `run_command()` como único punto de salida al sistema

`utils.py::run_command(command, requires_sudo=False)` centraliza toda
ejecución de comandos del sistema: añade `sudo` automáticamente si hace
falta y no se está ya como root, muestra un spinner mientras corre, y en caso
de error imprime el `stderr` y aborta con `SystemExit(1)`. La convención del
proyecto es que **todo** el código en `modules/` pase por esta función en
vez de llamar a `subprocess` directamente.

## 7. Cómo contribuir (modo desarrollo)

```bash
git clone https://github.com/Manueh9/ServerSetup_CLI
cd ServerSetup_CLI
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

Esto instala `serverforge-cli` en modo editable junto con las dependencias de
desarrollo (`pytest`, `pytest-mock`, `pytest-cov`).