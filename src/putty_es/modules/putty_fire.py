"""
Putty-Fire – Advanced Server Protection Module

Real hardening: firewall rules, SSH protection, intrusion signals,
rate limits, logging and a visible "Protected by Putty-Fire" status.
"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from putty_es.modules.base import BaseModule

if TYPE_CHECKING:
    from putty_es.core.config import Host
    from putty_es.core.executor import Executor

BANNER_FILE = "/etc/putty-fire/STATUS"
BANNER_TEXT = "Protected by Putty-Fire"
MOTD_SNIPPET = "\n*** Protected by Putty-Fire – Putty-ES Security Layer ***\n"


class PuttyFireModule(BaseModule):
    name = "putty-fire"
    description = (
        "Putty-Fire: advanced server protection – firewall, SSH lock-down, "
        "intrusion hardening, status banner 'Protected by Putty-Fire'"
    )

    def apply(self, host: "Host", config: dict[str, Any], executor: "Executor") -> bool:
        enable = config.get("enable", True)
        if not enable:
            return True

        level = str(config.get("level", "standard")).lower()  # minimal | standard | strict
        ssh_port = int(config.get("ssh_port", 22))
        allow_ports: List[str] = config.get(
            "allow_ports",
            [f"{ssh_port}/tcp", "80/tcp", "443/tcp"],
        )
        ban_ssh_bruteforce = config.get("ban_ssh_bruteforce", True)
        disable_password_auth = config.get("disable_password_auth", False)
        install_fail2ban = config.get("fail2ban", True)
        sysctl_harden = config.get("sysctl_harden", True)
        show_banner = config.get("show_banner", True)
        extra_deny: List[str] = config.get("deny_ports", [])

        # 1) Base packages for protection
        executor.run(
            host,
            "DEBIAN_FRONTEND=noninteractive apt-get update -qq && "
            "apt-get install -y -qq ufw fail2ban iptables netfilter-persistent 2>/dev/null || "
            "dnf install -y ufw fail2ban iptables 2>/dev/null || "
            "yum install -y fail2ban iptables 2>/dev/null || true",
            sudo=True,
            check=False,
        )

        # 2) Firewall (ufw preferred)
        self._setup_firewall(host, executor, allow_ports, extra_deny, ssh_port, level)

        # 3) SSH hardening
        self._harden_ssh(
            host,
            executor,
            ssh_port=ssh_port,
            disable_password=disable_password_auth,
            level=level,
        )

        # 4) fail2ban-style protection
        if install_fail2ban or ban_ssh_bruteforce:
            self._setup_fail2ban(host, executor, ssh_port=ssh_port, level=level)

        # 5) Kernel / network hardening via sysctl
        if sysctl_harden:
            self._sysctl_harden(host, executor, level=level)

        # 6) Status files + MOTD: "Protected by Putty-Fire"
        if show_banner:
            self._install_status_banner(host, executor)

        # 7) Simple audit log
        executor.run(
            host,
            "mkdir -p /var/log/putty-fire && "
            "echo \"[$(date -Iseconds)] Putty-Fire activated (level={level})\" "
            ">> /var/log/putty-fire/activate.log".format(level=level),
            sudo=True,
            check=False,
        )

        return True

    def _setup_firewall(
        self,
        host: "Host",
        executor: "Executor",
        allow_ports: List[str],
        deny_ports: List[str],
        ssh_port: int,
        level: str,
    ) -> None:
        code, _, _ = executor.run(host, "command -v ufw", check=False)
        if code == 0:
            executor.run(host, "ufw --force reset", sudo=True, check=False)
            executor.run(host, "ufw default deny incoming", sudo=True, check=False)
            executor.run(host, "ufw default allow outgoing", sudo=True, check=False)
            # Always keep SSH reachable
            executor.run(host, f"ufw allow {ssh_port}/tcp comment 'Putty-Fire SSH'", sudo=True, check=False)
            for p in allow_ports:
                executor.run(host, f"ufw allow {p}", sudo=True, check=False)
            for p in deny_ports:
                executor.run(host, f"ufw deny {p}", sudo=True, check=False)
            if level == "strict":
                executor.run(host, "ufw limit 22/tcp", sudo=True, check=False)
                executor.run(host, f"ufw limit {ssh_port}/tcp", sudo=True, check=False)
            executor.run(host, "ufw --force enable", sudo=True, check=False)
            executor.run(host, "ufw status verbose", sudo=True, check=False)
            return

        # Fallback: basic iptables
        executor.run(host, "iptables -P INPUT DROP", sudo=True, check=False)
        executor.run(host, "iptables -P FORWARD DROP", sudo=True, check=False)
        executor.run(host, "iptables -P OUTPUT ACCEPT", sudo=True, check=False)
        executor.run(host, "iptables -A INPUT -i lo -j ACCEPT", sudo=True, check=False)
        executor.run(
            host,
            "iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            f"iptables -A INPUT -p tcp --dport {ssh_port} -j ACCEPT",
            sudo=True,
            check=False,
        )
        for p in allow_ports:
            if "/" in p:
                port, proto = p.split("/", 1)
                executor.run(
                    host,
                    f"iptables -A INPUT -p {proto} --dport {port} -j ACCEPT",
                    sudo=True,
                    check=False,
                )

    def _harden_ssh(
        self,
        host: "Host",
        executor: "Executor",
        ssh_port: int,
        disable_password: bool,
        level: str,
    ) -> None:
        settings = {
            "Protocol": "2",
            "PermitEmptyPasswords": "no",
            "X11Forwarding": "no",
            "MaxAuthTries": "3" if level != "minimal" else "5",
            "LoginGraceTime": "30",
            "ClientAliveInterval": "300",
            "ClientAliveCountMax": "2",
            "AllowTcpForwarding": "no" if level == "strict" else "yes",
            "PermitRootLogin": "prohibit-password" if level != "minimal" else "yes",
        }
        if disable_password or level == "strict":
            settings["PasswordAuthentication"] = "no"
            settings["PubkeyAuthentication"] = "yes"

        for key, val in settings.items():
            executor.run(
                host,
                f"sed -i 's/^#*{key}.*/{key} {val}/' /etc/ssh/sshd_config 2>/dev/null; "
                f"grep -q '^{key} ' /etc/ssh/sshd_config || echo '{key} {val}' >> /etc/ssh/sshd_config",
                sudo=True,
                check=False,
            )

        if ssh_port != 22:
            executor.run(
                host,
                f"sed -i 's/^#*Port .*/Port {ssh_port}/' /etc/ssh/sshd_config; "
                f"grep -q '^Port ' /etc/ssh/sshd_config || echo 'Port {ssh_port}' >> /etc/ssh/sshd_config",
                sudo=True,
                check=False,
            )

        executor.run(
            host,
            "systemctl reload sshd 2>/dev/null || systemctl reload ssh 2>/dev/null || true",
            sudo=True,
            check=False,
        )

    def _setup_fail2ban(
        self,
        host: "Host",
        executor: "Executor",
        ssh_port: int,
        level: str,
    ) -> None:
        maxretry = "3" if level == "strict" else "5"
        bantime = "3600" if level == "strict" else "600"

        jail = f"""
