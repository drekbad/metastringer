#!/usr/bin/env python3

import requests
import argparse
from argparse import ArgumentParser
import sys
import time
import json
import os
import subprocess
import shutil
import csv


mime_type_mapping = {
    "application/pdf": {"definite": ".pdf"},
    "application/msword": {"definite": ".doc"},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {"definite": ".docx"},
    "application/vnd.ms-excel": {"definite": ".xls"},
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {"definite": ".xlsx"},
    "application/vnd.ms-powerpoint": {"definite": ".ppt"},
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": {"definite": ".pptx"},
    "application/javascript": {"definite": ".js"},
    "application/json": {"definite": ".json"},
    "application/xml": {"definite": ".xml"},
    "text/html": {"definite": ".html"},
    "text/css": {"definite": ".css"},
    "text/csv": {"definite": ".csv"},
    "text/plain": {"definite": ".txt"},
    "image/jpeg": {"definite": ".jpg"},
    "image/png": {"definite": ".png"},
    "image/gif": {"definite": ".gif"},
    "image/svg+xml": {"definite": ".svg"},
    "image/tiff": {"definite": ".tiff"},
    "image/bmp": {"definite": ".bmp"},
    "image/webp": {"definite": ".webp"},
    "image/x-icon": {"definite": ".ico"},
    "audio/mpeg": {"definite": ".mp3"},
    "audio/ogg": {"definite": ".ogg"},
    "audio/wav": {"definite": ".wav"},
    "audio/aac": {"definite": ".aac"},
    "audio/midi": {"definite": ".midi"},
    "video/mp4": {"definite": ".mp4"},
    "video/mpeg": {"definite": ".mpeg"},
    "video/ogg": {"definite": ".ogv"},
    "video/webm": {"definite": ".webm"},
    "video/quicktime": {"definite": ".mov"},
    "video/x-msvideo": {"definite": ".avi"},
    "video/x-ms-wmv": {"definite": ".wmv"},
    "application/zip": {"definite": ".zip"},
    "application/x-rar-compressed": {"definite": ".rar"},
    "application/x-tar": {"definite": ".tar"},
    "application/gzip": {"definite": ".gz"},
    "application/x-7z-compressed": {"definite": ".7z"},
    "application/x-iso9660-image": {"definite": ".iso"},
    "application/vnd.adobe.flash.movie": {"definite": ".swf"},
    "application/x-shockwave-flash": {"definite": ".swf"},
    "application/java-archive": {"definite": ".jar"},
    "application/x-perl": {"definite": ".pl"},
    "application/x-python": {"definite": ".py"},
    "application/x-ruby": {"definite": ".rb"},
    "application/x-php": {"definite": ".php"},
    "application/x-httpd-php": {"definite": ".php"},
    "application/vnd.apple.installer+xml": {"definite": ".mpkg"},
    "application/x-dosexec": {"definite": ".exe"},
    "application/x-msdownload": {"definite": ".exe"},
    "application/x-font-ttf": {"definite": ".ttf"},
    "application/font-woff": {"definite": ".woff"},
    "application/font-woff2": {"definite": ".woff2"},
    "application/octet-stream": {"likely": [".bin", ".exe", ".dll"]},
    "application/octet-stream": {"likely": [".bin", ".exe", ".dll"]},
    "application/vnd.ms-fontobject": {"definite": ".eot"},
    "binary/octet-stream": {"likely": [".bin", ".class", ".dex"]},
    "font/ttf": {"definite": ".ttf"},
    "font/woff": {"definite": ".woff"},
    "font/woff2": {"definite": ".woff2"},
    "text/javascript": {"definite": ".js"},
    "text/js": {"definite": ".js"},
    "text/xml": {"definite": ".xml"},
    "unk": {"likely": ["could be any binary data", "extension not provided"]},
    "warc/revisit": {"likely": ["specific to web archiving; not a typical file extension"]},
}


strictness_2_mime_mapping = {
    "pdf": ["application/pdf"],
    "doc": ["application/msword"],
    "docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
    "xls": ["application/vnd.ms-excel"],
    "xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
    "ppt": ["application/vnd.ms-powerpoint"],
    "pptx": ["application/vnd.openxmlformats-officedocument.presentationml.presentation"],
}


