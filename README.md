# Directory Fuzzing Tool

## Overview
This directory fuzzing tool is designed to identify valid directories and files on a web server. Using a customizable wordlist, the script attempts to access each path and checks the server's response, allowing security professionals to uncover hidden resources.

## Features
- **Customizable Wordlist:** Load a list of potential directory names from a specified file.
- **Multi-Threading:** Speed up the fuzzing process with concurrent requests.
- **File Extensions Support:** Specify valid file extensions to test for each directory.
- **Response Code Filtering:** Customize which HTTP response codes to consider as valid results.
- **Verbose Mode:** Optionally display all URLs being tested for easier debugging.
- **Output File:** Save successful paths and their corresponding HTTP status codes to a text file.


## Usage
Run the script using Python with the following syntax:
python fuzz.py <url> -w <wordlist> [-e <extensions>] [-r <response-codes>] [-t <threads>] [-o <output-file>] [-v]

## Arguments
<url>: Base URL to fuzz (e.g., http://example.com).
-w, --wordlist: Path to the wordlist file (required).
-e, --extensions: Comma-separated list of valid extensions (default: html,php,asp).
-r, --response-codes: Comma-separated list of response codes to filter (default: 200,301,302).
-t, --threads: Number of threads to use (default: 10).
-o, --output-file: File to save successful directories (default: successful_dirs.txt).
-v, --verbose: Enable verbose mode (show all URLs being tried).

## Example
python fuzz.py http://example.com -w wordlist.txt -e html,php -r 200,301 -t 10 -o successful_dirs.txt -v
