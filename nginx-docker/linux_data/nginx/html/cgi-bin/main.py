#!/usr/bin/env python3
"""
### cgi-bin/main.py

`index.html` のフォームから送信されたSQL文を受け取り、`MySQAPI` 経由でMySQLへ送信し、
結果（またはエラー）を同デザインのページ下部に表示するCGIスクリプト。

`CGITEST`（libcgipyのサンプル）と同様に、ページの骨格は`template/html/`配下の
テンプレートファイルへ分離し、`str.format()`で組み立てる方式を採用する。
CGIヘッダー（`Content-Type`等）も骨格テンプレート側に含めているため、
このスクリプト自身はヘッダーを個別に出力する必要が無い。

libcgipy（`httpcgi.CGIHTTP`）によってCGIとして起動されることを前提としており、
フォームデータの取得には旧`cgi`モジュール相当の `pycgi.FieldStorage` を、
例外発生時のサーバー側トレースバック出力には旧`cgitb`モジュール相当の
`pycgitb.enable` を使用する。
"""

import os
import sys
import html
import traceback
import pycgi
import pycgitb

# 同じディレクトリのview/MySQAPI.pyをimportできるようにする
CGI_BIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CGI_BIN_DIR)
from view.MySQAPI import MySQAPI

TEMPLATE_DIR = os.path.join(CGI_BIN_DIR, "template")

# --- トレースバック出力先の設定 ---
# 画面(クライアント)には詳細なエラーを出さず、サーバー側の標準エラー出力(コンテナのログ)に
# 詳細なトレースバックを残すことで、開発時のデバッグをしやすくする
cgitb = pycgitb.enable(logdir=sys.stderr)


def load_template(*relative_path_parts):
    """
    #### テンプレートファイルを読み込む

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | `*relative_path_parts` | `str` | `template/` からの相対パス構成要素(可変長) |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `str` | `str` | 読み込んだテンプレートの内容 |
    """
    path = os.path.join(TEMPLATE_DIR, *relative_path_parts)
    with open(path, "r", encoding="UTF-8") as f:
        return f.read()


def read_post_sql():
    """
    #### POSTデータからSQL文を取り出す

    `pycgi.FieldStorage` を用いてフォームデータ（`sql`パラメータ）を取得する。
    `CONTENT_LENGTH` / `CONTENT_TYPE` 等の読み取りは `FieldStorage` 側が行う。

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `str` | `str` | フォームから送信されたSQL文（未送信時は空文字） |
    """
    form = pycgi.FieldStorage()
    return form.getfirst("sql", "")


def run_sql(sql):
    """
    #### SQL文をMySQLへ送信して実行する

    失敗した場合は、詳細なトレースバックを `pycgitb` 経由でサーバー側へ出力しつつ、
    画面に表示するのはエラーメッセージのみに留める。

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | `sql` | `str` | 実行するSQL文 |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `bool` | `ok` | 成功したかどうか |
    | `list[tuple] \\| str` | `result` | 成功時は実行結果の行リスト、失敗時はエラーメッセージ |
    """
    try:
        with MySQAPI() as db:
            return True, db.send_sql(sql)
    except Exception as e:
        cgitb.handler(traceback.format_exc())  # 詳細なトレースバックはサーバー側(標準エラー)へ
        return False, str(e)                   # 画面には簡潔なメッセージのみ表示


def render_result_html(sql, ok, result):
    """
    #### 結果表示部分のHTML断片を生成する

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | `sql` | `str` | 実行したSQL文（未入力なら何も表示しない） |
    | `ok` | `bool` | 成功したかどうか |
    | `result` | `list[tuple] \\| str` | 成功時は結果行のリスト、失敗時はエラーメッセージ |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `str` | `str` | ページ下部に埋め込むHTML文字列 |
    """
    if not sql:
        return ""

    if not ok:
        return f'<p class="error">エラー: {html.escape(str(result))}</p>'

    if not result:
        return '<p class="ok">実行が完了しました（該当データなし）。</p>'

    rows_html = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(col))}</td>" for col in row) + "</tr>"
        for row in result
    )
    return f'<p class="ok">実行が完了しました。</p><table class="result"><tbody>{rows_html}</tbody></table>'


def render_page(sql, result_html):
    """
    #### ページ全体のHTMLを生成する

    `template/html/index.html`(骨格・CGIヘッダー付き)へ
    `template/html/body.html`(フォーム＋結果)と`template/css/main.css`を
    それぞれ埋め込んで、レスポンス全体(ヘッダー含む)を組み立てる。

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | `sql` | `str` | フォームに再表示するSQL文 |
    | `result_html` | `str` | 下部に埋め込む結果HTML |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `str` | `str` | CGIヘッダーを含む、出力するレスポンス全体 |
    """
    body = load_template("html", "body.html").format(
        sql    = html.escape(sql),
        result = result_html,
    )

    return load_template("html", "index.html").format(
        lang  = "ja",
        title = "SQL実行くん",
        head  = "",
        css   = load_template("css", "main.css"),
        html  = body,
    )


def main():
    """
    #### エントリポイント

    CGIとして呼び出された際の一連の処理（POSTデータ取得 → SQL実行 → HTML出力）を行う。
    `render_page()` が返す文字列にはCGIヘッダー（`Content-Type`等）と空行、
    続けて本文が既に含まれているため、そのまま標準出力へ書き出すだけでよい。
    """
    sql = read_post_sql() if os.environ.get("REQUEST_METHOD") == "POST" else ""
    ok, result = (True, None) if not sql else run_sql(sql)

    sys.stdout.write(render_page(sql, render_result_html(sql, ok, result)))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
