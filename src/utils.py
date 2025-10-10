import os
from datetime import datetime
import json
import config

def load_notified_task_state() -> dict:
    if os.path.exists(config.STATE_FILE):
        with open(config.STATE_FILE, config.FILE_MODE_READ, encoding=config.ENCODER) as f:
            return json.load(f)
    return dict()

def save_notified_task_state(page_id_titles: dict) -> None:
    with open(config.STATE_FILE, config.FILE_MODE_WRITE, encoding=config.ENCODER) as f:
        json.dump(page_id_titles, f, indent=2, ensure_ascii=False)

def load_user_map() -> dict:
    if os.path.exists(config.USER_MAP_FILE):
        with open(config.USER_MAP_FILE, config.FILE_MODE_READ, encoding=config.ENCODER) as f:
            return json.load(f)
    return dict()

def convert_to_datetime_obj(time_string: str) -> datetime:
    # 1. まずISO形式（時間やタイムゾーンを含む）での変換を試す
    try:
        # fromisoformatは '2025-10-08' のような日付だけだとエラーになる
        dt_object = datetime.fromisoformat(time_string)
        return dt_object
    except ValueError:
        # 2. ISO形式でエラーになったら、日付だけの形式 ('%Y-%m-%d') での変換を試す
        try:
            dt_object = datetime.strptime(time_string, '%Y-%m-%d')
            return dt_object
        except ValueError:
            # 3. どちらの形式でもなければ、エラーメッセージを出してNoneを返す
            print(f"エラー: '{time_string}' は対応していない形式です。")
            return None

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
