from flask import Flask, render_template, request, Response
import subprocess
import os
import re
import shutil
import time
import platform

app = Flask(__name__)

# ===================================
# OS DETECT
# ===================================

IS_WINDOWS = platform.system().lower() == "windows"

# ===================================
# PATHS
# ===================================

RESULT_DIR = "results"

if IS_WINDOWS:
    HOME_DIR = os.environ.get("USERPROFILE", "")
else:
    HOME_DIR = os.path.expanduser("~")

TEMP_TOOL_DIR = os.path.join(
    HOME_DIR,
    "SecurityTools"
)

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)

os.makedirs(
    TEMP_TOOL_DIR,
    exist_ok=True
)

if IS_WINDOWS:
    os.environ["PATH"] += ";" + TEMP_TOOL_DIR
else:
    os.environ["PATH"] += ":" + TEMP_TOOL_DIR


TARGET = ""


# ===================================
# LOGGER
# ===================================

def terminal_log(msg):
    print(msg, flush=True)


# ===================================
# CLEAN URL
# ===================================

def clean_target(target):

    if not target:
        return ""

    target = re.sub(
        r'https?://',
        '',
        target
    )

    target = target.replace(
        "/",
        ""
    )

    return target.strip()


# ===================================
# CHECK TOOL
# ===================================

def check_tool(tool):

    if tool in ["windows", "linux", "generic"]:
        return True

    if shutil.which(tool):
        return True

    ext = ".bat" if IS_WINDOWS else ".sh"

    temp_file = os.path.join(
        TEMP_TOOL_DIR,
        tool + ext
    )

    return os.path.exists(
        temp_file
    )


# ===================================
# TEMP TOOL
# ===================================

def create_temp_tool(tool):

    ext = ".bat" if IS_WINDOWS else ".sh"

    temp_path = os.path.join(
        TEMP_TOOL_DIR,
        tool + ext
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8"
    ) as f:

        if IS_WINDOWS:
            f.write(
                f'@echo [SIMULATED] {tool} running'
            )
        else:
            f.write(
                f'#!/bin/bash\necho "[SIMULATED] {tool} running"'
            )

    if not IS_WINDOWS:
        os.chmod(
            temp_path,
            0o755
        )

    return temp_path


# ===================================
# INSTALL TOOL (LINUX ONLY)
# ===================================