strictness_1_mime_mapping = {
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "svg": "image/svg+xml",
    "tiff": "image/tiff",
    "bmp": "image/bmp",
    "webp": "image/webp",
    "ico": "image/x-icon",
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "wav": "audio/wav",
    "aac": "audio/aac",
    "midi": "audio/midi",
    "mp4": "video/mp4",
    "mpeg": "video/mpeg",
    "ogv": "video/ogg",
    "webm": "video/webm",
    "mov": "video/quicktime",
    "avi": "video/x-msvideo",
    "wmv": "video/x-ms-wmv",
    "zip": "application/zip",
    "rar": "application/x-rar-compressed",
    "tar": "application/x-tar",
    "gz": "application/gzip",
    "7z": "application/x-7z-compressed",
    "iso": "application/x-iso9660-image",
    "swf": "application/x-shockwave-flash",
    "jar": "application/java-archive",
    "py": "application/x-python",
    "php": "application/x-httpd-php",
    "html": "text/html",
    "css": "text/css",
    "csv": "text/csv",
    "txt": "text/plain",
    "xml": "application/xml",
    "json": "application/json",
    "js": "application/javascript",
}


strictness_0_mime_mapping = {
    "pdf": ["application/pdf", "text/html", "application/octet-stream"],
    "doc": ["application/msword", "text/html", "application/octet-stream"],
    "docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/html", "application/octet-stream"],
    "xls": ["application/vnd.ms-excel", "text/html", "application/octet-stream"],
    "xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "text/html", "application/octet-stream"],
    "ppt": ["application/vnd.ms-powerpoint", "text/html", "application/octet-stream"],
    "pptx": ["application/vnd.openxmlformats-officedocument.presentationml.presentation", "text/html", "application/octet-stream"],
    "jpg": ["image/jpeg", "text/html", "application/octet-stream"],
    "jpeg": ["image/jpeg", "text/html", "application/octet-stream"],
    "png": ["image/png", "text/html", "application/octet-stream"],
    "gif": ["image/gif", "text/html", "application/octet-stream"],
    "svg": ["image/svg+xml", "text/html", "application/octet-stream"],
    "tiff": ["image/tiff", "text/html", "application/octet-stream"],
    "bmp": ["image/bmp", "text/html", "application/octet-stream"],
    "webp": ["image/webp", "text/html", "application/octet-stream"],
    "ico": ["image/x-icon", "text/html", "application/octet-stream"],
    "mp3": ["audio/mpeg", "text/html", "application/octet-stream"],
    "ogg": ["audio/ogg", "text/html", "application/octet-stream"],
    "wav": ["audio/wav", "text/html", "application/octet-stream"],
    "aac": ["audio/aac", "text/html", "application/octet-stream"],
    "midi": ["audio/midi", "text/html", "application/octet-stream"],
    "mp4": ["video/mp4", "text/html", "application/octet-stream"],
    "mpeg": ["video/mpeg", "text/html", "application/octet-stream"],
    "ogv": ["video/ogg", "text/html", "application/octet-stream"],
    "webm": ["video/webm", "text/html", "application/octet-stream"],
    "mov": ["video/quicktime", "text/html", "application/octet-stream"],
    "avi": ["video/x-msvideo", "text/html", "application/octet-stream"],
    "wmv": ["video/x-ms-wmv", "text/html", "application/octet-stream"],
    "zip": ["application/zip", "text/html", "application/octet-stream"],
    "rar": ["application/x-rar-compressed", "text/html", "application/octet-stream"],
    "tar": ["application/x-tar", "text/html", "application/octet-stream"],
    "gz": ["application/gzip", "text/html", "application/octet-stream"],
    "7z": ["application/x-7z-compressed", "text/html", "application/octet-stream"],
    "iso": ["application/x-iso9660-image", "text/html", "application/octet-stream"],
    "swf": ["application/x-shockwave-flash", "text/html", "application/octet-stream"],
    "jar": ["application/java-archive", "text/html", "application/octet-stream"],
    "py": ["application/x-python", "text/html", "application/octet-stream"],
    "php": ["application/x-httpd-php", "text/html", "application/octet-stream"],
    "html": ["text/html", "application/octet-stream"],
    "css": ["text/css", "text/html", "application/octet-stream"],
    "csv": ["text/csv", "text/html", "application/octet-stream"],
    "txt": ["text/plain", "text/html", "application/octet-stream"],
    "xml": ["application/xml", "text/html", "application/octet-stream", "text/plain"],
    "json": ["application/json", "text/html", "application/octet-stream", "text/plain"],
    "js": ["application/javascript", "text/html", "application/octet-stream", "text/plain"],
}


