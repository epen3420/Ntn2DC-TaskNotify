import notion_client as ntn
import discord_client as dc
import utils
import config
from typing import Tuple, Any, Optional

def main():
    # メンバーDBから一度だけメンバー情報を取る
    member_dict = ntn.retrieve_member_dict()
    if member_dict == dict():
        print("NullException: Can't get member list")
        exit()

    # 進行中 かつ 通知済チェック無し のタスクを取得 (config.PROP_NOTIFIED_NAME が False のもの)
    print("Fetching tasks from Notion...")
    data = ntn.fetch_db_only_status_progress()

    candidates = []

    # 候補リスト作成
    for record in data.get(config.KEY_RESULTS, []):
        page_id = record.get(config.KEY_ID)
        if not page_id: continue

        title = ntn.get_title(record)
        if not title: continue

        start_time_str = ntn.get_stateDate(record)
        deadline_str = ntn.get_deadline(record)

        assignee_records = ntn.get_relation_records(record, config.PROP_ASSIGNEE_NAME)
        assignee_names = [member_dict[assignee_id.get(config.KEY_ID)] for assignee_id in assignee_records]

        kind = ntn.get_select_value(record, config.PROP_KIND_NAME)

        candidates.append({
            "idx": 0, # Placeholder
            "title": title,
            "page_id": page_id,
            "kind": kind,
            "deadline": deadline_str,
            "start_time": start_time_str,
            "assignees": assignee_names,
            "record": record
        })

    if not candidates:
        print("No tasks found to notify.")
        return

    # インタラクティブに送信対象を選択
    selected_tasks = []
    print(f"\nFound {len(candidates)} candidate tasks/conferences.")

    for i, task in enumerate(candidates):
        print("-" * 50)
        print(f"[{i+1}/{len(candidates)}] {task['kind']}")
        print(f"Title: {task['title']}")
        if task['kind'] == config.PROP_TASK_NAME:
            print(f"Deadline: {task['deadline']}")
        else:
            print(f"Start Time: {task['start_time']}")
        print(f"Assignees: {', '.join(task['assignees'])}")

        if utils.ask_yes_no("Add to notification list?"):
            selected_tasks.append(task)
            print(">> Added.")
        else:
            print(">> Skipped.")

    if not selected_tasks:
        print("\nNo tasks selected. Exiting.")
        return

    # 最終確認
    print("\n" + "=" * 50)
    print(f"You have selected {len(selected_tasks)} items to notify:")
    for task in selected_tasks:
        print(f" - [{task['kind']}] {task['title']}")
    print("=" * 50)

    if not utils.ask_yes_no("Proceed to send notifications and update Notion status?"):
        print("Aborted.")
        return

    # 送信処理
    print("\nSending notifications...")
    success_count = 0
    for task in selected_tasks:
        try:
            if task['kind'] == config.PROP_TASK_NAME:
                dc.send_task_message(task['title'], task['page_id'], task['assignees'], task['deadline'])
            elif task['kind'] == config.PROP_CONFERENCE_NAME:
                dc.send_conference_message(task['title'], task['page_id'], task['assignees'], task['start_time'])

            # Notionの「通知済」チェックボックスを更新
            ntn.update_page_checkbox(task['page_id'], config.PROP_NOTIFIED_NAME, True)
            print(f"[OK] {task['title']}")
            success_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to process '{task['title']}': {e}")

    print(f"\nCompleted. {success_count}/{len(selected_tasks)} notifications sent.")


if __name__ == "__main__":
    main()
