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

        if is_task == "タスク":
            dc.send_task_message(title, page_id, assignee_names, datetime)
        elif is_task == "会議":
            dc.send_conference_message(title, page_id, assignee_names, datetime)
        else:
            continue

        notified_task_state.setdefault(page_id, title)


    utils.save_notified_task_state(notified_task_state)

if __name__ == "__main__":
    main()