# Where a MIME type has only one good file extension
exclusive_mime_type_mapping = {
    "image/gif": ".gif",
    "image/jpeg": ".jpg",
}


# Used to highlight extensions of interest in MIME type table
highlight_types = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


# Used to highlight metadata of interest in metadata output (single record search only)
highlight_keys = ['File Name', 'Author', 'Creator', 'Producer']


# ANSI color codes
green_start = "\033[92m"
green_end = "\033[0m"
blue_start = "\033[94m"
blue_end = "\033[0m"
red_start = "\033[91m"
red_end = "\033[0m"

italics_start = "\033[3m"
italics_end = "\033[0m"

files_downloaded = False
# Global set to keep track of extensions for which option 5 has been completed
tested_extensions = set()
# Global variable to track the current rate limit
current_rate_limit = 0.5  # Default value, can be modified by the script


def main():
    try:
        args = parse_arguments()
        rate_limit = args.rate_limit  # Capture the rate limit value
        strictness = args.strictness
        domain = remove_www_prefix(args.domain)
        file_list, server_response_time, unique_mime_types_count, cache_age = fetch_file_list(domain, args.nocache)

        if cache_age > 0:
            print(f"\nServer response time: {server_response_time:.2f} seconds {blue_start}{italics_start}(due to {cache_age:.1f} day old cache file){italics_end}{blue_end}")
        else:
            print(f"\nServer response time: {server_response_time:.2f} seconds")

        chosen_extension = None
        if args.ext or args.filetype:
            chosen_extension = args.ext if args.ext else args.filetype

        while True:
            if not chosen_extension:
                # Display MIME types count and table
                print(f"{green_start}{unique_mime_types_count} MIME types{green_end} for target: {green_start}{domain.upper()}{green_end}\n")
                definitive_results, likely_results, uncertain_results = list_file_types(file_list, domain)
                print_results(definitive_results, likely_results, uncertain_results, domain)
                chosen_extension = prompt_for_extension(file_list, domain, unique_mime_types_count)

            # Process the chosen extension
            result, matching_urls = process_filetype(file_list, chosen_extension, domain, unique_mime_types_count, strictness, args.verbosity, args.rate_limit)

            if result == "no_files_found":
                action = handle_no_files_found(chosen_extension)
                if action == "show_mime_list":
                    chosen_extension = None  # Reset chosen_extension to None to display MIME types again
                    continue
                elif action in ['q', 'quit', 'exit']:
                    sys.exit(0)
                else:
                    chosen_extension = action  # Set new chosen extension

            elif result == "files_found":
                # Display the menu and handle the choice
                test_files_for_metadata(matching_urls, chosen_extension, domain, rate_limit, portion=False, verbosity=args.verbosity)
                new_extension = display_menu_and_handle_choice(matching_urls, chosen_extension, domain, unique_mime_types_count, file_list, strictness, args.verbosity, args.rate_limit)
                if new_extension == 'new_extension':
                    chosen_extension = None  # Reset for new extension input
                elif new_extension == 'show_mime_list':
                    chosen_extension = None  # Reset to show MIME types again

            # Reset chosen_extension to None for the next iteration
            chosen_extension = None

        if args.rate_limit:
            manage_traffic(args.rate_limit)

        if files_downloaded:
            remove_downloaded_files()
    except KeyboardInterrupt:
        sys.exit(0)


def prompt_for_extension(file_list, domain, unique_mime_types_count):
    while True:
        print("Enter an extension to retrieve (e.g., 'pdf'), or type 'exit' to quit:\n")
        chosen_extension = input().lower()

        if chosen_extension in ['q', 'quit', 'exit']:
            sys.exit(0)
        elif chosen_extension.strip() == "":
            print("Invalid input. Please enter a valid extension or type 'exit' to quit.")
        else:
            return chosen_extension


def extract_extension_from_url(url):
    if '?' in url:
        url = url.split('?', 1)[0]  # Take the part before the query parameters
    ext = url.rsplit('.', 1)[-1]
    if ext and '/' not in ext:  # Check if it's a valid extension
        return '.' + ext  # Ensure the dot is included
    return None
    
    
