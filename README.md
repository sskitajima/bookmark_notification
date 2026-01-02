# bookmark_notification

bookmarkしたリンクをランダムに選んで、ユーザにメールで通知する。
cron等のサービスで定期実行できるようにして、過去のブックマークの内容を定期的にユーザに思い出させることを目的とする。

## Requirements

- サービスの互換性
  - Instapaperでも、他のサービスでも実行可能にする
  - gmail APIでも、他のメーラーでも実行可能にする
- 機能拡張性
  - 内容をAIによって処理させる余地を残す

## Design

- アプリケーションのエントリポイント
- Instapaperからbookmarkを取得する機能
- 取得したbookmarkからユーザに送信するものを選ぶ機能
- メールを送信する機能

```plantuml
@startuml "Overview of the class diagram"

struct Bookmark {
  id: int
  title: str
  url : str
  tags: list[str]
}

struct MailContent {
  to: str
  from: str
  subject: str
  content: str
}

class InstapaperRetriever {
  -x_auth_username: str
  -x_auth_password: str

  -BASE_URL: str
  -BOOKMARKS_LIST_URL : str
  -ADD_LIST_URL : str
  -DELETE_BOOKMARK_URL : str
  -STAR_BOOKMARK_URL : str
  -UNSTAR_BOOKMARK_URL : str
  -ARCHIVE_BOOKMARK_URL : str
  -UNARCHIVE_BOOKMARK_URL : str

  +retreive_bookmark()
  -get_access_token()
  -get_bookmarks_from_server()
  -generate_bookmark_object()
}

class ContentManager {
  +select_publish_content(list[Bookmark])
}

class MailSender {
  -credential_path

  +send_email()
}

class MailWriter {
  +write_email()
}

class Response {
  code: int
  msg: str
}

@enduml
```

```plantuml
@startuml "file structure"

folder scripts {
  file "main.py"
  
  folder common {
    file "response.py"
    file "mail_content.py"
    file "bookmark.py"
    file "logger.py"
    file "content_manager.py"
  }
  
  folder instapaper {
    file "instapaper_retriever.py"
  }
  
  folder mail {
    file "mail_sender.py"
    file "mail_writer.py"
  }
}

folder config {
  file "config.yaml"
  file "token.json"
}

@enduml
```

```plantuml
@startuml "application sequence"

autoactivate on

participant main
participant InstapaperRetriever
participant ContentManager
participant MailWriter
participant MailSender

-> main : execute the app

  main -> InstapaperRetriever : retrieve_bookmark()
  return list[Bookmark]

  main -> ContentManager: select_publish_content(list[Bookmark])
  return list[Bookmark]

  main -> MailWriter : write_email(list[Bookmark])
  return MailContent

  main -> MailSender : send_email(MailContent)
  return 

return

@enduml
```

- configurationはyamlファイルで行う
- loggingは、loggingモジュールで行う

## 準備

- Google CloudのOAuthの準備
- Instapaper APIの準備
- cronの準備

## その他

- 各技術要素の実装のプロトタイプが`prototype/`ディレクトリにある
