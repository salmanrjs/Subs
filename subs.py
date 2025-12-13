import argparse
import socket
import requests
import pyfiglet
import os
from colorama import Fore, Style
from requests.exceptions import RequestException

# ======================
# Config
# ======================
WORDLIST_FILE = "wordlist.txt"

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
            response = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True
            )
            return response.status_code
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

    with open(WORDLIST_FILE, "r") as f:
        words = f.read().splitlines()

    for word in words:
        if not word.strip():
            continue

        subdomain = f"{word.strip()}.{domain}"

        if dns_resolve(subdomain):
            status = check_http(subdomain, timeout)

            if status:
                print(Fore.GREEN + f"[+] {subdomain} -> {status}" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"[+] {subdomain} -> Alive (No HTTP)" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"[-] {subdomain} -> Dead" + Style.RESET_ALL)

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
        required=True,
        help="Target domain (example.com)"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=3,
        help="HTTP timeout in seconds"
    )

    args = parser.parse_args()
    scan(args.domain, args.timeout)

if __name__ == "__main__":
    main()