def process_extension(file_list, domain, unique_mime_types_count, strictness, chosen_extension, verbosity, rate_limit):
    result, matching_urls = process_filetype(file_list, chosen_extension, domain, unique_mime_types_count, strictness, verbosity, rate_limit)

    if result == "no_files_found":
        action = handle_no_files_found(chosen_extension)
        if action == "show_mime_list":
            return "show_mime_list"  # Pass this flag back up to the caller
        elif action in ['q', 'quit', 'exit']:
            sys.exit(0)
        return None if action == "list_mime_types" else action
    elif result == "files_found":
        new_extension = display_menu_and_handle_choice(matching_urls, chosen_extension, domain, unique_mime_types_count, file_list, strictness, verbosity, rate_limit)
        if new_extension == 'return_to_extension_selection':
            return None
        elif new_extension:
            return new_extension
    return None


def analyze_extensions_for_mime_type(mime_type, file_list):
    # logic to parse URLs and extract potential extensions
    # Return a list of found extensions
    pass
 
 
def format_extension_output(mime_type, url, mapping):
    extension = extract_extension_from_url(url)
    if extension:
        certainty = "DEFINITELY"
        extension_info = extension
    else:
        certainty = "LIKELY" if mapping["likely"] != "Various" else "UNKNOWN"
        extension_info = mapping["likely"]
        if mapping["alternatives"]:
            extension_info += " (or possibly: " + ", ".join(mapping["alternatives"]) + ")"
    
    return f"{mime_type:<30} {certainty:<10} {extension_info}"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Script to fetch and process files from the Wayback Machine.")
    parser.add_argument("domain", help="The domain to search.")
    parser.add_argument("filetype", nargs='?', help="The filetype to process. If not specified, all file types will be listed.", default=None)
    parser.add_argument("--ext", help="The filetype to process.", default=None)
    parser.add_argument("--rate-limit", type=float, help="Time in seconds to wait between requests.", default=0.5)
    parser.add_argument("--nocache", action='store_true', help="Bypass cache and fetch fresh data.")
    parser.add_argument("--strictness", type=int, choices=[0, 1, 2], default=1, help="Set the strictness level for file type detection.")
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="Increase output verbosity")
    return parser.parse_args()


def remove_www_prefix(domain):
    return domain[4:] if domain.startswith("www.") else domain


def fetch_file_list(domain, bypass_cache=False):
    cache_dir = "./cache"
    cache_filename = f"cache_{domain}_{time.strftime('%Y%m%d')}.json"
    cache_filepath = os.path.join(cache_dir, cache_filename)

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Check if cache file exists and is not older than 14 days
    if not bypass_cache and os.path.exists(cache_filepath) and time.time() - os.path.getmtime(cache_filepath) < 14 * 86400:
        try:
            with open(cache_filepath, 'r') as cache_file:
                file_list = json.load(cache_file)
            unique_mime_types = set(item[1] for item in file_list[1:])
            cache_age = (time.time() - os.path.getmtime(cache_filepath)) / 86400  # Cache age in days
            return file_list, 0.0, len(unique_mime_types), cache_age
        except json.JSONDecodeError:
            print("Corrupted cache file. Fetching fresh data.")
            # Continue to fetch new data if cache is corrupted

    # Fetch new data if cache is outdated or doesn't exist
    start_time = time.time()
    url = f"https://web.archive.org/web/timemap/?url=http://{domain}/&matchType=prefix&collapse=urlkey&output=json&fl=original%2Cmimetype%2Ctimestamp%2Cendtimestamp%2Cgroupcount%2Cuniqcount&filter=!statuscode%3A%5B45%5D..&limit=100000"
    response = requests.get(url)
    server_response_time = time.time() - start_time
    if response.status_code == 200:
        file_list = json.loads(response.text)
        with open(cache_filepath, 'w') as cache_file:
            json.dump(file_list, cache_file)
        unique_mime_types = set(item[1] for item in file_list[1:])
        return file_list, server_response_time, len(unique_mime_types), 0  # 0 for cache_age indicates fresh fetch
    else:
        print(f"Failed to fetch data for {domain}. Status code: {response.status_code}")
        sys.exit(1)


