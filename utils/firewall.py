import subprocess

def block_ip_windows(ip, rule_name_prefix="Threat Block: "):
    """
    Blocks an incoming IP address using Windows Advanced Firewall.
    Requires the script to run with Administrator privileges.
    """
    rule_name = f"{rule_name_prefix}{ip}"
    command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip="{ip}"'
    
    try:
        # We use shell=True and check=True so it raises exception if netsh fails (e.g. not Admin)
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True, "IP Successfully Blocked"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else e.stdout.strip()
        # Fallback error detection if netsh prints to stdout on permission error
        if "The requested operation requires elevation" in error_msg:
            return False, "Requires Administrator privileges to modify firewall."
        return False, error_msg
