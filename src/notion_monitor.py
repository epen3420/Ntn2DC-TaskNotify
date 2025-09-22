import os
import json
import requests
from dotenv import load_dotenv

# 環境変数読み込み (.env ファイル対応)
load_dotenv()

# 環境変数名
ENV_NOTION_TOKEN = "NOTION_TOKEN"
ENV_DATABASE_ID = "NOTION_DATABASE_ID"
ENV_DISCORD_WEBHOOK_URL = "DISCORD_WEBHOOK_URL"

# 環境変数から設定値を取得する
NOTION_TOKEN = os.getenv(ENV_NOTION_TOKEN)
DATABASE_ID = os.getenv(ENV_DATABASE_ID)
DISCORD_WEBHOOK_URL = os.getenv(ENV_DISCORD_WEBHOOK_URL)

# HTTPヘッダー関連の定数
HEADER_AUTHORIZATION = "Authorization"
HEADER_BEARER_PREFIX = "Bearer "
HEADER_NOTION_VERSION = "Notion-Version"
HEADER_CONTENT_TYPE = "Content-Type"
CONTENT_TYPE_JSON = "application/json"

# NotionAPI: API関連の定数
NOTION_API_BASE_URL = "https://api.notion.com/v1/databases/"
NOTION_PAGES_API_URL = "https://api.notion.com/v1/pages/"
QUERY_ENDPOINT = "/query"
NOTION_API_VERSION = "2022-06-28"

# NotionAPI: JSONキー関連の定数
KEY_ID = "id"
KEY_STATUS = "status"
KEY_NAME = "name"
KEY_PLAIN_TEXT = "plain_text"
KEY_RESULTS = "results"
KEY_PRPPERTIES = "properties"
KET_SELECT = "select"
KEY_TITLE = "title"
KEY_CHECKBOX = "checkbox"

# NotionAPI: 型"ステータス"用の定数
STATUS_ID_KEY = "status_id"
STATUS_NAME_KEY = "status_name"

# メテコアDB: プロパティ名
PROP_TITLE_NAME = "名前"
PROP_STATUS_NAME = "ステータス"
PROP_ASIGNEE_NAME = "担当者"
PROP_CHECKER_NAME = "確認者"
PROP_SUPRESS_NOTIFY_NAME = "非通知"
PROP_FORCE_NOTIFY_NAME = "強制通知"

# メテコアDB: ステータスID定数
STATUS_ID_INPROGRESS = "557498a8-4b29-41fc-b328-54107d7acc4f"

# python
FILE_MODE_READ = "r"
FILE_MODE_WRITE = "w"
ENCODER = "utf-8"

# ファイル名
STATE_FILE = "last_state.json"
USER_MAP_FILE = "user_map.json"

HEADERS = {
    HEADER_AUTHORIZATION: f"{HEADER_BEARER_PREFIX}{NOTION_TOKEN}",
    HEADER_NOTION_VERSION: NOTION_API_VERSION,
    HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON
}

def fetch_database():
    url = f"{NOTION_API_BASE_URL}{DATABASE_ID}{QUERY_ENDPOINT}"
    res = requests.post(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def load_previous_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, FILE_MODE_READ, encoding=ENCODER) as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, FILE_MODE_WRITE, encoding=ENCODER) as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        
def load_user_map():
    if os.path.exists(USER_MAP_FILE):
        with open(USER_MAP_FILE, FILE_MODE_READ, encoding=ENCODER) as f:
            return json.load(f)
    return {}

def build_notion_url(page_id: str) -> str:
    # ハイフン除去したIDでNotionページURLを作成
    clean_id = page_id.replace("-", "")
    return f"https://www.notion.so/{clean_id}"

def update_page_property(page_id: str, property_name: str, property_value):
    """
    指定されたページIDのプロパティを更新する
    
    Args:
        page_id (str): 更新対象のページID
        property_name (str): 更新するプロパティ名
        property_value: 設定する値（プロパティタイプに応じて適切な形式で指定）
                       - text/title: str
                       - select: str (選択肢の名前)
                       - multi_select: list[str] (選択肢の名前のリスト)
                       - checkbox: bool
                       - number: int/float
                       - date: str (ISO形式: "2023-12-25" または "2023-12-25T10:30:00.000Z")
    
    Returns:
        dict: 更新後のページ情報
        
    Raises:
        requests.HTTPError: API呼び出しでエラーが発生した場合
    """
    url = f"{NOTION_PAGES_API_URL}{page_id}"
    
    # プロパティの値を適切な形式に変換
    property_data = _format_property_value(property_name, property_value)
    
    payload = {
        "properties": {
            property_name: property_data
        }
    }
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def _format_property_value(property_name: str, value):
    """
    プロパティの値を適切なNotion API形式に変換する
    
    Args:
        property_name (str): プロパティ名
        value: 設定する値
        
    Returns:
        dict: Notion API形式のプロパティデータ
    """
    # 既知のプロパティタイプに基づいて形式を決定
    if property_name == PROP_TITLE_NAME:  # タイトル
        if isinstance(value, str):
            return {
                "title": [
                    {
                        "text": {
                            "content": value
                        }
                    }
                ]
            }
    elif property_name == PROP_STATUS_NAME:  # ステータス（select）
        if isinstance(value, str):
            return {
                "status": {
                    "name": value
                }
            }
    elif property_name == PROP_ASIGNEE_NAME:  # 担当者（multi_select）
        if isinstance(value, list):
            return {
                "multi_select": [
                    {"name": name} for name in value
                ]
            }
        elif isinstance(value, str):
            return {
                "multi_select": [
                    {"name": value}
                ]
            }
    elif property_name in [PROP_SUPRESS_NOTIFY_NAME, PROP_FORCE_NOTIFY_NAME]:  # チェックボックス
        if isinstance(value, bool):
            return {
                "checkbox": value
            }
    
    # 一般的なプロパティタイプの処理
    if isinstance(value, bool):
        return {"checkbox": value}
    elif isinstance(value, (int, float)):
        return {"number": value}
    elif isinstance(value, str):
        # 文字列の場合、まずはselectとして試行
        return {
            "select": {
                "name": value
            }
        }
    elif isinstance(value, list):
        # リストの場合、multi_selectとして処理
        return {
            "multi_select": [
                {"name": str(item)} for item in value
            ]
        }
    
    raise ValueError(f"Unsupported property type for {property_name}: {type(value)}")

