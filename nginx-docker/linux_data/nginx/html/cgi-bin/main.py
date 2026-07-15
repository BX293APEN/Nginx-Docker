#!/usr/bin/env python3

import pycgi, pycgitb
import os, sys, markdown
from http.cookies import SimpleCookie

CGI_BIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CGI_BIN_DIR)
from lib.MySQAPI import MySQAPI
from lib.SessionStore import SessionStore


class ControlSQL(MySQAPI):
    def __init__(
        self,
        host     = None,
        port     = None,
        user     = "root",
        password = None,
        database = None,
    ):
        """
        #### コンストラクタ

        `MySQAPI`を継承し、`USE`実行を伴うSQL送信機能を追加する。
        引数はそのまま`MySQAPI`のコンストラクタへ渡される
        (未指定項目は`MySQAPI`側で対応する環境変数から取得される)。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `host` | `str | None` | 接続先ホスト名(未指定時は環境変数`DB_HOST`) |
        | `port` | `int | None` | 接続先ポート番号(未指定時は環境変数`DB_PORT`) |
        | `user` | `str` | 接続ユーザ名(既定値`"root"`) |
        | `password` | `str | None` | 接続パスワード(未指定時は環境変数`DB_ROOT_PASSWORD`) |
        | `database` | `str | None` | 使用するデータベース名(未指定時は環境変数`DB_NAME`) |
        """
        super().__init__(
            host,
            port,
            user,
            password,
            database,
        )

    def run_sql(self, sql : str, database = None):
        """
        #### SQL文を実行する

        `database`が指定されている場合、先に`USE `database`;`を実行してから
        本来の`sql`を実行する。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `sql` | `str` | 実行するSQL文 |
        | `database` | `str | None` | 事前に`USE`するデータベース名(省略時は`USE`しない) |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `list[tuple] | str` | `list` または `str` | 実行結果、または例外発生時のエラーメッセージ |
        """

        if sql.count(";") > 0:
            sqlexe = sql.split(";")
        else:
            sqlexe = [sql]
        
        try:
            if database:
                self.send_sql(f"USE `{database}`;")
        except Exception as e:
            return f"""
<div>
    <h3 class="pt-3">USE `{database}`;</h3>
    <p>
        {e}
    </p>
</div>
"""
        
        value = ""
        try:
            for s in sqlexe:
                if s == "":
                    continue
                result = self.send_sql(s)
                value += f"""
<div>
    <h3 class="pt-3">{s};</h3>
    <p>
        {result if isinstance(result, str) else "<br>".join([f"{r}" for r in result])}
    </p>
</div>
"""
        except Exception as e:
            # sのSQL文が失敗したら終了
            value +=  f"""
<div>
    <h3 class="pt-3">{s};</h3>
    <p>
        {e}
    </p>
</div>
"""
        finally:
            return value


    def list_databases(self):
        """
        #### データベース一覧を取得する

        `SHOW DATABASES;`を実行し、データベース名のみのリストへ変換する。

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `list[str]` | `list` | データベース名の一覧(取得失敗時は空リスト) |
        """
        try:
            rows = self.send_sql("SHOW DATABASES;")
            return [row[0] for row in rows]
        except Exception:
            return []

    def list_users(self):
        """
        #### 接続可能なDBユーザ一覧を取得する

        `mysql.user`テーブルを参照し、ユーザ名のみの一覧(重複無し・昇順)へ変換する。
        この一覧の取得には`root`相当の権限を持つ接続が必要。

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `list[str]` | `list` | ユーザ名の一覧(取得失敗時は空リスト) |
        """
        try:
            rows = self.send_sql("SELECT DISTINCT User FROM mysql.user WHERE User != '';")
            return sorted({row[0] for row in rows})
        except Exception:
            return []

