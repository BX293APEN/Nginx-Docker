#!/usr/bin/env python3

import pycgi, pycgitb
import os, sys

CGI_BIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CGI_BIN_DIR)
from view.MySQAPI import MySQAPI

def run_sql(sql):
    try:
        with MySQAPI() as db:
            return db.send_sql(sql)
    except Exception as e:
        return str(e)

class WebCGI:
    def __init__(self, lang = "ja"):
        self.TEMPLATE_DIR   = os.path.join(CGI_BIN_DIR, "template")
        self.log            = pycgitb.enable()
        self.lang           = lang

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

    def urls(self, sql):
        """
        #### ページ全体のHTMLを生成する

        `template/html/index.html`(骨格・CGIヘッダー付き)へ
        `template/html/body.html`(フォーム＋結果)と`template/css/main.css`を
        それぞれ埋め込んで、レスポンス全体(ヘッダー含む)を組み立てる。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `sql` | `str` | フォームに再表示するSQL文 |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `str` | `str` | CGIヘッダーを含む、出力するレスポンス全体 |
        """
        self.log.handler(sql)
        result = run_sql(sql)
        body = self.load_template("html", "body.html").format(
            sql = sql,
            result = result,
        )

        return self.load_template("html", "index.html").format(
            lang  = self.lang,
            title = "MySQLCGI",
            head  = "",
            css   = self.load_template("css", "main.css"),
            html  = body,
        )



if __name__ == "__main__":
    form    = pycgi.FieldStorage()
    html    = WebCGI()

    print(html.urls(form.getvalue("sqlform", default = "SHOW DATABASES;")))