def list_file_types(file_list, domain):
    # Initialize dictionaries for different categories
    definitive_results = {}
    uncertain_results = set()
    likely_results = {}

    # Process each MIME type in the file list
    for item in file_list[1:]:
        mime_type = item[1]
        mapping = mime_type_mapping.get(mime_type, {"definite": None, "likely": []})
        definite_extension = mapping.get("definite")
        likely_extensions = mapping.get("likely", [])

        if definite_extension:
            definitive_results[mime_type] = definite_extension
        elif likely_extensions:
            likely_results[mime_type] = likely_extensions
        else:
            uncertain_results.add(mime_type)

    # Return the collected data without printing
    return definitive_results, likely_results, uncertain_results
    
    
def print_results(definitive_results, likely_results, uncertain_results, domain):

    header_length = max(len(domain) + len("MIME types for target: "), 60)
    print("-" * header_length)
    print(f"{'MIME Type':<30} {'Certainty':<15} {'Extension(s)':<15}")
    print("-" * header_length)

    # Print definitive results
    for mime_type, extension in sorted(definitive_results.items()):
        if mime_type in highlight_types:
            # Apply red color only to 'MIME Type' and 'Extension(s)'
            print(f"{red_start}{mime_type:<30}{red_end} {'DEFINITE':<15} {red_start}{extension:<15}{red_end}")
        else:
            # No color
            print(f"{blue_start}{mime_type:<30}{blue_end} {'DEFINITE':<15} {extension:<15}")

    # Print likely results
    for mime_type, extensions in sorted(likely_results.items()):
        ext_text = ', '.join(extensions)
        print(f"{blue_start}{mime_type:<30}{blue_end} {'LIKELY':<15} {ext_text:<15}")

    # Print uncertain results
    for mime_type in sorted(uncertain_results):
        print(f"{blue_start}{mime_type:<30}{blue_end} {'UNCERTAIN':<15}")

    # Print a final line to end the section
    print("-" * header_length)


def process_filetype(file_list, filetype, domain, unique_mime_types_count, strictness, verbosity, rate_limit):
    if not filetype:
        filetype = "unknown"  # Default value or handle it appropriately

    mime_type = find_mime_type(filetype, strictness)
    matching_urls = []

    for item in file_list:
        url, archive_number, item_mime_type = item[0], item[2], item[1]
        ext_in_url = extract_extension_from_url(url)

        # Check for exclusive MIME type association with a different extension
        if item_mime_type in exclusive_mime_type_mapping and exclusive_mime_type_mapping[item_mime_type] != '.' + filetype:
            continue

        if strictness in [0, 1]:
            # Exclude if URL has a different extension, except if MIME type is a native match for level 1
            if ext_in_url and ext_in_url != '.' + filetype:
                if strictness == 1 and strictness_1_mime_mapping.get(filetype) != item_mime_type:
                    continue
                elif strictness == 0:
                    continue  # Apply the same logic for level 0

            # Include URLs ending with the filetype or MIME type matches
            if ext_in_url == '.' + filetype or item_mime_type in mime_type:
                matching_urls.append((url, archive_number, item_mime_type))
        elif strictness == 2 and ext_in_url == '.' + filetype and item_mime_type in mime_type:
            matching_urls.append((url, archive_number, item_mime_type))

    if len(matching_urls) == 0:
        return "no_files_found", None

    print(f"\nFound {green_start}{len(matching_urls)}{green_end} files with the extension {green_start}'{filetype}'{green_end} and MIME type '{mime_type}'.")
    display_menu_and_handle_choice(matching_urls, filetype, domain, unique_mime_types_count, file_list, strictness, verbosity, rate_limit)

    return "files_found", matching_urls


def handle_no_files_found(filetype):
    print(f"\n{italics_start}{red_start}No files found{red_end} with the extension {red_start}'{filetype}'{red_end}.{italics_end}")
    print("Enter a different extension, or:")
    print("1: See a list of all discovered MIME types and extensions")
    print("2: Quit")
    choice = input("\n").lower()

    if choice == '1':
        return "show_mime_list"  # Return a flag indicating to show MIME list
    elif choice in ['2', 'q', 'quit', 'exit']:
        sys.exit(0)
    else:
        return choice


