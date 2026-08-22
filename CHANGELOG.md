# Changelog

🇪🇸 Español · [🇬🇧 English](CHANGELOG.en.md)

Todos los cambios notables de este proyecto se documentan en este fichero.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [Sin publicar]

## [1.0.0] - 2026-08-22

### Añadido
- CLI inicial para automatizar la configuración y el hardening de servidores
  Ubuntu, con modularización en `commands/` (interfaz) y `modules/` (lógica).
- Módulo de actualización del sistema (`system`).
- Instalación y configuración de SSH, incluyendo cambio de puerto.
- Instalación y configuración de Git.
- Personalización del prompt de shell (rama, timestamp, entorno virtual).
- Módulo `ufw`: instalación, activación/desactivación y gestión de reglas de
  puertos (allow/deny).
- Módulo `fail2ban`: protección contra fuerza bruta en SSH.
- Módulo `hostname`: configuración de nombre de host con prompt interactivo
  dentro del flujo `--all`.
- Módulo `users`: gestión de usuarios, permisos sudo, grupos y claves SSH.
- Módulo `cron`: gestión de tareas programadas (añadir, listar, eliminar).
- Módulo `swap`: gestión de ficheros swap con persistencia en `fstab`.
- Módulo `timezone`: configuración de la zona horaria del sistema.
- Suite de tests con `pytest` para todos los módulos.
- Interfaz visual modernizada con `rich`: tablas, barras de uso, spinner en
  vivo durante la ejecución de comandos y separadores de fase.
- Ayuda en dos niveles (`--help`): resumen general de módulos y detalle por
  módulo.
- Empaquetado como paquete Python instalable (`pyproject.toml`), con el
  ejecutable `sforge` como punto de entrada.
- Publicación del paquete `serverforge-cli` en [PyPI](https://pypi.org/project/serverforge-cli/),
  instalable con `pip install serverforge-cli` en Linux, macOS y Windows.
- Scripts `install.sh` e `install.bat` que instalan el paquete publicado en
  PyPI con un solo comando.
- Sección "Instalación rápida" en el README (español e inglés) con los
  comandos de instalación para Linux, macOS y Windows, y un aviso sobre en
  qué sistema operativo tiene sentido ejecutar cada módulo.
- Ficheros `LICENSE` (MIT) y `CHANGELOG.md`.
- Documentación del proyecto (`README.md` en español y `README.en.md` en
  inglés) con arquitectura, ejemplos de uso y notas de seguridad.

### Cambiado
- Reestructuración del código fuente al layout estándar `src/serverforge_cli/`
  (antes en la raíz del repositorio).
- Los ejemplos de uso del README pasan de `python3 cli.py --xxx` a
  `sforge --xxx`, acordes al punto de entrada instalado vía pip.
- Sección "Instalación" del README renombrada a "Desarrollo" (clonar +
  entorno virtual + instalación editable), dejando la instalación vía PyPI
  como vía principal para usuarios finales.

[Sin publicar]: https://github.com/Manueh9/ServerSetup_CLI/compare/v1...HEAD
[1.0.0]: https://pypi.org/project/serverforge-cli/1.0.0/
