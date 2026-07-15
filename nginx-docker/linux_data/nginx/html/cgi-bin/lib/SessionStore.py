"""
### SessionStore.py

Cookie で受け渡す「セッションID(ランダムトークン)」と、サーバー側に保持する
認証情報(ユーザー名・パスワード)を紐付けて管理するための簡易セッションストア。

ファイルシステム上にセッションごとの JSON ファイルを保存する

本番運用では Redis 等の利用を推奨
"""

import os
import json
import time
import secrets


class SessionStore:
    """
    ### SessionStore クラス

    セッションID をキーとして、認証情報をサーバー側の一時ファイルに
    保存・読込・削除するためのクラス。

    | 使用例 | 説明 |
    | --- | --- |
    | `store = SessionStore()` | 既定のディレクトリ(`/tmp/mysqlcgi_sessions`)を使う |
    | `sid = store.create(user, password)` | 新しいセッションを作成しIDを取得する |
    | `store.load(sid)` | セッションIDから認証情報を取得する |
    | `store.delete(sid)` | セッションを破棄する |
    """

    def __init__(self, directory="/tmp/mysqlcgi_sessions", ttl_seconds=1800):
        """
        #### コンストラクタ

        保存先ディレクトリが存在しない場合は作成する
        (他ユーザーから読めないよう `0700` で作成)。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `directory` | `str` | セッションファイルを保存するディレクトリ(既定`/tmp/mysqlcgi_sessions`) |
        | `ttl_seconds` | `int` | セッションの有効期限・秒(既定`1800` = 30分) |
        """
        self.directory = directory
        self.ttl_seconds = ttl_seconds
        os.makedirs(self.directory, mode=0o700, exist_ok=True)

    def _path(self, session_id):
        """
        #### セッションIDに対応するファイルパスを取得する

        パストラバーサル対策として、`session_id` は
        `secrets.token_hex` が生成する16進数文字列のみを許可する。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `session_id` | `str | None` | 検証したいセッションID |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `str | None` | `str` | セッションファイルの絶対パス(不正なIDの場合は`None`) |
        """
        if not session_id or not all(c in "0123456789abcdef" for c in session_id):
            return None
        return os.path.join(self.directory, f"{session_id}.json")

    def create(self, user, password):
        """
        #### 新しいセッションを作成する

        暗号学的に安全なランダムなセッションIDを生成し、
        認証情報(`user`/`password`)を紐付けてファイルへ保存する。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `user` | `str` | 認証済みのDBユーザー名 |
        | `password` | `str` | 認証に使用したパスワード |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `str` | `str` | 発行したセッションID(Cookieの値として使用する) |
        """
        session_id = secrets.token_hex(32)
        path = self._path(session_id)
        with open(path, "w", encoding="UTF-8") as f:
            json.dump({"user": user, "password": password, "created": time.time()}, f)
        os.chmod(path, 0o600)
        return session_id

    def load(self, session_id):
        """
        #### セッションIDから認証情報を取得する

        存在しない・不正な形式・期限切れのセッションIDに対しては
        `None` を返す(期限切れの場合はファイルも削除する)。

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `session_id` | `str | None` | 取得したいセッションID |

        | 戻り値 | 型 | 説明 |
        | --- | --- | --- |
        | `dict | None` | `dict` | `{"user": str, "password": str}`(取得失敗時は`None`) |
        """
        path = self._path(session_id)
        if not path or not os.path.isfile(path):
            return None

        try:
            with open(path, "r", encoding="UTF-8") as f:
                data = json.load(f)
        except Exception:
            return None

        if time.time() - data.get("created", 0) > self.ttl_seconds:
            self.delete(session_id)
            return None

        return {"user": data.get("user"), "password": data.get("password")}

    def delete(self, session_id):
        """
        #### セッションを破棄する

        | 引数 | 型 | 説明 |
        | --- | --- | --- |
        | `session_id` | `str | None` | 破棄したいセッションID |
        """
        path = self._path(session_id)
        if path and os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
