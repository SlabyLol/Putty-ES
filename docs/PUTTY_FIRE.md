# Putty-Fire – Server Protection Layer

**Putty-Fire** is the security module of Putty-ES. When activated, protected hosts show:

```text
Protected by Putty-Fire
```

## What it does (real hardening)

| Feature | Description |
|--------|-------------|
| Firewall | ufw (or iptables fallback): default deny in, allow needed ports |
| SSH lock-down | Protocol 2, limited auth tries, no empty passwords, optional no password login |
| Brute-force shield | fail2ban jail for SSH |
| Kernel harden | sysctl: rp_filter, syncookies, no source routes, etc. |
| Status | `/etc/putty-fire/STATUS` + MOTD line + `putty-fire-status` command |
| Audit log | `/var/log/putty-fire/activate.log` |

## Levels

- **minimal** – light firewall + basic SSH settings  
- **standard** – recommended default (firewall + fail2ban + sysctl + banner)  
- **strict** – rate-limited SSH, fewer retries, longer bans, stronger sysctl, optional password auth off  

## Config example

```yaml
modules:
  - name: putty-fire
    enable: true
    level: standard
    ssh_port: 22
    allow_ports: ["22/tcp", "80/tcp", "443/tcp"]
    ban_ssh_bruteforce: true
    fail2ban: true
    sysctl_harden: true
    disable_password_auth: false
    show_banner: true
```

See `configs/example-putty-fire.yaml`.

## On the server after apply

```bash
putty-fire-status
cat /etc/putty-fire/STATUS
```

You should see **Protected by Putty-Fire**.

## Important

- Always keep SSH access (key recommended) before enabling `disable_password_auth: true`.
- Putty-Fire is defensive security hardening – not an offensive tool.