def display_menu_and_handle_choice(matching_urls, filetype, domain, unique_mime_types_count, file_list, strictness, verbosity, rate_limit):
    global tested_extensions
    while True:
        print("\nSelect an option:")
        print("1: Print the list of URLs")
        print("2: Save the list to a file")
        print("3: Choose a different extension")
        print(f"4: {red_start}[NOT YET IMPLEMENTED]{red_end} Test a portion of the files for metadata")
        if filetype in tested_extensions:
            print(f"5: {green_start}[COMPLETED]{green_end} Test all files for metadata")
        else:
            print("5: Test all files for metadata")
        print("6: Quit")
        choice = input("\n").lower()

        if choice in ['1', 'p']:
            print_urls([url for url, _, _ in matching_urls])  # Adjusted for three elements
            download_prompt(matching_urls)
        elif choice in ['2', 's']:
            save_to_csv(matching_urls, filetype, domain)
        elif choice == '3':
            new_extension = prompt_for_extension(file_list, domain, unique_mime_types_count)
            if new_extension:
                return process_extension(file_list, domain, unique_mime_types_count, strictness, new_extension, verbosity, rate_limit)
            else:
                return 'return_to_extension_selection'
        elif choice == '4':
            test_files_for_metadata(matching_urls, filetype, domain, rate_limit, portion=True, verbosity=verbosity)
        elif choice == '5':
            test_files_for_metadata(matching_urls, filetype, domain, rate_limit, portion=False, verbosity=verbosity)
        elif choice in ['6', 'q', 'quit', 'exit']:
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a valid option.")
    return None  # Return None or a default value if no new extension is chosen


def find_mime_type(extension, strictness):
    if strictness == 0:
        return strictness_0_mime_mapping.get(extension, ["text/plain"])
    elif strictness == 2:
        # Placeholder for future development
        return strictness_2_mime_mapping.get(extension, ["text/plain"])
    else:  # Default strictness
        return strictness_1_mime_mapping.get(extension, ["text/plain"])


def save_to_csv(matching_urls, filetype, domain):
    filename = f"archived_{filetype}_{domain}.csv"
    if os.path.exists(filename):
        print(f"File '{filename}' already exists.")
        print("Select an option:")
        print("1: Overwrite the file")
        print("2: Rename and save the file")
        print("3: Cancel")
        save_choice = input("\nEnter your choice (1-3): ")
        if save_choice == '2':
            new_filename = input("Enter the new filename: ")
            filename = new_filename if new_filename.endswith('.csv') else new_filename + '.csv'
        elif save_choice == '3' or save_choice.lower() == 'q':
            return

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['MIME Type', 'Original URL', 'Archived Download URL'])
        for original_url, archive_number, mime_type in matching_urls:
            download_url = f"https://web.archive.org/web/{archive_number}/{original_url}"
            csvwriter.writerow([mime_type, original_url, download_url])

    print(f"File saved as {filename}")


def download_prompt(matching_urls):
    while True:
        print("\nEnter a URL to retrieve a file, [r]eturn to the previous menu, or [q]uit:")
        selected_url = input().strip()  # Removed the .lower() method

        if selected_url == 'r':
            return
        elif selected_url == 'q':
            sys.exit(0)
        elif any(selected_url == url for url, _, _ in matching_urls):
            retrieve_file(selected_url, matching_urls)
        else:
            print("URL not found in the list. Please enter a valid URL.")


def retrieve_file(selected_url, matching_urls):
    archive_number = next((archive_number for url, archive_number, _ in matching_urls if url == selected_url), None)
    if archive_number:
        download_url = f"https://web.archive.org/web/{archive_number}/{selected_url}"
        print(f"\nAttempting to download from: {download_url}")
        file_path = download_file(download_url)
        if file_path:
            metadata = extract_metadata(file_path)
            print_extracted_metadata(metadata)
            ask_remove_downloaded_files(file_path)
    else:
        print("\nArchive number not found for the selected URL.")


def print_extracted_metadata(metadata):
    if metadata:
        print("\033[4mExtracted Metadata:\033[0m")
        for key, value in metadata.items():
            if key in highlight_keys:
                print(f"{key}: \033[92m{value}\033[0m")  # Highlighted
            else:
                print(f"{key}: {value}")
    else:
        print("No metadata found or extractable for this file.")