def install_tool(tool):

    logs = []

    logs.append(
        f"[CHECK] {tool}"
    )

    if check_tool(tool):

        logs.append(
            "[SUCCESS] Already installed"
        )

        return logs

    if IS_WINDOWS:

        temp_path = create_temp_tool(
            tool
        )

        logs.append(
            f"[TEMP] {temp_path}"
        )

        return logs

    install_cmd = f"sudo apt install -y {tool}"

    try:

        logs.append(
            f"[INSTALL] {tool}"
        )

        process = subprocess.run(
            install_cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if process.stdout:
            logs.append(
                process.stdout
            )

        if process.stderr:
            logs.append(
                process.stderr
            )

        if not check_tool(tool):

            temp_path = create_temp_tool(
                tool
            )

            logs.append(
                f"[TEMP] {temp_path}"
            )

    except:

        temp_path = create_temp_tool(
            tool
        )

        logs.append(
            f"[TEMP] {temp_path}"
        )

    return logs


# ===================================
# COMMANDS
# ===================================

def get_commands():

    if IS_WINDOWS:

        basic_commands = [

            ("1_IP_CONFIG", "windows", "ipconfig", "ipconfig.txt"),
            ("2_ROUTE", "windows", "route print", "route.txt"),
            ("3_DNS_RESOLVER", "windows", "ipconfig /displaydns", "dnsresolver.txt"),
            ("4_NET_CONNECTIONS", "windows", "netstat -ano", "netstat.txt"),
            ("5_PING", "windows", f"ping {TARGET}", "ping.txt"),
            ("6_TRACE_ROUTE", "windows", f"tracert {TARGET}", "tracert.txt"),
            ("7_ARP_TABLE", "windows", "arp -a", "arp.txt"),

        ]

    else:

        basic_commands = [

            ("1_IP_CONFIG", "linux", "ifconfig", "ipconfig.txt"),
            ("2_ROUTE", "linux", "route -n", "route.txt"),
            ("3_DNS_RESOLVER", "linux", "cat /etc/resolv.conf", "dnsresolver.txt"),
            ("4_NET_CONNECTIONS", "linux", "netstat -tunap", "netstat.txt"),
            ("5_PING", "linux", f"ping -c 4 {TARGET}", "ping.txt"),
            ("6_TRACE_ROUTE", "linux", f"traceroute {TARGET}", "traceroute.txt"),
            ("7_ARP_TABLE", "linux", "arp -a", "arp.txt"),

        ]

    tool_commands = [

        ("8_WHOIS", "whois", f"whois {TARGET}", "whois.txt"),
        ("9_NSLOOKUP", "nslookup", f"nslookup {TARGET}", "nslookup.txt"),
        ("10_DIG", "dig", f"dig {TARGET}", "dig.txt"),

        ("11_NMAP", "nmap", f"nmap {TARGET}", "nmap.txt"),

        ("12_WHATWEB", "whatweb", f"whatweb {TARGET}", "whatweb.txt"),
        ("13_NIKTO", "nikto", f"nikto -h {TARGET}", "nikto.txt"),
        ("14_BANNER", "generic", f"curl -I http://{TARGET}", "banner.txt"),

        ("15_CMSEEK", "cmseek", f"cmseek -u {TARGET}", "cmseek.txt"),
        ("16_WPSCAN", "wpscan", f"wpscan --url {TARGET}", "wpscan.txt"),

        ("17_SUBLIST3R", "sublist3r", f"sublist3r -d {TARGET}", "sublist3r.txt"),
        ("18_AMASS", "amass", f"amass enum -d {TARGET}", "amass.txt"),

        ("19_THEHARVESTER", "theHarvester", f"theHarvester -d {TARGET} -b all", "harvester.txt"),

        ("20_DNSENUM", "dnsenum", f"dnsenum {TARGET}", "dnsenum.txt"),
        ("21_DNSRECON", "dnsrecon", f"dnsrecon -d {TARGET}", "dnsrecon.txt"),

        ("22_ENUM4LINUX", "enum4linux", f"enum4linux {TARGET}", "enum4linux.txt"),

        ("23_GOBUSTER", "gobuster", f"gobuster dir -u http://{TARGET}", "gobuster.txt"),

        ("24_DIRB", "dirb", f"dirb http://{TARGET}", "dirb.txt"),

        ("25_SSLSCAN", "sslscan", f"sslscan {TARGET}", "sslscan.txt"),

        ("26_WIRESHARK", "wireshark", "wireshark --version", "wireshark.txt"),

        ("27_MALTEGO", "maltego", "maltego", "maltego.txt")

    ]

    return basic_commands + tool_commands


# ===================================
# ROUTES
# ===================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/start_scan",
    methods=["GET"]
)
def start_scan():

    global TARGET

    TARGET = request.args.get(
        "target"
    )

    TARGET = clean_target(
        TARGET
    )

    print(
        f"\nSCAN STARTED : {TARGET}\n",
        flush=True
    )

    return render_template(
        "live_result.html",
        target=TARGET
    )


# ===================================
# LIVE STREAM
# ===================================

@app.route("/stream")
def stream():

    def generate():

        commands = get_commands()

        for name, tool, cmd, filename in commands:

            output = ""

            header = [

                "=" * 60,
                name,
                f"COMMAND : {cmd}",
                "=" * 60

            ]

            for line in header:

                terminal_log(
                    line
                )

                output += (
                    line + "\n"
                )

                yield f"data: {line}\n\n"

            if not check_tool(
                tool
            ):

                install_logs = install_tool(
                    tool
                )

                for line in install_logs:

                    terminal_log(
                        line
                    )

                    output += (
                        line + "\n"
                    )

                    yield f"data: {line}\n\n"

            try:

                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                for line in iter(
                    process.stdout.readline,
                    ''
                ):

                    line = line.strip()

                    if line:

                        terminal_log(
                            line
                        )

                        output += (
                            line + "\n"
                        )

                        yield f"data: {line}\n\n"

                    time.sleep(
                        0.03
                    )

            except Exception as e:

                error_msg = (
                    f"ERROR : {str(e)}"
                )

                terminal_log(
                    error_msg
                )

                output += (
                    error_msg + "\n"
                )

                yield f"data: {error_msg}\n\n"

            with open(
                os.path.join(
                    RESULT_DIR,
                    filename
                ),
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    output
                )

            saved_msg = (
                f"[SAVED] {filename}"
            )

            terminal_log(
                saved_msg
            )

            yield f"data: {saved_msg}\n\n"

        yield f"data: SCAN COMPLETED\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream"
    )


# ===================================
# START
# ===================================

if __name__ == "__main__":

    app.run(
        debug=True,
        threaded=True,
        use_reloader=False
    )