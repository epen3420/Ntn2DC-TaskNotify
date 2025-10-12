import os
from dotenv import load_dotenv

# 環境変数読み込み (.env ファイル対応)
load_dotenv()

# 環境変数
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASK_DATABASE_ID = os.getenv("NOTION_TASK_DATABASE_ID")
MEMBER_DATABASE_ID = os.getenv("NOTION_MEMBER_DATABASE_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# HTTPヘッダー関連
HEADER_AUTHORIZATION = "Authorization"
HEADER_BEARER_PREFIX = "Bearer "
HEADER_NOTION_VERSION = "Notion-Version"
HEADER_CONTENT_TYPE = "Content-Type"
CONTENT_TYPE_JSON = "application/json"

# NotionAPI関連
NOTION_API_BASE_URL = "https://api.notion.com/v1/databases/"
NOTION_PAGES_API_URL = "https://api.notion.com/v1/pages/"
QUERY_ENDPOINT = "/query"
NOTION_API_VERSION = "2022-06-28"

# NotionAPI JSONキー
KEY_ID = "id"
KEY_STATUS = "status"
KEY_NAME = "name"
KEY_PLAIN_TEXT = "plain_text"
KEY_RESULTS = "results"
KEY_PROPERTIES = "properties"
KEY_TITLE = "title"
KEY_CHECKBOX = "checkbox"
KEY_SELECT = "select"
KEY_MULTI_SELECT = "multi_select"
KEY_DATE = "date"

# Notionプロパティ名
PROP_TITLE_NAME = "名前"
PROP_STATUS_NAME = "ステータス"
PROP_ASSIGNEE_NAME = "担当者"
PROP_CHECKER_NAME = "確認者"
PROP_DEADLINE="締切日"
PROP_SUPPRESS_NOTIFY_NAME = "非通知"
PROP_FORCE_NOTIFY_NAME = "強制通知"
PROP_KIND_NAME = "種類"
PROP_TASK_NAME = "タスク"
PROP_CONFERENCE_NAME = "会議"

# Notionステータス名
STATUS_NAME_PROGRESS = "進行中"

# ファイル関連
FILE_MODE_READ = "r"
FILE_MODE_WRITE = "w"
ENCODER = "utf-8"
STATE_FILE = "../log/last_state.json"
USER_MAP_FILE = "../data/user_map.json"

def build_conference_message(title, assignee_mention_str, page_url, start_date):
    return f"""
> # {title}
## 開始日時: {start_date}
## 担当者
{assignee_mention_str}

👇 **詳細はこちら**
{page_url}
"""

def build_task_message(title, assignee_mention_str, page_url, deadline):
    return f"""
> # {title}
## 締切日: {deadline}
## 担当者
{assignee_mention_str}

👇 **詳細はこちら**
{page_url}
"""
