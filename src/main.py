import notion_client as ntn
import discord_client as dc
import utils
import config
from datetime import datetime, timezone

def main():
    # メンバーDBから一度だけメンバー情報を取る
    member_dict = ntn.retrieve_member_dict()
    if member_dict == dict():
        print("NullException: Can't get member list")
        exit()

    data = ntn.fetch_db_only_status_progress()
    notified_task_state = utils.load_notified_task_state()

    # ログ表示の集計用
    task_count = 0
    conference_count = 0

    notified_task_progress = []
    for record in data.get(config.KEY_RESULTS, []):
        page_id = record.get(config.KEY_ID)

        if not page_id:
            continue

        title = ntn.get_title(record)
        if not title:
            continue


        start_time_str = ntn.get_stateDate(record)
        deadline_str = ntn.get_deadline(record)
        dt_obj = datetime.fromisoformat(deadline_str)

        # 今より前が期限のタスクがあればコンソールで通知するため
        if datetime.now(timezone.utc) >= dt_obj.replace(tzinfo=timezone.utc):
            notified_task_progress.append([title, page_id])
            continue

        if page_id in notified_task_state:
            continue

        assignee_records = ntn.get_relation_records(record, config.PROP_ASSIGNEE_NAME)
        assignee_names = [member_dict[assignee_id.get(config.KEY_ID)] for assignee_id in assignee_records]

        is_task = ntn.get_select(record, config.PROP_KIND_NAME)

        if is_task == config.PROP_TASK_NAME:
            dc.send_task_message(title, page_id, assignee_names, deadline_str)
            task_count = task_count + 1
        elif is_task == config.PROP_CONFERENCE_NAME:
            dc.send_conference_message(title, page_id, assignee_names, start_time_str)
            conference_count = conference_count + 1
        else:
            continue

        notified_task_state.setdefault(page_id, title)

    utils.save_notified_task_state(notified_task_state)

    if len(notified_task_progress) != 0:
        print(f"締め切りを過ぎて、進行中のタスクが{len(notified_task_progress)}件あります")
        print("以下のタスクが完了している場合は、更新してください")
        for task in notified_task_progress:
            print(f"  - {task[0]}\n\t{ntn.build_notion_url(task[1])}")
        print()


    if task_count + conference_count <= 0:
        print("未通知のタスクまたは会議はありませんでした")
    else:
        print(f"タスク: {task_count}件\n会議: {conference_count}件\n計: {task_count + conference_count}件のDiscordへの通知が完了しました。")
        print()

        if conference_count > 0:
            print("会議の予定はサーバーにイベント登録してね")


if __name__ == "__main__":
    main()
