#!/usr/bin/env python3

import pycgi, pycgitb
import os, sys, markdown

CGI_BIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CGI_BIN_DIR)
from lib.MySQAPI import MySQAPI

def run_sql(sql, database = None):
    """
    #### SQL文を実行する

    `database` が指定されている場合、先に`USE `database`;`を実行してから
    本来の`sql`を実行する。

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | `sql` | `str` | 実行するSQL文 |
    | `database` | `str \\| None` | 事前に`USE`するデータベース名(省略時は`USE`しない) |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `list[tuple] \\| str` | `list` または `str` | 実行結果、または例外発生時のエラーメッセージ |
    """
    try:
        with MySQAPI(user="root") as db:
            if database:
                db.send_sql(f"USE `{database}`;")
            return db.send_sql(sql)
    except Exception as e:
        return str(e)


def list_databases():
    """
    #### データベース一覧を取得する

    `SHOW DATABASES;`を実行し、データベース名のみのリストへ変換する。

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `list[str]` | `list` | データベース名の一覧(取得失敗時は空リスト) |
    """
    try:
        with MySQAPI(user="root") as db:
            rows = db.send_sql("SHOW DATABASES;")
        return [row[0] for row in rows]
    except Exception:
        return []


def build_database_options(databases, selected = None):
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

class WebCGI:
    def __init__(self, lang = "ja"):
        self.TEMPLATE_DIR   = os.path.join(os.path.dirname(CGI_BIN_DIR), "template")
        self.log            = pycgitb.enable()
        self.lang           = lang
        self.md             = markdown.Markdown(extensions=["extra", "tables", "attr_list"])


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

        ref = self.md.convert(self.load_template("html", "howtouse.md"))
        ref = ref.replace(
            "<table>", 
            """<table class= "table table-bordered table-striped">"""
        ).replace(
            "<td>",
            """<td class="text-nowrap">"""
        )

        ref = f"""
<div class = "pt-4">
    {ref}
</div>
""" 
        self.log.handler(sql)

        # データベース一覧を取得し、実在するものだけを選択中データベースとして扱う
        databases = list_databases()
        database  = database if database in databases else None

        result = run_sql(sql, database = database)
        body = self.load_template("html", "body.html").format(
            sql      = sql,
            result   = result,
            database = database or os.environ.get("DB_NAME", "未選択"),
        )

        return self.load_template("html", "index.html").format(
            lang  = self.lang,
            title = title,
            head  = "",
            style = self.load_template("html", "styleConfig.html"),
            header = self.load_template("html", "header.html").format(
                database = build_database_options(databases, selected = database),
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
