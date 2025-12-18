# subs – Subdomain Enumeration Tool v1.0

subs is a simple command-line tool written in Python. It finds subdomains using a wordlist, checks DNS, then checks the website status. The tool only shows useful results.

---

## Features

* Find subdomains using a wordlist
* Check DNS first, then HTTP
* Show only important results: **200, 403, 404**
* Built-in delay to avoid fast scanning
* Simple and clean output
* Works on Windows and Linux (Kali)

---

## Installation

It is recommended to use a virtual environment (venv).

### Clone the repository

```
git clone https://github.com/salmanrjs/subs.git
cd subs
```

### Create and activate virtual environment

**Kali / Linux**

```
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```
python -m venv venv
.\venv\Scripts\activate
```

### Install requirements

```
pip install -r requirements.txt
```

---

## Usage

The tool reads subdomains from `wordlist.txt`.

### Start scan

```
subs -d example.com
```

### Change timeout (optional)

```
subs -d example.com -t 5
```

* Default timeout: 3 seconds
* Max timeout: 10 seconds

### Show help only

```
subs
```

---

## Output Example

```
[+] api.example.com -> 200
[+] admin.example.com -> 403
[+] test.example.com -> 404
```

---

## Project Files

```
subs/
├── subs.py
├── wordlist.txt
├── requirements.txt
└── README.md
```

---

## Requirements

* Python 3
* requests
* pyfiglet
* colorama

---

## Author

Salman Rajab

---

## Disclaimer

Use this tool only on domains you own or have permission to test.
