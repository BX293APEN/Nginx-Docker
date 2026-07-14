#!/usr/bin/env python3

import pycgi, pycgitb
import os, sys, markdown

CGI_BIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CGI_BIN_DIR)
from lib.MySQAPI import MySQAPI

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
        | `host` | `str \\| None` | 接続先ホスト名(未指定時は環境変数`DB_HOST`) |
        | `port` | `int \\| None` | 接続先ポート番号(未指定時は環境変数`DB_PORT`) |
        | `user` | `str` | 接続ユーザー名(既定値`"root"`) |
        | `password` | `str \\| None` | 接続パスワード(未指定時は環境変数`DB_ROOT_PASSWORD`) |
        | `database` | `str \\| None` | 使用するデータベース名(未指定時は環境変数`DB_NAME`) |
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
        | `database` | `str \\| None` | 事前に`USE`するデータベース名(省略時は`USE`しない) |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `list[tuple] \\| str` | `list` または `str` | 実行結果、または例外発生時のエラーメッセージ |
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

class WebCGI:
    def __init__(self, lang = "ja"):
        self.TEMPLATE_DIR   = os.path.join(os.path.dirname(CGI_BIN_DIR), "template")
        self.log            = pycgitb.enable()
        self.lang           = lang
        self.md             = markdown.Markdown(extensions=["extra", "tables", "attr_list"])

    def build_database_options(self, databases, selected = None):
        """
        #### データベース選択用プルダウンの選択肢HTMLを生成する

        `header.html`の`{database}`プレースホルダーへ埋め込む
        `<li>`要素(Bootstrapドロップダウンの項目)を組み立てる。
        各項目は`?database=<db名>&sql=SHOW TABLES;`へのリンクとなり、
        選択中のデータベースには`active`クラスを付与する。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `databases` | `list[str]` | 表示するデータベース名の一覧 |
        | `selected` | `str \\| None` | 現在選択中のデータベース名 |

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
                f'<li><a class="dropdown-item{active}" href="?database={name}&sql=SHOW TABLES;">{name}</a></li>'
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

    def urls(self, sql, database = None, title = "MySQLCGI"):
        """
        #### ページ全体のHTMLを生成する

        `template/html/index.html`(骨格・CGIヘッダー付き)へ
        `template/html/body.html`(フォーム＋結果)と`template/css/main.css`を
        それぞれ埋め込んで、レスポンス全体(ヘッダー含む)を組み立てる。

        データベース一覧を取得して`header.html`のプルダウンメニューへ反映し、
        `database`が実在するデータベース名であれば`USE `database`;`を
        実行してから`sql`を実行する。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `sql` | `str` | フォームに再表示するSQL文 |
        | `database` | `str \\| None` | プルダウンで選択されたデータベース名 |
        | `title` | `str` | ページタイトル |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `str` | `str` | CGIヘッダーを含む、出力するレスポンス全体 |
        """

        self.log.handler(sql)

        with ControlSQL() as db:
            # データベース一覧を取得
            databases = db.list_databases()
            # 実在するものだけを選択中データベースとして扱う
            database  = database if database in databases else None
            result = db.run_sql(sql, database = database)
        
        ref = self.md.convert(
            self.load_template("html", "howtouse.md").format(
                selectdb = database or os.environ.get("DB_NAME", "XXX"),
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
        body = self.load_template("html", "body.html").format(
            result   = result,
            database = database or os.environ.get("DB_NAME", "未選択"),
        )

        return self.load_template("html", "index.html").format(
            lang  = self.lang,
            title = title,
            head  = "",
            style = self.load_template("html", "styleConfig.html"),
            header = self.load_template("html", "header.html").format(
                database = self.build_database_options(databases, selected = database),
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

    print(html.urls(
        form.getvalue("sql", default = "SHOW DATABASES;"),
        database = form.getvalue("database", default = None),
    ))
