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
ENV_ADMIN_DISCORD_ID = "DISCORD_ADMIN_ID"

# 環境変数から設定値を取得する
NOTION_TOKEN = os.getenv(ENV_NOTION_TOKEN)
DATABASE_ID = os.getenv(ENV_DATABASE_ID)
DISCORD_WEBHOOK_URL = os.getenv(ENV_DISCORD_WEBHOOK_URL)
DISCORD_ADMIN_ID = os.getenv(ENV_ADMIN_DISCORD_ID)

# HTTPヘッダー関連の定数
HEADER_AUTHORIZATION = "Authorization"
HEADER_BEARER_PREFIX = "Bearer "
HEADER_NOTION_VERSION = "Notion-Version"
HEADER_CONTENT_TYPE = "Content-Type"
CONTENT_TYPE_JSON = "application/json"

# NotionAPI: API関連の定数
NOTION_API_BASE_URL = "https://api.notion.com/v1/databases/"
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

def send_discord_notification(title, page_id, assignees):
    mentions = []
    unknowns = []
    user_map = load_user_map()
    page_url = build_notion_url(page_id)

    for name in assignees:
        discord_id = user_map.get(name)
        if discord_id:
            mentions.append(f"<@{discord_id}>")
        else:
            unknowns.append(name)

    mention_str = " ".join(mentions) if mentions else "（メンション対象なし）"
    unknown_mention_str = " ".join(unknowns) if unknowns else ""
    unknown_note = f"\n-# DiscordIDが未登録です: {', '.join(unknowns)}" if unknowns else ""

    message = {
        "content": f"# {title}\n担当者:{mention_str}{unknown_mention_str}\nリンク: {page_url}{unknown_note}",
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
            
		# 非通知フラグ取得
        suppress_notify = page[KEY_PRPPERTIES].get(PROP_SUPRESS_NOTIFY_NAME, {}).get(KEY_CHECKBOX, False)
        # 強制通知フラグ取得
        force_notify = page[KEY_PRPPERTIES].get(PROP_FORCE_NOTIFY_NAME, {}).get(KEY_CHECKBOX, False)

        # 新しい状態を保存（ステータスIDのみ保存）
        new_state[page_id] = status_id

        # 差分検知（ステータスIDで比較）
        if page_id not in prev_state or prev_state[page_id] != status_id:
            if not suppress_notify and status_id == STATUS_ID_INPROGRESS or force_notify:
                send_discord_notification(title, page_id, assignee_names)

    save_state(new_state)

if __name__ == "__main__":
    main()
