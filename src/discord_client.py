import requests
import config
import utils
import notion_client


SUPPRESS_SEND_CODE = 4096

def send_task_message(title: str, page_id: str, assignees: list, deadline: str):
    message_content = _build_discord_message(title, page_id, assignees, deadline, True)
    _send_message_to_discord(message_content)
    return message_content

def send_conference_message(title: str, page_id: str, assignees: list, start_time: str):
    message_content = _build_discord_message(title, page_id, assignees, start_time, False)
    _send_message_to_discord(message_content)
    return message_content

def _build_discord_message(title: str, page_id: str, assignees: list, datetime: str, is_task: bool):
    user_map = utils.load_user_map()
    if user_map == dict():
        raise Exception("NullException: there are not discord user maps")

    page_url = notion_client.build_notion_url(page_id)

    assignee_mentions = []
    for name in assignees:
        discord_id = user_map.get(name)
        if discord_id:
            assignee_mentions.append(f"<@{discord_id}>")
        else:
            print(f"NullException: Not found discord id: [{name}]")

    assignee_mention_str = "\n".join([f"\\- {assignee}" for assignee in assignee_mentions])

    datetime_str = utils.convert_to_datetime_obj(datetime)

    if is_task:
        return config.build_task_message(title, assignee_mention_str.rstrip("\n"), page_url, datetime_str)
    else:
        return config.build_conference_message(title, assignee_mention_str.rstrip("\n"), page_url, datetime_str)

def _send_message_to_discord(message_content: str, should_silent : bool = True):
    message = {
        "content": message_content.strip(),
        "flags": SUPPRESS_SEND_CODE if should_silent else 0
    }

    requests.post(config.DISCORD_WEBHOOK_URL, json=message)
