import notion_client as ntn
import discord_client as dc
import utils
import config

def main():
    member_dict = ntn.retrieve_member_dict()
    if member_dict == dict():
        print("NullException: Can't get member list")
        exit()

    data = ntn.fetch_db_only_status_progress()
    notified_task_state = utils.load_notified_task_state()

    task_count = 0
    conference_count = 0
    for record in data.get(config.KEY_RESULTS, []):
        page_id = record.get(config.KEY_ID)

        if not page_id:
            continue

        if page_id in notified_task_state:
            continue

        title = ntn.get_title(record)
        if not title:
            continue

        datetime = ntn.get_deadline(record)

        assignee_records = ntn.get_relation_records(record, config.PROP_ASSIGNEE_NAME)
        assignee_names = [member_dict[assignee_id.get(config.KEY_ID)] for assignee_id in assignee_records]

        is_task = ntn.get_select(record, config.PROP_KIND_NAME)

        if is_task == config.PROP_TASK_NAME:
            dc.send_task_message(title, page_id, assignee_names, datetime)
            task_count = task_count + 1
        elif is_task == config.PROP_CONFERENCE_NAME:
            dc.send_conference_message(title, page_id, assignee_names, datetime)
            conference_count = conference_count + 1
        else:
            continue

        notified_task_state.setdefault(page_id, title)

    utils.save_notified_task_state(notified_task_state)

    if task_count + conference_count <= 0:
        print("未通知のタスクまたは会議はありませんでした")
    else:
        print(f"タスク: {task_count}件\n会議: {conference_count}件\n計: {task_count + conference_count}件のDiscordへの通知が完了しました。")
        print()

        if conference_count > 0:
            print("会議の予定はサーバーにイベント登録してね")


if __name__ == "__main__":
    main()
