# Nginx-Docker
- Docker上でNginx CGI DBを簡易的に連携させるプロジェクト

## 実行手順
1. `docker compose up --build -d`
1. [アクセス](http://localhost:3000)

## 必要パッケージ

| パッケージ | 用途 |
| --- | --- |
| `nginx` | 静的ファイル配信 + `/cgi-bin/`配下をfcgiwrapへFastCGI中継 |
| `fcgiwrap` | FastCGI(Nginx側) ⇔ CGI(標準入出力・環境変数)の変換ラッパー本体 |
| `spawn-fcgi` | `fcgiwrap`をFastCGIプロセスとして起動・待受させるためのスポナー |
| `mysql-connector-python` | `MySQAPI.py` がMySQLへ接続するために使用 |
| `libcgipy` | `main.py` が使用する`pycgi`(FieldStorage)・`pycgitb`(簡易ロガー)モジュールを提供(依存関係の`libcgi`経由で自動インストールされる) |

## 処理内容
1. cgi-bin配下のCGIスクリプトに実行権限を付与する (root)
2. Nginxの実行時ディレクトリを作成し、権限を落とす先のユーザーに所有権を渡す (root)
3. fcgiwrap を起動 : NginxからのFastCGIリクエストをCGIとして実行する (${USER_NAME})
4. Nginx を起動 : 静的ファイル配信 + /cgi-bin/ を fcgiwrap へFastCGI中継 (${USER_NAME})
5. コンテナを起動し続けるため無限ループで待機する


## FastCGI

```bash
spawn-fcgi \
    -a "${FCGI_HOST}" \
    -p "${FCGI_PORT}" \
    -F 5  \
    -u "${APP_USER}" \
    -g "${APP_USER}" \
    -- /usr/sbin/fcgiwrap
```

| 引数 | 内容 |
| --- | --- |
| -a "${FCGI_HOST}" | ホスト名指定 (`${FCGI_HOST}` : `127.0.0.1`) |
| -p "${FCGI_PORT}" | ポート指定 (`${FCGI_PORT}` : `9001`) |
| -F 5 | fcgiwrap並行処理プロセス数 (5プロセス) |
| -u | FastCGI プロセスの所有ユーザ指定 |
| -g | FastCGI プロセスの所有グループ指定 |

## Nginx の設定

| 項目 | 内容 | 説明 |
| --- | --- | --- |
| worker_processes | auto | CPUコア数から自動的に使用プロセス数を決定 |
| pid | run/nginx.pid | PIDファイルの出力先を指定 `/${ENTRY_DIR}/${WS}/nginx/run/nginx.pid` |
| error_log | run/error.log | エラーログの出力先 `/${ENTRY_DIR}/${WS}/nginx/run/error.log` |
| worker_connections | 1024 | 1プロセス当たり接続できる最大接続数 |
| http | - | 実機ではsites-availableからincludeして自動的にhttpブロック内に入っていたが、Dockerでイチから構築しているため、httpブロックを書く必要がある |
| access_log | run/access.log | アクセス履歴 `/${ENTRY_DIR}/${WS}/nginx/run/access.log` |
| client_body_temp_path | run/tmp/client_body | 巨大なデータを受け取る際に使用するファイル `/${ENTRY_DIR}/${WS}/nginx/run/tmp/client_body` |
| proxy_temp_path       | run/tmp/proxy | リバースプロキシ用ファイル `/${ENTRY_DIR}/${WS}/nginx/run/tmp/proxy` |
| fastcgi_temp_path     | run/tmp/fastcgi | CGIスクリプト用ファイル `/${ENTRY_DIR}/${WS}/nginx/run/tmp/fastcgi` |
| uwsgi_temp_path       | run/tmp/uwsgi | uWSGIを使う際のファイル `/${ENTRY_DIR}/${WS}/nginx/run/tmp/uwsgi` |
| scgi_temp_path        | run/tmp/scgi | SCGIを使う際のファイル `/${ENTRY_DIR}/${WS}/nginx/run/tmp/scgi` |

### location設定

`location ~ ^/cgi-bin/[^/]+\.py$`

| 項目 | 内容 |
| --- | --- |
| `~` | 正規表現宣言 |
| `^` | 行頭の場合 : 行頭宣言 |
| `/cgi-bin/` | /cgi-bin/ |
| `(A\|B\|C\|D)` | `A`又は`B`又は`C`又は`D` |
| `[ ]+` | `[ ]`内の表現にマッチする文字列が1文字以上 |
| `[^/]+` | `/`を除く文字列が1文字以上 |
|　`\` | エスケープ |
| `$` | 末尾 |