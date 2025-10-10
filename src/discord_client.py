import requests
import config
import utils
import notion_client


WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]

def send_task_message(title: str, page_id: str, assignees: list, deadline: str):
    _send_discord_notification(title, page_id, assignees, deadline, True)

def send_conference_message(title: str, page_id: str, assignees: list, start_time: str):
    _send_discord_notification(title, page_id, assignees, start_time, False)

def _send_discord_notification(title: str, page_id: str, assignees: list, datetime: str, is_task: bool):
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

    assignee_mention_str = ""
    for assignee in assignee_mentions:
        assignee_mention_str = assignee_mention_str + f"\\- {assignee}\n"

    datetime_obj = utils.convert_to_datetime_obj(datetime)
    datetime_unix = int(datetime_obj.timestamp())
    weekday = WEEKDAYS[datetime_obj.weekday()]

    message_content = ""
    if is_task:
        deadline_str = f"<t:{datetime_unix}:d> ({weekday})"
        message_content = config.build_task_message(title, assignee_mention_str.rstrip("\n"), page_url, deadline_str)
    else:
        start_time_str = f"<t:{datetime_unix}:d> ({weekday}) <t:{datetime_unix}:t>"
        message_content = config.build_conference_message(title, assignee_mention_str.rstrip("\n"), page_url, start_time_str)

    _send_message_to_discord(message_content)

def _send_message_to_discord(message_content: str):
    message = {
        "content": message_content.strip(),
        "flags": 4096  # Suppress notifications
    }

    requests.post(config.DISCORD_WEBHOOK_URL, json=message)
