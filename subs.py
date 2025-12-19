#!/usr/bin/env python3

import argparse
import socket
import requests
import pyfiglet
import os
import time
from colorama import Fore, Style
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed

# ======================
# Config
# ======================
WORDLIST_FILE = "wordlist.txt"
ALLOWED_STATUS = {200, 403, 404}
DELAY = 0.03
DEFAULT_TIMEOUT = 3
MAX_TIMEOUT = 10

# ======================
# Banner
# ======================
def show_banner():
    banner = pyfiglet.figlet_format("SubS")
    print(Fore.RED + banner + Style.RESET_ALL)
    print("-" * 30)
    print(Fore.YELLOW + "# Subdomain Enumeration Tool" + Style.RESET_ALL)
    print(Fore.CYAN + "# Coded by Salman Rajab v1.0" + Style.RESET_ALL)
    print("-" * 30)
    print()

def show_usage():
    print(Fore.GREEN + "Usage: python subs.py -d domain.com" + Style.RESET_ALL)
    print()

# ======================
# Auto Threads Logic
# ======================
def get_auto_threads(word_count):
    if word_count < 5000:
        return 1
    elif word_count < 30000:
        return 3
    elif word_count < 100000:
        return 5
    else:
        return 8

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
# Worker
# ======================
def process_word(word, domain, timeout):
    word = word.strip()
    if not word:
        return

    subdomain = f"{word}.{domain}"

    if dns_resolve(subdomain):
        status = check_http(subdomain, timeout)

        if status in ALLOWED_STATUS:
            if status == 200:
                color = Fore.GREEN
            elif status == 403:
                color = Fore.YELLOW
            elif status == 404:
                color = Fore.RED
            else:
                color = Fore.WHITE

            print(color + f"[+] {subdomain} -> {status}" + Style.RESET_ALL)

    time.sleep(DELAY)

# ======================
# Scan Logic
# ======================
def scan(domain, timeout):
    if not os.path.exists(WORDLIST_FILE):
        print(Fore.RED + f"[!] Wordlist file not found: {WORDLIST_FILE}" + Style.RESET_ALL)
        return

    with open(WORDLIST_FILE, "r", encoding="utf-8", errors="ignore") as f:
        words = f.read().splitlines()

    thread_count = get_auto_threads(len(words))

    print(Fore.CYAN + "[*] Start scanning..." + Style.RESET_ALL)

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [
            executor.submit(process_word, word, domain, timeout)
            for word in words
        ]

        for _ in as_completed(futures):
            pass

# ======================
# Main
# ======================
def main():
    show_banner()

    parser = argparse.ArgumentParser(
        usage=argparse.SUPPRESS,
        description=None,
        add_help=False
    )

    parser.add_argument(
        "-d", "--domain",
        metavar="",
        help="Target Domain (example.com)"
    )

    parser.add_argument(
        "-t", "--timeout",
        metavar="",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout in seconds"
    )

    args = parser.parse_args()

    if not args.domain:
        show_usage()
        parser.print_help()
        return

    # timeout validation
    if args.timeout <= 0:
        print(Fore.YELLOW + "[!] Invalid timeout. Using default (3s)." + Style.RESET_ALL)
        args.timeout = DEFAULT_TIMEOUT
    elif args.timeout > MAX_TIMEOUT:
        print(
            Fore.YELLOW
            + f"[!] Timeout too high. Max allowed is {MAX_TIMEOUT}s. Using {MAX_TIMEOUT}s."
            + Style.RESET_ALL
        )
        args.timeout = MAX_TIMEOUT

    scan(args.domain, args.timeout)

if __name__ == "__main__":
    main()