def ask_remove_downloaded_files(retrieved_file_path):
    directory = os.path.dirname(retrieved_file_path)
    all_files = os.listdir(directory)

    # Ask to remove the current file
    print(f"\nDo you wish to {red_start}remove the retrieved file?{red_end} [y/N]")
    choice = input().lower()
    if choice == 'y':
        os.remove(retrieved_file_path)
        print("Retrieved file removed.")
        all_files.remove(os.path.basename(retrieved_file_path))  # Remove the file from the list

        # If there are more files, ask to remove them. If not, remove the directory.
        if len(all_files) > 0:
            print(f"\nThere are {len(all_files)} additional file(s) in the temporary directory.")
            print("Do you want to remove all these files? [y/N]")
            all_files_choice = input().lower()
            if all_files_choice == 'y':
                shutil.rmtree(directory, ignore_errors=True)
                print("All files in the temporary directory removed.")
            else:
                print("Additional files retained.")
        else:
            shutil.rmtree(directory, ignore_errors=True)  # Remove the directory as it's now empty
            print("Temporary directory removed.")
    else:
        print("No files removed.")


def download_file(url, bulk_operation=False, rate_limit=0.5, filetype=None, verbosity=0):
    global current_rate_limit  # Refer to the global variable
    global files_downloaded
    directory = "./temp_metadata"
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_name = os.path.basename(url.split('?')[0])
    if not file_name or '.' not in file_name:  # Assign default filename if invalid
        file_name = f"missing-name{filetype if filetype else '.bin'}"
        counter = 1
        while os.path.exists(os.path.join(directory, file_name)):
            file_name = f"missing-name{counter}{filetype if filetype else '.bin'}"
            counter += 1

    save_path = os.path.join(directory, file_name)

    try:
        response = requests.get(url)
        time.sleep(current_rate_limit)  # Use the current rate limit for delay
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            if not bulk_operation:
                print(f"\nFile saved to {save_path}\n")
            files_downloaded = True
            return save_path
        else:
            if not bulk_operation:
                print(f"\nFailed to download file. Status code: {response.status_code}")
            if verbosity > 0:
                print("  [-] File not retrieved successfully")
            return None
    except requests.exceptions.ConnectionError:
        print(f"\n{red_start}{italics_start}Server has refused the current request due to rate limiting.{italics_end}{red_end}")
        print("Consider using a higher rate-limit value to prevent this issue.")
        print(f"Current rate limit is set to {blue_start}{current_rate_limit} seconds{blue_end}.")
        print("Choose an option:")
        print("1: Wait for 60 seconds and continue with a new rate limit")
        print("2: Break and tally results")
        choice = input("Enter your choice (1 or 2): ").strip()

        if choice == '1':
            new_rate_limit = input("Enter new rate limit (in seconds; default new rate: 2): ").strip()
            try:
                new_rate_limit = float(new_rate_limit)
                current_rate_limit = new_rate_limit  # Update the global rate limit
            except ValueError:
                print("Invalid input. Defaulting to 2 seconds.")
                current_rate_limit = 2.0  # Default to 2 seconds if invalid input
                
            print(f"{italics_start}{blue_start}Waiting for 60 seconds{blue_end}{italics_end} before continuing with a rate limit of {blue_start}{current_rate_limit} seconds{blue_end}...")
            time.sleep(60)
            return download_file(url, bulk_operation, filetype, verbosity)
        elif choice == '2':
            # Logic to break and tally results
            return None