[DEFAULT]
bantime = {bantime}
findtime = 600
maxretry = {maxretry}
backend = systemd

[sshd]
enabled = true
port = {ssh_port}
filter = sshd
logpath = /var/log/auth.log
maxretry = {maxretry}
""".strip()

        import base64

        b64 = base64.b64encode(jail.encode()).decode()
        executor.run(
            host,
            f"mkdir -p /etc/fail2ban/jail.d && "
            f"echo '{b64}' | base64 -d > /etc/fail2ban/jail.d/putty-fire.conf",
            sudo=True,
            check=False,
        )
        executor.run(
            host,
            "systemctl enable --now fail2ban 2>/dev/null || service fail2ban restart 2>/dev/null || true",
            sudo=True,
            check=False,
        )

    def _sysctl_harden(self, host: "Host", executor: "Executor", level: str) -> None:
        rules = [
            "net.ipv4.conf.all.rp_filter=1",
            "net.ipv4.conf.default.rp_filter=1",
            "net.ipv4.icmp_echo_ignore_broadcasts=1",
            "net.ipv4.conf.all.accept_source_route=0",
            "net.ipv4.conf.all.accept_redirects=0",
            "net.ipv4.conf.all.send_redirects=0",
            "net.ipv4.tcp_syncookies=1",
        ]
        if level == "strict":
            rules.extend(
                [
                    "net.ipv4.conf.all.log_martians=1",
                    "net.ipv6.conf.all.accept_redirects=0",
                    "kernel.randomize_va_space=2",
                ]
            )
        for r in rules:
            executor.run(host, f"sysctl -w {r}", sudo=True, check=False)
        # Persist
        conf = "\n".join(rules) + "\n"
        import base64

        b64 = base64.b64encode(conf.encode()).decode()
        executor.run(
            host,
            f"echo '{b64}' | base64 -d > /etc/sysctl.d/99-putty-fire.conf && sysctl --system",
            sudo=True,
            check=False,
        )

    def _install_status_banner(self, host: "Host", executor: "Executor") -> None:
        """Install small status so systems show Protected by Putty-Fire."""
        import base64

        status = (
            f"{BANNER_TEXT}\n"
            f"Module: putty-fire\n"
            f"Product: Putty-ES\n"
            f"Do not remove – security layer active\n"
        )
        b64 = base64.b64encode(status.encode()).decode()
        executor.run(
            host,
            f"mkdir -p /etc/putty-fire && echo '{b64}' | base64 -d > {BANNER_FILE} && "
            f"chmod 644 {BANNER_FILE}",
            sudo=True,
            check=False,
        )

        # MOTD / login hint (small line at bottom of login)
        motd = MOTD_SNIPPET
        mb64 = base64.b64encode(motd.encode()).decode()
        executor.run(
            host,
            f"echo '{mb64}' | base64 -d > /etc/motd.d/99-putty-fire 2>/dev/null || "
            f"(grep -q 'Protected by Putty-Fire' /etc/motd 2>/dev/null || "
            f"echo '{motd.strip()}' >> /etc/motd)",
            sudo=True,
            check=False,
        )

        # CLI-friendly status command on the server
        script = (
            "#!/bin/sh\n"
            "echo '════════════════════════════════════'\n"
            "echo '  Protected by Putty-Fire'\n"
            "echo '  Putty-ES Security Layer'\n"
            "echo '════════════════════════════════════'\n"
            f"[ -f {BANNER_FILE} ] && cat {BANNER_FILE}\n"
            "command -v ufw >/dev/null && ufw status | head -20\n"
            "command -v fail2ban-client >/dev/null && fail2ban-client status sshd 2>/dev/null | head -15\n"
        )
        sb64 = base64.b64encode(script.encode()).decode()
        executor.run(
            host,
            f"echo '{sb64}' | base64 -d > /usr/local/bin/putty-fire-status && "
            f"chmod +x /usr/local/bin/putty-fire-status",
            sudo=True,
            check=False,
        )
