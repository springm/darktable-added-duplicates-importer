#!/usr/bin/env python3

import argparse
import sqlite3
import os
import sys
import subprocess

# Pfad zur darktable-Datenbank
DB_PATH = os.path.expanduser("~/.config/darktable/library.db")

def check_versions(file_list):
    output_list = []

    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for line in file_list:
        full_path, expected_versions = line.strip().split(';')
        dir_path = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        expected_versions = int(expected_versions)

        # SQL-Abfrage
        query = """
        SELECT COUNT(*)
        FROM images i
        JOIN film_rolls fr ON i.film_id = fr.id
        WHERE i.filename = ?
        AND fr.folder LIKE ?
        """
        
        cursor.execute(query, (filename,  '%' + dir_path))
        actual_versions = cursor.fetchone()[0]

        if actual_versions < expected_versions:
            print(' '.join([full_path,str(actual_versions),str(expected_versions)]))
            output_list.append(full_path)

    conn.close()
    return output_list

def execute_command(result):
    command = ["darktable"] + result
    subprocess.run(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Darktable-Utility: Import additional image duplicates

Read a list of image names from stdin or a text file,
check the darktable library if the duplicates are already present.
If not, call darktable with the additional duplicates.
""",
    epilog='\u00A9 2024 Markus Spring <me@markus-spring.de> https://markus-spring.info')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print results and execute command')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Only print result, don\'t execute command')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='Input file (default: stdin)')

    args = parser.parse_args()

    file_list = args.file.readlines()
    result = check_versions(file_list)

    if args.verbose or args.dry_run:
        print(' '.join(result))

    if not args.dry_run:
        execute_command(result)
        
# if __name__ == "__main__":
#     # Lesen der Eingabe von einer Datei oder stdin
#     if len(sys.argv) > 1:
#         with open(sys.argv[1], 'r') as file:
#             file_list = file.readlines()
#     else:
#         file_list = sys.stdin.readlines()

#     result = check_versions(file_list)
    
#     # Ausgabe der Leerzeichen-separierten Liste
#     print(' '.join(result))
    
#     # # # # Wenn die Liste nicht leer ist, darktable mit den Dateien als Argumente aufrufen
#     # if result:
#     #     command = ["darktable"] + result
#     #     subprocess.run(command)
