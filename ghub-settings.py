#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of this program was made with code from:
# https://pynative.com/python-sqlite-blob-insert-and-retrieve-digital-data/

import datetime
import json
import os
import sys
import shutil
from typing import (Tuple)
import sqlite3

DEFAULT_FOLDER_LG_GHUB_SETTINGS = ""
DEFAULT_PATH_SETTINGS_DB = ""
DEFAULT_FILENAME_SETTINGS_DB = 'settings.db'
DEFAULT_FILENAME_SETTINGS_JSON = 'EDIT_ME.json'


def init_dirs() -> bool:
    global DEFAULT_FOLDER_LG_GHUB_SETTINGS, DEFAULT_PATH_SETTINGS_DB

    if sys.platform.startswith('win'):  # Windows
        DEFAULT_FOLDER_LG_GHUB_SETTINGS = os.path.expandvars('%LOCALAPPDATA%/LGHUB/')  # Must end with /
    elif sys.platform.startswith('darwin'):  # MacOS
        DEFAULT_FOLDER_LG_GHUB_SETTINGS = os.path.expandvars(
            '$HOME/Library/Application Support/lghub/')  # Must end with /
    else:
        return False
    DEFAULT_PATH_SETTINGS_DB = DEFAULT_FOLDER_LG_GHUB_SETTINGS + DEFAULT_FILENAME_SETTINGS_DB
    return True


def make_backup(file_path):
    backup_file_path = file_path + datetime.datetime.now().strftime('.%Y-%m-%d_%H-%M-%S')
    try:
        shutil.copy(file_path, backup_file_path)
        print(f"A backup of the settings.db file has been made to:\n{backup_file_path}")
    except Exception as error:
        print(
            f"ERROR: Failed to make a backup of the settings.db file! From:\n{file_path}\nTo:\n{backup_file_path}\n\nSince this is a critical failure, the program will quit.\n\nError:{error}")
        exit(42)


def get_latest_id(file_path) -> Tuple[int, str]:
    latest_id = -1
    error_message = ""
    try:
        with sqlite3.connect(file_path) as sqlite_connection:
            cursor = sqlite_connection.cursor()

            sql_get_latest_id = 'select MAX(_id) from DATA'
            cursor.execute(sql_get_latest_id)
            record = cursor.fetchall()
            latest_id = record[0][0]
    except sqlite3.Error as error:
        error_message = f"ERROR: Failed to read latest id from the table inside {file_path}\nThis program will quit.\n\nError: {error}"
    return latest_id, error_message


def write_json_to_file(blob, file_path) -> Tuple[bool, str]:
    try:
        with open(file_path, 'wb') as file:
            file.write(blob)
        print("Stored blob data into: ", file_path, "\n")
    except Exception as error:
        error_message = """
ERROR: Failed to write the following file:
{file_path}
Error:
{exception_message}
        """
        print(error_message.format(file_path=file_path, exception_message=error))


def sort_settings(settings: str) -> str:
    j = json.loads(settings)
    # sorted_names = [c["name"] for c in j["cards"]["cards"]]
    j["cards"]["cards"].sort(
        key=lambda card: f'{card.get("name")}{card.get("id")}')  # sort cards in place by name-then-id
    return json.dumps(j, indent=2).encode('utf-8')


def add_brightness(settings: str) -> str:
    j = json.loads(settings)

    #abc

    return json.dumps(j, indent=2).encode('utf-8')




def get_settings_json(data_id, file_path) -> str:
    sqlite_connection = 0
    settings: str = ""
    try:
        with sqlite3.connect(file_path) as sqlite_connection:
            cursor = sqlite_connection.cursor()
            sql_fetch_blob_query = "SELECT _id, FILE from DATA where _id = ?"
            cursor.execute(sql_fetch_blob_query, (data_id,))
            record = cursor.fetchall()
            for row in record:
                print("Id = ", row[0])
                settings_data = row[1]
                settings = settings_data
            cursor.close()
    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    return settings


def write_settings_json(settings: str, json_file_path):
    write_json_to_file(settings, json_file_path)


def convert_to_binary_data(file_path):
    try:
        with open(file_path, 'rb') as file:
            blob_data = file.read()
        return blob_data
    except Exception as error:
        error_message = """
ERROR: Failed to read the following file:
{file_path}
This program will quit.
Error:
{exception_message}
        """
        print(error_message.format(file_path=file_path, exception_message=error))
        exit(24)


def insert_blob(data_id, settings: str, db_file_path):
    sqlite_connection = 0
    try:
        with sqlite3.connect(db_file_path) as sqlite_connection:
            cursor = sqlite_connection.cursor()
            replace_query = "Replace INTO DATA (_id, _date_created, FILE) VALUES (?, ?, ?)"
            blob = settings # convert_to_binary_data(updated_settings_file_path)
            # Convert data into tuple format
            data_tuple = (data_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), blob)
            cursor.execute(replace_query, data_tuple)
            sqlite_connection.commit()
            cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)


def main() -> int:
    if not init_dirs():
        print(f"ERROR: Unsupported platform:  {sys.platform}")
        return 1

    if not os.path.exists(DEFAULT_PATH_SETTINGS_DB):
        print(f"ERROR: The file settings.db was not found:\n{DEFAULT_PATH_SETTINGS_DB}\n\nQuitting...")
        return 2

    '''
    program_introduction_notification = """
This program is intended to extract and replace the settings.json inside the settings.db used by Logitech G Hub.

Press Enter to continue.
    """
    print(program_introduction_notification)
    if sys.version_info[0] < 3:
        raw_input()
    else:
        input()
    print("This program will extract the settings from the database...")
    '''
    latest_id, error_message = get_latest_id(DEFAULT_PATH_SETTINGS_DB)
    if latest_id <= 0:
        print(error_message)
        return 3

    settings = get_settings_json(latest_id, DEFAULT_PATH_SETTINGS_DB)
    write_settings_json(settings, DEFAULT_FOLDER_LG_GHUB_SETTINGS + DEFAULT_FILENAME_SETTINGS_JSON)
    settings = sort_settings(settings)
    settings = add_brightness(settings)
    write_settings_json(settings, DEFAULT_FOLDER_LG_GHUB_SETTINGS + DEFAULT_FILENAME_SETTINGS_JSON + '2')

    print("IMPORTANT: PLEASE CLOSE LG G HUB NOW")
    '''
    print("The extracted file will be open after you press Enter.")
    print("Please edit it and don't forget to save the file then close the file (and the program that opened with)")
    '''
    if sys.version_info[0] < 3:
        raw_input()
    else:
        input()
    '''
    if sys.platform.startswith('win'): # Windows
        os.system(file_written)
    elif sys.platform.startswith('darwin'): # MacOS
        os.system('open "' + file_written + '"')
    else:
        print(file_written)
    '''
    make_backup(DEFAULT_PATH_SETTINGS_DB)
    insert_blob(latest_id, settings, DEFAULT_PATH_SETTINGS_DB)
    print("The settings have been updated.")
    return 0


if __name__ == '__main__':
    exit(main())
