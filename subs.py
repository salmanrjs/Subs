import argparse
import socket
import requests
import pyfiglet
import os
import time
from colorama import Fore, Style
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# ======================
# Config
# ======================
DEFAULT_WORDLIST_FILE = "wordlist.txt"
ALLOWED_STATUS = {200, 403, 404}
DELAY = 0.03
DEFAULT_TIMEOUT = 3
MAX_TIMEOUT = 10
DEFAULT_OUTPUT = None
VERSION = "v2.0"

# Thread-safe output
print_lock = Lock()
file_lock = Lock()

# ======================
# Banner / Interface
# ======================
def show_banner():
    banner = pyfiglet.figlet_format("SubS")
    print(Fore.RED + banner + Style.RESET_ALL)
    print("-" * 40)
    print(Fore.YELLOW + "# Subdomain Enumeration Tool" + Style.RESET_ALL)
    print(Fore.CYAN + f"# Coded by Salman Rajab {VERSION}" + Style.RESET_ALL)
    print("-" * 40)
    print(Fore.GREEN + "Commands:" + Style.RESET_ALL)
    print(Fore.GREEN + "  -d, --domain     Target domain (example.com)" + Style.RESET_ALL)
    print(Fore.GREEN + "  -w, --wordlist   Wordlist file path (optional)" + Style.RESET_ALL)
    print(Fore.GREEN + "  -t, --timeout    HTTP timeout in seconds" + Style.RESET_ALL)
    print(Fore.GREEN + "  -T, --threads    Number of threads (optional; defaults to auto)" + Style.RESET_ALL)
    print(Fore.GREEN + "  -o, --output     Save results to a text file (optional)" + Style.RESET_ALL)
    print("-" * 40)
    print()

def show_usage():
    print(Fore.GREEN + "Usage examples:" + Style.RESET_ALL)
    print(Fore.GREEN + "  python subs.py -d domain.com" + Style.RESET_ALL)
    print(Fore.GREEN + "  python subs.py -d domain.com -w mylist.txt" + Style.RESET_ALL)
    print(Fore.GREEN + "  python subs.py -d domain.com -o results.txt" + Style.RESET_ALL)
    print(Fore.GREEN + "  python subs.py -d domain.com -T 10" + Style.RESET_ALL)
    print(Fore.GREEN + "  python subs.py -d domain.com -T 10 -o results.txt -t 5 -w mylist.txt" + Style.RESET_ALL)
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
                headers={"User-Agent": f"subs/{VERSION}"}
            )
            return r.status_code
        except RequestException:
            continue

    return None

# ======================
# Output Helpers
# ======================
def write_result(output_file, line):
    if not output_file:
        return
    with file_lock:
        with open(output_file, "a", encoding="utf-8", errors="ignore") as f:
            f.write(line + "\n")

def print_result(color, line):
    with print_lock:
        print(color + line + Style.RESET_ALL)

# ======================
# Worker
# ======================
def process_word(word, domain, timeout, output_file):
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

            line = f"[+] {subdomain} -> {status}"
            print_result(color, line)
            write_result(output_file, line)

    time.sleep(DELAY)

# ======================
# Scan Logic
# ======================
def scan(domain, timeout, threads, output_file, wordlist_file):
    if not os.path.exists(wordlist_file):
        print(Fore.RED + f"[!] Wordlist file not found: {wordlist_file}" + Style.RESET_ALL)
        return

    with open(wordlist_file, "r", encoding="utf-8", errors="ignore") as f:
        words = f.read().splitlines()

    auto_threads = get_auto_threads(len(words))
    thread_count = threads if threads is not None else auto_threads

    print(Fore.CYAN + "[*] Start scanning..." + Style.RESET_ALL)
    print(Fore.CYAN + f"[*] Wordlist: {wordlist_file} ({len(words)} words)" + Style.RESET_ALL)
    print(Fore.CYAN + f"[*] Threads: {thread_count}" + Style.RESET_ALL)
    print(Fore.CYAN + f"[*] Timeout: {timeout}s" + Style.RESET_ALL)
    if output_file:
        print(Fore.CYAN + f"[*] Output: {output_file}" + Style.RESET_ALL)

        try:
            with open(output_file, "w", encoding="utf-8", errors="ignore") as f_out:
                f_out.write(f"# SubS {VERSION}\n")
                f_out.write(f"# Target: {domain}\n")
                f_out.write(f"# Wordlist: {wordlist_file}\n")
                f_out.write(f"# Threads: {thread_count}\n")
                f_out.write(f"# Timeout: {timeout}s\n")
                f_out.write("-" * 30 + "\n")
        except OSError as e:
            print(Fore.RED + f"[!] Cannot write to output file: {e}" + Style.RESET_ALL)
            output_file = None

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [
            executor.submit(process_word, word, domain, timeout, output_file)
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
        "-w", "--wordlist",
        metavar="",
        default=DEFAULT_WORDLIST_FILE,
        help="Wordlist file path (optional)"
    )

    parser.add_argument(
        "-t", "--timeout",
        metavar="",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout in seconds"
    )

    parser.add_argument(
        "-T", "--threads",
        metavar="",
        type=int,
        default=None,
        help="Number of threads (optional; defaults to auto)"
    )

    parser.add_argument(
        "-o", "--output",
        metavar="",
        default=DEFAULT_OUTPUT,
        help="Output file to save results (optional)"
    )

    args = parser.parse_args()

    if not args.domain:
        show_usage()
        parser.print_help()
        return

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

    if args.threads is not None:
        if args.threads <= 0:
            print(Fore.YELLOW + "[!] Invalid threads. Using auto threads." + Style.RESET_ALL)
            args.threads = None
        elif args.threads > 200:
            print(Fore.YELLOW + "[!] Threads too high. Capping to 200." + Style.RESET_ALL)
            args.threads = 200

    scan(args.domain, args.timeout, args.threads, args.output, args.wordlist)

if __name__ == "__main__":
    main()
