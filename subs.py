import argparse
import socket
import requests
import pyfiglet
import os
import time
from colorama import Fore, Style
from requests.exceptions import RequestException

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

    print(Fore.CYAN + "[*] Start scanning..." + Style.RESET_ALL)

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

