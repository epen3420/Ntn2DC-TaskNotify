import os
from datetime import datetime
import json
import shutil
import config

FILE_MODE_READ = "r"
FILE_MODE_WRITE = "w"
ENCODER = "utf-8"

def load_notified_task_state() -> dict:
    if os.path.exists(config.NOTIFIED_STATE_PATH):
        with open(config.NOTIFIED_STATE_PATH, FILE_MODE_READ, encoding=ENCODER) as f:
            return json.load(f)
    return dict()

def save_notified_task_state(page_id_titles: dict) -> None:
    if not os.path.exists(config.LOG_PATH):
        os.mkdir(config.LOG_PATH)

    with open(config.NOTIFIED_STATE_PATH, FILE_MODE_WRITE, encoding=ENCODER) as f:
        json.dump(page_id_titles, f, indent=2, ensure_ascii=False)

def load_user_map() -> dict:
    if os.path.exists(config.USER_MAP_PATH):
        with open(config.USER_MAP_PATH, FILE_MODE_READ, encoding=ENCODER) as f:
            return json.load(f)
    return dict()

def convert_to_datetime_obj(time_str: str) -> str:
    WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]

    dt_obj = datetime.fromisoformat(time_str)
    week_index = dt_obj.weekday()
    week_day_str = WEEKDAYS[week_index]

    if dt_obj.hour == 0 and dt_obj.second == 0:
        return dt_obj.strftime(f'%Y/%m/%d ({week_day_str})')
    else:
        return dt_obj.strftime(f'%Y/%m/%d ({week_day_str}) %H:%M')

def ask_continue(message: str) -> bool:
    yes_str = ["Yes", "yes", "Y", "y"]
    no_str = ["No", "no", "N", "n"]
    stop_str = ["Stop", "stop", "S", "s", "exit", "e"]

    print(message)
    print()
    user_input = input("Do you want to continue? (y/n/exit) ")

    if user_input in yes_str:
        return True
    elif user_input in no_str:
        return False
    elif user_input in stop_str:
        exit(1)
    else:
        return ask_continue(message)

    shutil.rmtree(config.LOG_PATH)
    os.mkdir(config.LOG_PATH)

def ask_yes_no(question: str) -> bool:
    yes_str = ["yes", "y"]
    no_str = ["no", "n"]

    while True:
        choice = input(f"{question} (y/n): ").lower()
        if choice in yes_str:
            return True
        elif choice in no_str:
            return False
        else:
            print("Please enter 'y' or 'n'.")

if __name__ == '__main__':
    yes_str = ["y", "Y", "yes", "Yes"]
    no_str = ["n", "N", "no", "No"]
    is_continue = input("Do you want to remove log folder? (y/n) ")
    if is_continue not in yes_str + no_str:
        print("Invalid input")
        exit()

    if is_continue in no_str:
        exit()

    remove_log()
    print("removed log folder")
