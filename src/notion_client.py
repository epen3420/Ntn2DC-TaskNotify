import requests
import config

HEADERS = {
    config.HEADER_AUTHORIZATION: f"{config.HEADER_BEARER_PREFIX}{config.NOTION_TOKEN}",
    config.HEADER_NOTION_VERSION: config.NOTION_API_VERSION,
    config.HEADER_CONTENT_TYPE: config.CONTENT_TYPE_JSON
}

def fetch_db(database_id: str, payload: dict = dict()) -> dict:
    url = f"{config.NOTION_API_BASE_URL}{database_id}{config.QUERY_ENDPOINT}"
    res = requests.post(url, headers=HEADERS, json=payload)
    res.raise_for_status()
    return res.json()

def fetch_db_only_status_progress() -> dict:
    payload = {
        "filter": {
            "and": [
                {
                    "property": config.PROP_STATUS_NAME,
                    config.KEY_STATUS: {
                        "equals": config.STATUS_NAME_PROGRESS,
                    }
                },
                {
                    "property": config.PROP_NOTIFIED_NAME,
                    config.KEY_CHECKBOX: {
                        "equals": False,
                    }
                }
            ]
        }
    }

    return fetch_db(config.TASK_DATABASE_ID, payload)

def get_page_from_id(page_id: str) -> dict:
    url = f"{config.NOTION_PAGES_API_URL}{page_id}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def get_title(record: dict) -> str:
    title_prop = record[config.KEY_PROPERTIES].get(config.PROP_TITLE_NAME)
    if not title_prop or not title_prop[config.KEY_TITLE]:
        return None
    return title_prop[config.KEY_TITLE][0][config.KEY_PLAIN_TEXT]

def get_checkbox_value(record: dict, prop_name: str) -> bool:
    return record[config.KEY_PROPERTIES].get(prop_name, {}).get(config.KEY_CHECKBOX, False)

def get_select_value(record: dict, prop_name: str) -> str:
    select_data = record[config.KEY_PROPERTIES].get(prop_name, {}).get(config.KEY_SELECT)
    if select_data:
        return select_data.get("name")
    return None

def get_relation_records(record: dict, prop_name: str) -> list:
    relation_prop = record[config.KEY_PROPERTIES][prop_name]["relation"]
    if not relation_prop:
        return []
    return relation_prop

def get_deadline(record: dict) -> str:
    return record[config.KEY_PROPERTIES].get(config.PROP_DEADLINE).get("date").get("start")

def get_stateDate(record: dict) -> str:
    return record[config.KEY_PROPERTIES].get(config.PROP_START_DATE).get("date").get("start")

def retrieve_member_dict() -> dict:
    member_datas = fetch_db(config.MEMBER_DATABASE_ID)
    member_dict = dict()
    for member in member_datas[config.KEY_RESULTS]:
        member_dict.setdefault(member[config.KEY_ID], get_title(member))

    return member_dict

def update_page_checkbox(page_id: str, prop_name: str, value: bool) -> dict:
    url = f"{config.NOTION_PAGES_API_URL}{page_id}"
    payload = {
        config.KEY_PROPERTIES: {
            prop_name: {
                config.KEY_CHECKBOX: value
            }
        }
    }
    res = requests.patch(url, headers=HEADERS, json=payload)
    res.raise_for_status()
    return res.json()

def build_notion_url(page_id: str) -> str:
    clean_id = page_id.replace("-", "")
    return f"https://www.notion.so/{clean_id}"

if __name__ == '__main__':
    import json
    data = fetch_db_only_status_progress()
    print(json.dumps(data[config.KEY_RESULTS], indent=2,ensure_ascii=False))
