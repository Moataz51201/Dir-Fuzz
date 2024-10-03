import requests
import threading
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
]

# List of proxies (if you want to use proxies to avoid blocking)
#PROXIES = [
 #   'http://proxy1.example.com:8080',
  #  'http://proxy2.example.com:8080',
    # Add as many proxies as needed
#]

def create_session_with_retries():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def fuzz_directory(base_url, wordlist, valid_extensions, response_codes, output_file, max_threads=10, verbose=False):
    lock = threading.Lock()
    paths = [line.strip() for line in open(wordlist, 'r') if line.strip() and not line.startswith('#')]
    total_urls = len(paths) * (len(valid_extensions) + 1)
    tried_urls = [0]

    session = create_session_with_retries()
    with open(output_file, 'a') as f_out:
        def fuzz_path(path):
            if "#" in path:
                return
            
            url = f"{base_url}/{path}"
            try:
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                response = session.get(url, headers=headers, timeout=15)
                with lock:
                    tried_urls[0] += 1
                    progress = f"Progress: {tried_urls[0]}/{total_urls} URLs tried"
                    sys.stdout.write(f"\r{progress}")
                    sys.stdout.flush()

                if verbose:
                    print(f"\nTrying: {url}")

                if response.status_code in response_codes:
                    print(f"\n[{response.status_code}] Found: {url}")
                    f_out.write(f"[{response.status_code}] Valid : {url}\n")
            except requests.exceptions.RequestException as e:
                if verbose:
                    print(f"\nRequest failed for {url}: {e}")

            for ext in valid_extensions:
                url_with_ext = f"{base_url}/{path}.{ext}"
                try:
                    time.sleep(random.uniform(0.5, 2))  # Random delay
                    headers = {'User-Agent': random.choice(USER_AGENTS)}
                    response = session.get(url_with_ext, headers=headers, timeout=15)
                    with lock:
                        tried_urls[0] += 1
                        progress = f"Progress: {tried_urls[0]}/{total_urls} URLs tried"
                        sys.stdout.write(f"\r{progress}")
                        sys.stdout.flush()

                    if verbose:
                        print(f"\nTrying: {url_with_ext}")

                    if response.status_code in response_codes:
                        print(f"\n[{response.status_code}] Found: {url_with_ext}")
                        f_out.write(f"[{response.status_code}] Valid : {url_with_ext}\n")
                except requests.exceptions.RequestException as e:
                    if verbose:
                        print(f"\nRequest failed for {url_with_ext}: {e}")

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(fuzz_path, path) for path in paths]
            for future in as_completed(futures):
                future.result()

    print("\nFuzzing completed!")


# Main function with argument parsing
def main():
    parser = argparse.ArgumentParser(description="Directory Fuzzing Script")
    
    
    parser.add_argument("url", help="Base URL to fuzz (e.g., http://example.com)")
    
    
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    
    
    parser.add_argument("-e", "--extensions", default="html,php,asp", 
                        help="Comma-separated list of valid extensions (default: html,php,asp)")
    
    
    parser.add_argument("-r", "--response-codes", default="200,301,302", 
                        help="Comma-separated list of response codes to filter (default: 200,301,302)")
    
    
    parser.add_argument("-t", "--threads", type=int, default=10, 
                        help="Number of threads to use (default: 10)")
                        
    parser.add_argument("-o", "--output-file", default="successful_dirs.txt", 
                        help="File to save successful directories (default: successful_dirs.txt)")                    

    
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Enable verbose mode (show all URLs being tried)")

    
    args = parser.parse_args()
    
    # Convert comma-separated extensions and response codes to lists
    valid_extensions = args.extensions.split(',')
    response_codes = list(map(int, args.response_codes.split(',')))
    
    
    fuzz_directory(args.url, args.wordlist, valid_extensions, response_codes, args.output_file, args.threads, args.verbose)

if __name__ == "__main__":
    main()
