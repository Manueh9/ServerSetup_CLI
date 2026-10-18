# Changelog

🇪🇸 Español · [🇬🇧 English](CHANGELOG.en.md)

Todos los cambios notables de este proyecto se documentan en este fichero.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [Sin publicar]

## [1.1.0] - 2026-10-18

### Añadido
- Validación del sistema operativo al arrancar (`is_supported_os`): si no es
  Debian/Ubuntu, la CLI aborta con un mensaje claro antes de ejecutar ningún
  comando, en vez de fallar a medias más adelante con errores confusos
  (`apt`, `ufw` y `systemctl` no existen en otras distros).
- Validación de `sshd_config` (`sshd -t`) antes de reiniciar el servicio SSH
  tras cambiar de puerto: si la configuración queda inválida, no se reinicia
  el servicio y se conserva el acceso remoto con la configuración anterior.

### Corregido
- El texto de uso de `--help` (y el `prog` mostrado en `--help <módulo>`)
  seguía mostrando `cli.py` en vez de `sforge`.
- `--protect-ssh` (fail2ban) lanzaba una excepción sin controlar si se
  ejecutaba sin permisos suficientes para escribir `jail.local`, y aun así
  intentaba reiniciar el servicio con una configuración que no llegó a
  escribirse. Ahora se informa el error de permisos y no se reinicia el
  servicio si la escritura falla.
- `--create-user ... --user-password ...` aplicaba la contraseña con
  `chpasswd` sin pasar por el runner de comandos centralizado ni solicitar
  privilegios de root, por lo que fallaba en silencio al ejecutarse sin
  `sudo`. Ahora usa el mismo runner que el resto de comandos, con
  `sudo` cuando hace falta.

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

[Sin publicar]: https://github.com/Manueh9/ServerSetup_CLI/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Manueh9/ServerSetup_CLI/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Manueh9/ServerSetup_CLI/releases/tag/v1.0.0
