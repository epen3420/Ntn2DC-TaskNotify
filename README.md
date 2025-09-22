# Ntn2DC-TaskNotify

プロジェクト"メテオコア・レギオン"専用のアプリケーションです。
NotionデータベースとDiscord Webhookを連携し、タスクのステータス変更を自動的にDiscordに通知を行います。

## 機能

- **Notionデータベース監視**: 指定されたNotionデータベースのページを定期的に監視
- **ステータス変更検知**: タスクのステータスが「進行中」に変更された際を検知
- **Discord通知**: ステータス変更時に担当者をメンションしてDiscordに通知
- **ユーザーマッピング**: Notionの担当者名とDiscord IDをマッピング
- **通知制御**: 非通知フラグや強制通知フラグによる通知の制御

## 必要要件

- Python 3.7+
- 必要なPythonパッケージ:
  - `requests`
  - `python-dotenv`

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/tokizg/Ntn2DC-TaskNotify.git
cd Ntn2DC-TaskNotify
```

### 2. 依存関係のインストール

```bash
pip install requests python-dotenv
```

### 3. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成し、以下の内容を設定してください：

```env
# Notion API設定
NOTION_TOKEN=ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Notionデータベース設定
NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Discord設定
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### 環境変数の取得方法

- **NOTION_TOKEN**: Notionのコネクトの内部インテグレーションシークレット。[Notion Developers(開発者ポータル)](https://www.notion.so/my-integrations)でインテグレーションを作成してください。
- **NOTION_DATABASE_ID**: NotionデータベースページのURLから取得できます。

```text
https://www.notion.so/ この部分がデータベースのIDです ?v=〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇
```

- **DISCORD_WEBHOOK_URL**: Discordサーバーのチャンネル設定でWebhook URLを作成し、ここに割り当ててください。

### 4. ユーザーマッピングの設定

`src/user_map.json` ファイルを作成し、Notionに設定した人物名（担当者・確認者）とDiscord IDを紐づけてください：

```json
{
  "山田太郎": "123456789012345678",
  "佐藤花子": "234567890123456789",
  "田中一郎": "345678901234567890"
  ...
}
```

### 5. Notionデータベースの設定

監視対象のNotionデータベースには以下のプロパティが必要です：

| プロパティ名 | タイプ | 説明 |
|------------|--------|------|
| 名前 | タイトル | タスクのタイトル |
| ステータス | ステータス | タスクの進行状況 |
| 担当者 | マルチセレクト | タスクの担当者 |
| 確認者 | マルチセレクト | タスクの確認者（オプション） |
| 非通知 | チェックボックス | 通知を無効にするフラグ |
| 強制通知 | チェックボックス | 強制的に通知するフラグ |

## 使用方法

### 基本的な実行

```bash
cd src
python notion_monitor.py
```

### 定期実行について

このプログラムは、定期実行を前提にしていません。
手動で実行されることを想定して実装しています。

## ファイル構成

```text
Ntn2DC-TaskNotify/
├── README.md
├── .env                    # 環境変数設定（要作成）
└── src/
    ├── notion_monitor.py   # メインスクリプト
    ├── user_map.json      # ユーザーマッピング（要作成）
    └── last_state.json    # 前回の状態保存（自動生成）
```

## 通知の仕組み

1. **フィルタリング**:
  a. **"進行中"に変わった場合**: 基本的に、ステータスが"進行中"になったタスクのみ通知を行います。
  b. **"強制通知"フラグ**: ステータスの更新の有無にかかわらず、これがTrueなタスクはすべて通知を行います。通知後に、このフラグはFalseになります。
  c. **"非通知"フラグ**: このフラグがTrueなタスクは、通知が行われません。
  フラグの優先順位は、**非通知フラグ** > **強制通知フラグ**です。
2. **メッセージ配信**: 担当者をメンションしてDiscordに通知

## 注意事項

- `.env`ファイルと`user_map.json`、Gitリポジトリにコミットしないよう`.gitignore`に追加してください
- Notionのインテグレーションにはデータベースへのアクセス権限を付与する必要があります
- 各サーバーで、Discord Webhookの権限設定を適切に行ってください

## Licence

このプロジェクトはMITライセンスの下で公開されています。

## Contribution

バグレポートや機能提案は、GitHubのIssuesでお知らせください。
