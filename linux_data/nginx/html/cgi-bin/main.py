#!/usr/bin/env python3
"""
### cgi-bin/main.py

`index.html` のフォームから送信されたSQL文を受け取り、`MySQAPI` 経由でMySQLへ送信し、
結果（またはエラー）を `index.html` と同じデザインのページ下部に表示するCGIスクリプト。

libcgipy（`httpcgi.CGIHTTP`）によってCGIとして起動されることを前提としており、
`os.environ` の `REQUEST_METHOD` / `CONTENT_LENGTH` 等を利用して
標準入出力（`sys.stdin` / `sys.stdout`）経由でリクエスト・レスポンスをやり取りする。
"""

import os
import sys
import html
from urllib.parse import parse_qs

# 同じディレクトリのMySQAPI.pyをimportできるようにする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from view.MySQAPI import MySQAPI


def read_post_sql():
    """
    #### POSTデータからSQL文を取り出す

    `CONTENT_LENGTH` バイト分だけ標準入力から読み取り、`sql` パラメータの値を取得する。

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `str` | `str` | フォームから送信されたSQL文（未送信時は空文字） |
    """
    length = int(os.environ.get("CONTENT_LENGTH", 0) or 0)
    body   = sys.stdin.buffer.read(length).decode("utf-8", "replace") if length else ""
    params = parse_qs(body)
    return params.get("sql", [""])[0]


def run_sql(sql):
    """
    #### SQL文をMySQLへ送信して実行する

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
        return False, str(e)


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
    #### ページ全体のHTMLを生成する（index.htmlと共通のデザインを使用）

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | `sql` | `str` | フォームに再表示するSQL文 |
    | `result_html` | `str` | 下部に埋め込む結果HTML |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | `str` | `str` | 出力するHTML全体 |
    """
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>SQL実行くん</title>
<style>
    body          {{ font-family: sans-serif; margin: 2rem; }}
    textarea      {{ width: 100%; max-width: 600px; box-sizing: border-box; }}
    table.result  {{ border-collapse: collapse; margin-top: 1rem; }}
    table.result td {{ border: 1px solid #999; padding: 4px 8px; }}
    p.error       {{ color: #c00; }}
    p.ok          {{ color: #060; }}
</style>
</head>
<body>
<h1>SQL実行くん (MySQL連携)</h1>

<form method="POST" action="/cgi-bin/main.py">
    <label for="sql">SQL文</label><br>
    <textarea id="sql" name="sql" rows="6" cols="60">{html.escape(sql)}</textarea><br>
    <button type="submit">実行</button>
</form>

{result_html}
</body>
</html>
"""


def main():
    """
    #### エントリポイント

    CGIとして呼び出された際の一連の処理（POSTデータ取得 → SQL実行 → HTML出力）を行う。
    レスポンスはCGIの仕様に従い、ヘッダー（`Content-Type` 等）と空行、続けて本文の順に
    標準出力（実体はNginxから中継されたクライアントソケット）へ書き出す。
    """
    sql = read_post_sql() if os.environ.get("REQUEST_METHOD") == "POST" else ""
    ok, result = (True, None) if not sql else run_sql(sql)
    body = render_page(sql, render_result_html(sql, ok, result))

    sys.stdout.write("Content-Type: text/html; charset=UTF-8\r\n\r\n")
    sys.stdout.write(body)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
