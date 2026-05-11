from flask import Flask, render_template, request
import subprocess
import os
import re

app = Flask(__name__)

RESULT_DIR = "results"

if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)


def clean_target(target):
    target = re.sub(r'https?://', '', target)
    target = target.replace("/", "")
    return target


def run_command(cmd, filename):
    try:
        result = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300
        )

        with open(f"{RESULT_DIR}/{filename}", "w") as f:
            f.write(result)

        return result

    except Exception as e:
        return str(e)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():

    target = request.form["target"]
    target = clean_target(target)

    outputs = {}

    outputs["nmap"] = run_command(
        f"nmap -A {target}",
        "nmap.txt"
    )

    outputs["nikto"] = run_command(
        f"nikto -h {target}",
        "nikto.txt"
    )

    outputs["whatweb"] = run_command(
        f"whatweb https://{target}",
        "whatweb.txt"
    )

    outputs["ruby"] = run_command(
        "ruby -v",
        "ruby.txt"
    )

    outputs["perl"] = run_command(
        "perl -v",
        "perl.txt"
    )

    outputs["gobuster"] = run_command(
        f"gobuster dir -u https://{target} -w /usr/share/wordlists/dirb/common.txt",
        "gobuster.txt"
    )

    outputs["amass"] = run_command(
        f"amass enum -d {target}",
        "amass.txt"
    )

    outputs["subfinder"] = run_command(
        f"subfinder -d {target}",
        "subfinder.txt"
    )

    outputs["dirsearch"] = run_command(
        f"dirsearch -u https://{target}",
        "dirsearch.txt"
    )

    outputs["ffuf"] = run_command(
        f"ffuf -u https://{target}/FUZZ -w /usr/share/wordlists/dirb/common.txt",
        "ffuf.txt"
    )

    return render_template(
        "result.html",
        target=target,
        outputs=outputs
    )


if __name__ == "__main__":
    app.run(debug=True)