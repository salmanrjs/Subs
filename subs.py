#!/usr/bin/env python3

import argparse
import socket
import requests
import pyfiglet
import os
import time
import random
from colorama import Fore, Style
from requests.exceptions import RequestException

# ======================
# Config
# ======================
WORDLIST_FILE = "wordlist.txt"
ALLOWED_STATUS = {200, 403, 404}
DELAY_MIN = 0.05
DELAY_MAX = 0.15

# ======================
# Banner
# ======================
def show_banner():
    banner = pyfiglet.figlet_format("subs")
    print(Fore.RED + banner + Style.RESET_ALL)
    print("=" * 50)
    print("Coded by Salman Rajab v1.0")
    print("=" * 50)
    print()

# ======================
# DNS Resolve
# ======================
def dns_resolve(subdomain):
    try:
        socket.gethostbyname(subdomain)
        return True
    except socket.gaierror:
        return False

# ======================
# HTTP Check
# ======================
def check_http(subdomain, timeout):
    urls = [
        f"http://{subdomain}",
        f"https://{subdomain}"
    ]

    for url in urls:
        try:
            r = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={"User-Agent": "subs/1.0"}
            )
            return r.status_code
        except RequestException:
            continue

    return None

# ======================
# Scan Logic
# ======================
def scan(domain, timeout):
    if not os.path.exists(WORDLIST_FILE):
        print(Fore.RED + f"[!] Wordlist file not found: {WORDLIST_FILE}" + Style.RESET_ALL)
        return

    with open(WORDLIST_FILE, "r", encoding="utf-8", errors="ignore") as f:
        words = f.read().splitlines()

    for word in words:
        word = word.strip()
        if not word:
            continue

        subdomain = f"{word}.{domain}"

        if dns_resolve(subdomain):
            status = check_http(subdomain, timeout)

            if status in ALLOWED_STATUS:
                color = Fore.GREEN if status == 200 else Fore.YELLOW
                print(color + f"[+] {subdomain} -> {status}" + Style.RESET_ALL)

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

# ======================
# Main
# ======================
def main():
    show_banner()

    parser = argparse.ArgumentParser(
        description="subs - Subdomain Enumeration Tool",
        usage="subs -d domain.com"
    )

    parser.add_argument(
        "-d", "--domain",
        help="Target domain (example.com)"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=3,
        help="HTTP timeout in seconds"
    )

    args, _ = parser.parse_known_args()

    if not args.domain:
        parser.print_help()
        return

    scan(args.domain, args.timeout)

if __name__ == "__main__":
    main()