class WebCGI:
    def __init__(self, lang = "ja"):
        """
        #### コンストラクタ

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `lang` | `str` | ページの`lang`属性へ設定する言語コード(既定値`"ja"`) |
        """
        self.TEMPLATE_DIR   = os.path.join(os.path.dirname(CGI_BIN_DIR), "template")
        
        self.log            = pycgitb.enable()
        self.lang           = lang
        self.md             = markdown.Markdown(extensions=["extra", "tables", "attr_list"])
        
        # ==============================================================
        # ログイン成功時に発行するセッション(user/passwordの紐付け)を管理する
        # ==============================================================
        # セッションIDをやり取りするCookie名
        self.SESSION_COOKIE_NAME = "session_id"
        # セッション(Cookie)のタイムアウト時間[秒]
        self.SESSION_TTL_SECONDS = 30 * 60
        self.session_store  = SessionStore(ttl_seconds = self.SESSION_TTL_SECONDS)

    def build_database_options(self, databases, selected = None, user = "root"):
        """
        #### データベース選択用プルダウンの選択肢HTMLを生成する

        `header.html`の`{database_options}`プレースホルダーへ埋め込む
        `<li>`要素(Bootstrapドロップダウンの項目)を組み立てる。
        各項目は`?user=<接続ユーザ>&database=<db名>&sql=SHOW TABLES;`
        へのリンクとなり、選択中のデータベースには`active`クラスを付与する。
        認証状態はCookieのセッションIDで維持するため、`password`は
        リンクに一切含めない。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `databases` | `list[str]` | 表示するデータベース名の一覧 |
        | `selected` | `str | None` | 現在選択中のデータベース名 |
        | `user` | `str` | 現在接続中のユーザ名(既定値`"root"`) |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `str` | `str` | `<li>`要素を連結したHTML文字列 |
        """
        if not databases:
            return '<li><span class="dropdown-item-text text-muted">データベースがありません</span></li>'

        items = []
        for name in databases:
            active = " active" if name == selected else ""
            items.append(
                f'<li><a class="dropdown-item{active}" '
                f'href="?user={user}&database={name}&sql=SHOW TABLES;">{name}</a></li>'
            )
        return "\n".join(items)

    def build_user_options(self, users, selected = None, database = None):
        """
        #### DBユーザ選択用プルダウンの選択肢HTMLを生成する

        `header.html`の`{user_options}`プレースホルダーへ埋め込む
        `<li>`要素(Bootstrapドロップダウンの項目)を組み立てる。
        各項目は`?user=<ユーザ名>&database=<db名>&sql=SHOW DATABASES;`へのリンクとなり、
        選択中のユーザには`active`クラスを付与する。
        `root`以外のユーザを選択した場合、有効なセッションが無ければ
        `urls`メソッド側の認証チェックによりパスワード入力画面へ遷移する。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `users` | `list[str]` | 表示するユーザ名の一覧 |
        | `selected` | `str | None` | 現在選択中のユーザ名 |
        | `database` | `str | None` | 現在選択中のデータベース名(切替後も維持する) |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `str` | `str` | `<li>`要素を連結したHTML文字列 |
        """
        if not users:
            return '<li><span class="dropdown-item-text text-muted">ユーザが設定されていません</span></li>'

        database = database or ""
        items = []
        for name in users:
            active = " active" if name == selected else ""
            items.append(
                f'<li><a class="dropdown-item{active}" '
                f'href="?user={name}&database={database}&sql=SHOW DATABASES;">{name}</a></li>'
            )
        return "\n".join(items)

    def load_template(self, *relative_path_parts):
        """
        #### テンプレートファイルを読み込む

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `*relative_path_parts` | `str` | `template/` からの相対パス構成要素(可変長) |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `str` | `str` | 読み込んだテンプレートの内容 |
        """
        path = os.path.join(self.TEMPLATE_DIR, *relative_path_parts)
        with open(path, "r", encoding="UTF-8") as f:
            return f.read()

    def read_session_id(self):
        """
        #### リクエストのCookieからセッションIDを取得する

        環境変数`HTTP_COOKIE`(fastcgi_paramsにより`Cookie`ヘッダーから設定される)
        を解析し、`SESSION_COOKIE_NAME`の値を取り出す。

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `str | None` | `str` | Cookieに含まれるセッションID(無ければ`None`) |
        """
        cookie = SimpleCookie()
        cookie.load(os.environ.get("HTTP_COOKIE", ""))
        morsel = cookie.get(self.SESSION_COOKIE_NAME)
        return morsel.value if morsel else None

    def urls(self, form, title = "MySQLCGI"):
        """
        #### ページ全体を生成する

        `template/html/index.html`(骨格)へ`template/html/body.html`
        (フォーム＋結果)、または`root`以外のユーザへの切替時で
        パスワード未確定の場合は`template/html/password.html`
        (パスワード入力フォーム)を埋め込んでレスポンス本文を組み立てる。

        認証状態はCookieの`session_id`で管理する。

        | 条件 | 処理 |
        | --- | --- |
        | `POST`でパスワード送信 | 受信したパスワードで接続試行 → 成功したらセッション発行(有効期限 : `SESSION_TTL_SECONDS`) & Cookieを返す |
        | 既存セッションが同じユーザのもの | 保存済みのパスワードを使って自動的に再接続 |
        | 上記以外 | パスワード入力画面を返す |

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `form` | `pycgi.FieldStorage` | GETクエリまたはPOSTボディから取得したフォームデータ |
        | `title` | `str` | ページタイトル |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `tuple[str, str]` | `tuple` | `(Set-Cookieヘッダー行(無ければ空文字列), レスポンス本文HTML)` |
        """

        sql             = form.getvalue("sql", default = "SHOW DATABASES;")
        database        = form.getvalue("database", default = None)
        user            = form.getvalue("user", default = "root") or "root"
        request_method  = os.environ.get("REQUEST_METHOD", "GET").upper()

        self.log.handler(sql)

        # データベース一覧・ユーザ一覧は常にroot(既定接続)から取得する
        with ControlSQL() as admin_db:
            databases = admin_db.list_databases()
            users     = admin_db.list_users()

        # 実在するものだけを選択中データベース/ユーザとして扱う
        database = database if database in databases else None
        user     = user if (user == "root" or user in users) else "root"

        session_id = self.read_session_id()
        session    = self.session_store.load(session_id)

        set_cookie_header = ""
        password           = None
        is_new_login       = False

        if request_method == "POST" and form.getvalue("password", default = None):
            # password.html からのログイン送信。POSTボディのみで受け取り、
            # 以降はこのパスワードをURLやHTMLへ一切書き出さない
            password     = form.getvalue("password")
            is_new_login = True
        elif session and session.get("user") == user:
            # 既存セッションに紐づくパスワードを使って自動的に再接続する
            password = session.get("password")

        # 有効な認証情報(POSTされたパスワード、または同一ユーザの
        # 有効なセッション)が無ければ認証待ちにする。root も例外にしない。
        need_password = not password
        auth_error    = None
        result        = ""

        if not need_password:
            try:
                with ControlSQL(user = user, password = password) as db:
                    result = db.run_sql(sql, database = database)

                if is_new_login:
                    # 認証に成功した場合のみ新しいセッションを発行する
                    # (root を含む全ユーザ共通。Cookie自体の有効期限も
                    #  SessionStore側のTTLと合わせて30分にする)
                    new_session_id = self.session_store.create(user, password)

                    # HTTPS化した際は `; Secure` を追加すること
                    set_cookie_header = f"""\
Set-Cookie: {self.SESSION_COOKIE_NAME}={new_session_id}; \
Path=/; HttpOnly; SameSite=Lax; \
Max-Age={self.SESSION_TTL_SECONDS} \
"""
                    
            except Exception as e:
                # 接続失敗(パスワード誤りなど)の場合もパスワード入力画面へ戻す
                need_password = True
                auth_error    = str(e)

        ref = self.md.convert(
            self.load_template("html", "howtouse.md").format(
                selectdb = database or os.environ.get("DB_NAME", "XXX"),
                userName = user
            )
        )
        ref = ref.replace(
            "<table>", 
            """<table class= "table table-bordered table-striped">"""
        ).replace(
            "<td>",
            """<td class="text-nowrap">"""
        )

        ref = f"""
<div class = "border-top">
    {ref}
</div>
""" 
        if need_password:
            body = self.load_template("html", "password.html").format(
                user     = user,
                database = database or "",
                sql      = sql,
                error    = f'<br><span class="text-danger">{auth_error}</span>' if auth_error else "",
            )
        else:
            body = self.load_template("html", "body.html").format(
                result   = result,
                database = database or os.environ.get("DB_NAME", "未選択"),
                user     = user,
            )


        return self.load_template("html", "index.html").format(
            lang  = self.lang,
            cookie = set_cookie_header,
            title = title,
            head  = "",
            style = self.load_template("html", "styleConfig.html"),
            header = self.load_template("html", "header.html").format(
                database_options = self.build_database_options(
                    databases, selected = database, user = user,
                ),
                user_options = self.build_user_options(
                    users, selected = user, database = database,
                ),
                user     = user,
                database = database or "",
            ),
            html  = body,
            css = "",
            footer = f"""
<div class="container pt-3">
    {ref}
</div>
"""
        )


if __name__ == "__main__":
    form    = pycgi.FieldStorage()
    html    = WebCGI()

    print(html.urls(form))