#!/usr/bin/env python3

import argparse
import sqlite3
import os
import re
import sys
import subprocess

from contextlib import closing

# Pfad zur darktable-Datenbank
DB_PATH = os.path.expanduser("~/.config/darktable/library.db")

def find_xmp_files(directory):
    result = {}
    home_dir = os.path.expanduser("~")
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.xmp') and '.sync-conflict-' not in file:
                full_path = os.path.join(root, file)
                base_name = re.sub(r'(_\d+)?\.ARW\.xmp$', '.ARW', full_path)
                
                if base_name.startswith(home_dir):
                    base_name = os.path.relpath(base_name, home_dir)
                
                result[base_name] = result.get(base_name, 0) + 1
    
    return [f"{base};{count}" for base, count in result.items() if count > 0]

def get_file_info(line):
    full_path, expected_versions = line.strip().split(';')
    return {
        'full_path': full_path,
        'dir_path': os.path.dirname(full_path),
        'filename': os.path.basename(full_path),
        'expected_versions': int(expected_versions)
    }

def get_actual_versions(cursor, filename, dir_path):
    query = """
    SELECT COUNT(*)
    FROM images i
    JOIN film_rolls fr ON i.film_id = fr.id
    WHERE i.filename = ?
    AND fr.folder LIKE ?
    """
    cursor.execute(query, (filename, '%' + dir_path))
    return cursor.fetchone()[0]

def check_versions(file_list, db_path):
    output_list = []

    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()

        for line in file_list:
            file_info = get_file_info(line)
            actual_versions = get_actual_versions(cursor, file_info['filename'], file_info['dir_path'])

            if actual_versions < file_info['expected_versions']:
                print(f"{file_info['full_path']} {actual_versions} {file_info['expected_versions']}")
                output_list.append(file_info['full_path'])

    return output_list

import subprocess

def execute_command(result):
    # Replace 'your_command_here' with the actual command you want to execute
    command = ['darktable'] + result
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Darktable-Utility: Import additional image duplicates

Read a list of image names from stdin or a text file,
check the darktable library if the duplicates are already present.
If not, call darktable with the additional duplicates.
""",
    epilog='\u00A9 2024 Markus Spring <me@markus-spring.de> https://markus-spring.info')
    
    parser.add_argument("-d", "--directory", action='append', help="Directory to start the search from (can be used multiple times)")
    parser.add_argument('-v', '--verbose', action='store_true', help='Print results and execute command')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Only print result, don\'t execute command')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='Input file (default: stdin)')

    args = parser.parse_args()

    file_list = []
    if args.directory:
        for directory in args.directory:
            file_list.extend(find_xmp_files(directory))
    else:
        file_list = args.file.readlines()
    result = check_versions(file_list, DB_PATH)

    if args.verbose or args.dry_run:
        print(' '.join(result))

    if not args.dry_run:
        execute_command(result)
