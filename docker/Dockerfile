# Ubuntu con systemd como PID 1, para ejercitar sforge (apt, systemctl, ufw,
# fail2ban, sshd, chpasswd...) de verdad dentro de un contenedor, sin VM.
# Requiere arrancarse con --privileged + cgroup host (ver docker-compose.yml).
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        systemd \
        sudo \
        openssh-server \
        fail2ban \
        ufw \
        cron \
        python3 \
        python3-pip \
        python3-venv \
        git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# systemd unit files que no aportan nada dentro de un contenedor y solo
# ralentizan/rompen el arranque de /sbin/init.
RUN find /etc/systemd/system /lib/systemd/system -name "*.wants/*" \
        \( -name "*getty*" -o -name "*udev*" \) -exec rm -f {} \; 2>/dev/null; \
    systemctl mask systemd-udevd.service systemd-udevd-kernel.socket \
        systemd-udevd-control.socket 2>/dev/null || true

RUN useradd -m -s /bin/bash -G sudo sforge \
    && echo "sforge ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/sforge \
    && chmod 0440 /etc/sudoers.d/sforge

WORKDIR /opt/serverforge-cli
COPY . .
RUN pip install --break-system-packages -e ".[dev]"

STOPSIGNAL SIGRTMIN+3
CMD ["/sbin/init"]
