import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urljoin
import time
import shutil
import datetime
import sys
import getpass
import logging
from tqdm import tqdm  # progress bar

# ========= Colors ==========
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

# ========= Security ==========
USERNAME = "alfa-root"
PASSWORD = "alfa-root####"

def check_auth():
    print(f"{YELLOW}[SECURITY]{RESET} Login Required")
    user = input("Enter Username: ")
    pwd = getpass.getpass("Enter Password: ")
    if user == USERNAME and pwd == PASSWORD:
        print(f"{GREEN}[+] Access Granted!{RESET}\n")
    else:
        print(f"{RED}[-] Access Denied!{RESET}")
        sys.exit(1)

# ========= Logging Setup ==========
logging.basicConfig(
    filename="scanner.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ========= ASCII Banner ==========
def print_banner():
    banner = f"""
{CYAN}
░█▀█░█░░░█▀▀░█▀█░░░█▀▄░█▀█░█▀█░▀█▀░░
░█▀█░█░░░█▀▀░█▀█░░░█▀▄░█░█░█░█░░█░░░
░▀░▀░▀▀▀░▀░░░▀░▀░░░▀░▀░▀▀▀░▀▀▀░░▀░░░
                                {YELLOW}Create By Alfa Root-ACS{RESET}
    """
    print(banner)

# ========= Headers ==========
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ========= Core Scanner ==========
def extract_parameters(url, domain, session, visited, max_depth=3, depth=0, pbar=None):
    if depth > max_depth:
        return set()
    
    if url in visited:
        return set()
    
    visited.add(url)
    logging.info(f"Scanning {url}")
    print(f"{BLUE}[*] Scanning:{RESET} {url}")
    if pbar: 
        pbar.update(1)
    
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        parsed = urlparse(url)
        parameters = set(parse_qs(parsed.query).keys())
        
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        for link in links:
            full_url = urljoin(url, link)
            if domain in full_url:
                new_params = extract_parameters(full_url, domain, session, visited, max_depth, depth + 1, pbar)
                parameters.update(new_params)
                
        return parameters
    
    except Exception as e:
        logging.error(f"Error scanning {url}: {e}")
        print(f"{RED}[!] Error:{RESET} {url} -> {e}")
        return set()

# ========= Main ==========
def main():
    check_auth()          # security
    print_banner()        # banner

    # Interactive input for target URL and depth
    target_url = input(f"{YELLOW}Enter target URL: {RESET}").strip()
    depth_input = input(f"{YELLOW}Enter max crawl depth (default 3): {RESET}").strip()
    max_depth = int(depth_input) if depth_input.isdigit() else 3

    session = requests.Session()
    domain = urlparse(target_url).netloc
    visited = set()

    print(f"{YELLOW}[*] Scanning {target_url} down to depth {max_depth}...{RESET}")
    
    with tqdm(total=100, desc="Progress", ncols=100, colour="green") as pbar:
        params = extract_parameters(target_url, domain, session, visited, max_depth, pbar=pbar)

    if params:
        print(f"{GREEN}[+] Found parameters:{RESET}")
        for param in sorted(params):
            print(f"  - {param}")
    else:
        print(f"{RED}[-] No parameters found.{RESET}")

if __name__ == "__main__":
    main()
    
