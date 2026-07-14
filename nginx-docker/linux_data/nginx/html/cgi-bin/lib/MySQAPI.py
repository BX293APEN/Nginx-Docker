"""
### MySQAPI.py

`MySQLite.py`（SQLite用サンプル）を参考に、MySQL用へ書き換えたラッパーモジュール。
`mysql-connector-python` を用いてMySQLサーバーへ接続し、
SQL文の送受信を簡単に行えるようにする。
"""

import os
import mysql.connector


class MySQAPI():
    """
    ### MySQAPI クラス

    MySQLサーバーとの接続・SQL実行をまとめて扱うためのラッパークラス。
    `MySQLite` と同様に `with` 文（コンテキストマネージャ）での利用を想定している。

    | 使用例 | 説明 |
    | --- | --- |
    | `with MySQAPI() as db:` | 環境変数の接続情報でMySQLへ接続する |
    | `db.send_sql("SELECT 1;")` | SQL文を送信し、結果をタプル形式で取得する |
    """

    def __init__(
        self,
        host     = None,
        port     = None,
        user     = None,
        password = None,
        database = None,
    ):
        """
        #### コンストラクタ

        引数が指定されなかった項目は、対応する環境変数から値を取得する。
        （Docker Compose の `environment:` で渡される値を想定）

        | 引数 | 型 | 説明 | 未指定時に参照する環境変数 |
        | --- | --- | --- | --- |
        | `host` | `str` | 接続先ホスト名（MySQLコンテナ名など） | `DB_HOST` |
        | `port` | `int` | 接続先ポート番号 | `DB_PORT` |
        | `user` | `str` | 接続ユーザー名 | `DB_USER` |
        | `password` | `str` | 接続パスワード | `DB_PASSWORD` |
        | `database` | `str` | 使用するデータベース名 | `DB_NAME` |
        """
        self.databaseHost = mysql.connector.connect(
            host     = host     or os.environ.get("DB_HOST", "localhost"),
            port     = int(port or os.environ.get("DB_PORT", 3306)),
            user     = user     or os.environ.get("DB_USER", "root"),
            password = password or os.environ.get("DB_ROOT_PASSWORD", ""),
            database = database or os.environ.get("DB_NAME", ""),
        )  # データベースとの接続

    def __enter__(self):
        """
        #### `with` 文開始時の処理

        カーソルを生成し、自分自身を返す。

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `self` | `MySQAPI` | カーソル生成済みの自インスタンス |
        """
        self.database = self.databaseHost.cursor()  # カーソルを作る
        return self

    def send_sql(self, sql):
        """
        #### SQL文送信

        SQL文を実行してコミットしたうえで、実行結果を全て取得する。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `sql` | `str` | 実行するSQL文 |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `list[tuple]` | `list` | 実行結果を全て格納したタプルのリスト |
        """
        self.database.execute(sql)
        result = self.database.fetchall()  # タプル形式で全て取得 先にデータを読むこと
        self.db_commit()
        return result

    def db_commit(self):
        """
        #### コミット処理

        未コミットの変更をデータベースへ反映する。
        """
        self.databaseHost.commit()

    def __exit__(self, *args):
        """
        #### `with` 文終了時の処理

        コミットしたうえで、カーソルと接続をクローズする。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `*args` | `tuple` | 例外情報（type, value, traceback）。正常終了時は全て `None` |
        """
        self.db_commit()
        self.database.close()
        self.databaseHost.close()