def extract_metadata(file_path):
    if not exiftool_exists():
        return {}  # ExifTool not found, return empty metadata

    try:
        result = subprocess.run(['exiftool', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            if "File is empty" not in result.stderr:
                print(f"{red_start}ExifTool error for {file_path}: {result.stderr.strip()}{red_end}")
            return {}
        return process_metadata(result.stdout)
    except Exception as e:
        print(f"Error running ExifTool: {e}")
        return {}


def test_files_for_metadata(matching_urls, filetype, domain, rate_limit, portion, verbosity):
    global tested_extensions
    # Initialize percentage to a default value
    percentage = 0.0
    user_broke_loop = False
    
    exiftool_available = exiftool_exists()
    if not exiftool_available:
        print(f"{blue_start}ExifTool was not found. More detailed metadata may be available by using this tool.{blue_end}")
        print(f"{italics_start}{blue_start} Install ExifTool on Linux: sudo apt-get install exiftool{blue_end}{italics_end}")
        print(f"{italics_start}{blue_start} Install ExifTool on Windows: Download from https://exiftool.org/{blue_end}{italics_end}\n")

    if portion:
        # Determine the number of files to test based on the portion logic
        num_files_to_test = determine_portion(matching_urls)
    else:
        num_files_to_test = len(matching_urls)
        
    if not portion:  # If testing all files (Option 5)
        tested_extensions.add(filetype)

    tested_files_metadata = []
    relevant_metadata_found = False
    for i, (url, archive_number, _) in enumerate(matching_urls):
        if i >= num_files_to_test:
            break
        relative_url = url.replace(f"https://{domain}", "").replace(f"http://{domain}", "").replace(f"https://www.{domain}", "").replace(f"http://www.{domain}", "")
        print(f"Retrieving: {relative_url}")
        file_path = download_file(f"https://web.archive.org/web/{archive_number}/{url}", bulk_operation=True, rate_limit=rate_limit)
        
        if file_path is None:  # assuming None is returned to indicate breaking the loop
            user_broke_loop = True  # Set the flag if user breaks the loop
#            total_files_tested = i  # Update to the actual number of files tested
            break  # exit the loop
        if file_path:
            metadata = extract_metadata(file_path)
            metadata_match_found = any(key in metadata for key in highlight_keys if key != "File Name" and key != "Error")
            if metadata_match_found:
                relevant_metadata_found = True
                tested_files_metadata.append((url, metadata))
                if verbosity >= 1:
                    print(f"{green_start}[+]{green_end} Metadata found")
            elif verbosity >= 1:
                print(f"{red_start}[-]{red_end} No metadata found")
            os.remove(file_path)
            
    # Calculate the percentage if files were tested
    total_files_tested = i + 1  # Adjust to count the number of files actually tested
    files_with_metadata = len(tested_files_metadata)
    percentage = (files_with_metadata / total_files_tested) * 100 if total_files_tested > 0 else 0

    # Adjusting message formatting and colors based on the count
    found_color = green_start if files_with_metadata > 0 else red_start
    tested_color = blue_start if user_broke_loop else found_color
    percent_color = green_start if files_with_metadata > 0 else red_start

    if user_broke_loop:
        print(f"\n{found_color}{files_with_metadata}{green_end}/{tested_color}{total_files_tested}{green_end} tested files ({percent_color}{percentage:.2f}%{green_end}) of the {blue_start}{len(matching_urls)}{green_end} total contained targeted metadata.")
    else:
        print(f"\n{found_color}{files_with_metadata}/{len(matching_urls)} ({percentage:.2f}%){green_end} files contained targeted metadata.")


def determine_portion(matching_urls):
    # logic for determining the portion of files to test
    # Example: 20% of total, but not less than 50 and not more than 200
    # Add user prompts if needed for warning and adjustments
    pass


def save_metadata_results(tested_files_metadata, filetype, domain):
    filename = f"metadata_results_{filetype}_{domain}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Original URL', 'Metadata'])
        for url, metadata in tested_files_metadata:
            csvwriter.writerow([url, json.dumps(metadata)])

    print(f"\nMetadata results saved to {filename}")


def exiftool_exists():
    return shutil.which("exiftool") is not None


def print_basic_metadata(file_path, show_instructions=True):
    try:
        file_stats = os.stat(file_path)
        file_name = os.path.basename(file_path)
        metadata = {
            "File Name": file_name,
            "File Size": f"{file_stats.st_size} bytes",
            "Last Modified": time.ctime(file_stats.st_mtime),
            "Created": time.ctime(file_stats.st_ctime)
        }
        return metadata
    except Exception as e:
        print(f"Error extracting basic metadata: {e}")
        return {}


def process_metadata(metadata):
    lines = metadata.split('\n')
    metadata_dict = {}

    for line in lines:
        parts = line.split(': ', 1)
        if len(parts) == 2:
            key, value = parts
            key = key.strip()
            if key in highlight_keys:
                value = f"{green_start}{value.strip()}{green_end}"
            elif key == 'Directory':
                continue
            metadata_dict[key] = value
    return metadata_dict


def print_urls(matching_urls):
    for url in matching_urls:
        print(url)


def manage_traffic(rate_limit):
    time.sleep(rate_limit)
    

def remove_downloaded_files():
    print(f"\nDo you wish to {red_start}remove the retrieved files?{red_end} [y/N]")
    choice = input().lower()
    if choice == 'y':
        shutil.rmtree("./temp_metadata", ignore_errors=True)
        print("Retrieved files and directory removed.")


if __name__ == "__main__":
    main()