def update_page_multiple_properties(page_id: str, properties: dict):
    """
    指定されたページIDの複数のプロパティを一度に更新する
    
    Args:
        page_id (str): 更新対象のページID
        properties (dict): プロパティ名をキー、値をバリューとする辞書
        
    Returns:
        dict: 更新後のページ情報
        
    Example:
        update_page_multiple_properties(
            page_id="xxx-xxx-xxx",
            properties={
                "名前": "新しいタスク名",
                "ステータス": "進行中",
                "担当者": ["山田太郎", "佐藤花子"],
                "非通知": False
            }
        )
    """
    url = f"{NOTION_PAGES_API_URL}{page_id}"
    
    formatted_properties = {}
    for prop_name, prop_value in properties.items():
        formatted_properties[prop_name] = _format_property_value(prop_name, prop_value)
    
    payload = {
        "properties": formatted_properties
    }
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def send_discord_notification(title, page_id, assignees, checkers):
    asigneeMentions = []
    asigneeUnknowns = []
    checkerMentions = []
    checkerUnknowns = []

    NO_MENTIONS_MSG = "（メンション対象なし）"

    user_map = load_user_map()
    page_url = build_notion_url(page_id)

    for name in assignees:
        discord_id = user_map.get(name)
        if discord_id:
            asigneeMentions.append(f"<@{discord_id}>")
        else:
            asigneeUnknowns.append(name)

    for name in checkers:
        discord_id = user_map.get(name)
        if discord_id:
            checkerMentions.append(f"<@{discord_id}>")
        else:
            checkerUnknowns.append(name)

    asignee_mention_str = " ".join(asigneeMentions)
    asignee_unknown_str = " ".join(asigneeUnknowns)
    checker_mention_str = " ".join(checkerMentions)
    checker_unknown_str = " ".join(checkerUnknowns)
    asignee_unknown_note = f"\n-# 担当者のDiscordIDが未登録です: {', '.join(asigneeUnknowns)}" if asigneeUnknowns else ""
    checker_unknown_note = f"\n-# 確認者のDiscordIDが未登録です: {', '.join(checkerUnknowns)}" if checkerUnknowns else ""

    message = {
        "content": f"# {title}\n担当者:{asignee_mention_str}{asignee_unknown_str}\n確認者:{checker_mention_str}{checker_unknown_str}\nリンク: {page_url}\n{asignee_unknown_note}\n{checker_unknown_note}",
        "flags": 4096 # サイレントメッセージとして送信する
    }
    requests.post(DISCORD_WEBHOOK_URL, json=message)

def main():
    data = fetch_database()
    prev_state = load_previous_state()
    new_state = {}

    for page in data.get(KEY_RESULTS, []):
        page_id = page[KEY_ID]

        # ページタイトル取得
        title_prop = page[KEY_PRPPERTIES].get(PROP_TITLE_NAME)
        if not title_prop or not title_prop[KEY_TITLE]:
            continue
        title = title_prop[KEY_TITLE][0][KEY_PLAIN_TEXT]

        # ステータス取得
        status_prop = page[KEY_PRPPERTIES].get(PROP_STATUS_NAME)
        if status_prop[KEY_STATUS]:
            status_id = status_prop[KEY_STATUS][KEY_ID]
        else:
            status_id = None

        # 担当者（multi_select型）取得
        assignee_names = []
        assignee_prop = page[KEY_PRPPERTIES].get(PROP_ASIGNEE_NAME)

        if assignee_prop and assignee_prop.get("type") == "multi_select":
            assignee_names = [sel["name"] for sel in assignee_prop["multi_select"]]

        # 確認者も同様に取得
        checker_names = []
        checker_prop = page[KEY_PRPPERTIES].get(PROP_CHECKER_NAME)

        if checker_prop and checker_prop.get("type") == "multi_select":
            checker_names = [sel["name"] for sel in checker_prop["multi_select"]]
            
		# 非通知フラグ取得
        suppress_notify = page[KEY_PRPPERTIES].get(PROP_SUPRESS_NOTIFY_NAME, {}).get(KEY_CHECKBOX, False)
        # 強制通知フラグ取得
        force_notify = page[KEY_PRPPERTIES].get(PROP_FORCE_NOTIFY_NAME, {}).get(KEY_CHECKBOX, False)

        # 新しい状態を保存（ステータスIDのみ保存）
        new_state[page_id] = status_id

        # 差分検知（ステータスIDで比較）
        # ステータスが更新されていたら
        if page_id not in prev_state or prev_state[page_id] != status_id or force_notify:
            # 非通知設定されていない、かつ、ステータスが"進行中"、または、強制通知設定されている
            if not suppress_notify and status_id == STATUS_ID_INPROGRESS or force_notify:
                send_discord_notification(title, page_id, assignee_names,checker_names)
                update_page_property(page_id,PROP_FORCE_NOTIFY_NAME,False)

    save_state(new_state)

if __name__ == "__main__":
    main()
