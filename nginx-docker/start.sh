#!/usr/bin/env bash
# --- コンテナのエントリポイント ---
# 1. cgi-bin配下のCGIスクリプトに実行権限を付与する (root)
# 2. Nginxの実行時ディレクトリを作成し、権限を落とす先のユーザーに所有権を渡す (root)
# 3. fcgiwrap を起動 (NginxからのFastCGIリクエストをCGIとして実行する。プロセス自体は${USER_NAME}に権限を落とす)
# 4. Nginx を起動 (静的ファイル配信 + /cgi-bin/ を fcgiwrap へFastCGI中継。workerプロセスは${USER_NAME}に権限を落とす)
# 5. コンテナを起動し続けるため無限ループで待機する
#
# 実行時のカレントディレクトリは Dockerfile の WORKDIR (= ${VOLUME} のマウント先) と一致する。
#
# 補足: このstart.sh自体、およびWORKDIR(Nginxのhtml/config一式)は
#       ホームディレクトリ(/home/${USER_NAME})配下ではなく /${ENTRY_DIR} 直下に配置している。
#       個人用の権限モデル(ホームディレクトリ)とサービス実行に必要な権限を分離するため。
#
# --- 実行ユーザーの方針(root起動 → 権限降格) ---
#
# | 項目 | 実行ユーザー | 理由 |
# | --- | --- | --- |
# | start.sh本体(このスクリプト) | root(Dockerfileで`USER`を指定していないため) | ボリュームマウントされた`cgi-bin`配下は所有者がホスト側に依存するため、非rootだと`chmod`が"Operation not permitted"になる |
# | fcgiwrap(CGI実行プロセス) | ${USER_NAME} | `spawn-fcgi`の`-u`/`-g`オプションで、ソケットのbind後に権限を落として起動する |
# | Nginx workerプロセス | ${USER_NAME} | `nginx`起動時に`-g "user ${USER_NAME};"`を渡し、masterプロセスの起動後にworkerプロセスの権限を落とす |
#
# --- 旧構成(libcgipy自作サーバー)からの変更点 ---
#
# | 項目 | 旧構成 | 新構成 |
# | --- | --- | --- |
# | CGI実行サーバー | `python3 -m httpcgi.http_cgi`(自作) | `fcgiwrap`(標準ツール) |
# | Nginxとの連携方式 | `proxy_pass`(HTTPリバースプロキシ) | `fastcgi_pass`(FastCGI) |
# | HTTPメソッド対応 | GETのみ(POSTにバグあり) | GET/POSTともに動作 |

set -eu

# --- 権限を落とす先のユーザー (DockerfileでENV化された${USER_NAME}を利用) ---
readonly APP_USER="${USER_NAME}"

# --- パス設定 (WORKDIRからの絶対パスに変換しておく) ---
readonly NGINX_PREFIX="$(pwd)/nginx"
readonly NGINX_HTML="${NGINX_PREFIX}/html"
readonly CGI_BIN_DIR="${NGINX_HTML}/cgi-bin"

# --- fcgiwrap の待受アドレス (nginx.conf の fastcgi_pass と合わせること) ---
readonly FCGI_HOST="127.0.0.1"
readonly FCGI_PORT="9001"

# --- Nginxが書き込みに使う実行時ディレクトリを用意 ---
# (linux_dataはボリュームマウントのため、イメージビルド時ではなくここで作成する)
# nginx.conf内の *_temp_path で指定した各ディレクトリを全て作成しておく
mkdir -p \
    "${NGINX_PREFIX}/run/tmp/client_body" \
    "${NGINX_PREFIX}/run/tmp/proxy" \
    "${NGINX_PREFIX}/run/tmp/fastcgi" \
    "${NGINX_PREFIX}/run/tmp/uwsgi" \
    "${NGINX_PREFIX}/run/tmp/scgi"

# --- 上記ディレクトリの所有者を${APP_USER}に変更 ---
# (このディレクトリはroot(このスクリプト)が作成するが、実際に書き込むのは
#  権限降格後の${APP_USER}で動くNginx workerプロセスのため、事前に所有権を渡しておく)
chown -R "${APP_USER}:${APP_USER}" "${NGINX_PREFIX}/run"

# --- cgi-bin直下のCGIスクリプトに実行権限を付与 ---
# (linux_dataはボリュームマウントのため、イメージビルド時ではなくここで付与する。
#  fcgiwrap は対象ファイルに実行権限が無いと "Permission denied" になる)
find "${CGI_BIN_DIR}" -maxdepth 1 -type f -name '*.py' -exec chmod +x {} +

# --- fcgiwrap をバックグラウンドで起動 ---
# spawn-fcgi が fcgiwrap プロセスを起動し、TCPソケット(127.0.0.1:9001)で待受ける
# -F 5      : リクエストを並行処理できるよう fcgiwrap を5プロセス起動する
# -u/-g     : ソケットのbind後、fcgiwrapプロセス自体は${APP_USER}へ権限を落として起動する
#             (spawn-fcgi自身はrootのまま実行されるが、fork後の子プロセス(fcgiwrap)がsetuid/setgidされる)
spawn-fcgi \
    -a "${FCGI_HOST}" \
    -p "${FCGI_PORT}" \
    -F 5 \
    -u "${APP_USER}" \
    -g "${APP_USER}" \
    -- /usr/sbin/fcgiwrap

# --- Nginxを起動 ---
# 既定でデーモン化してバックグラウンドで動作するため、続けて待機処理に入る
# -g "user ${APP_USER};" : nginx.conf側では実行ユーザーを指定していないため、
#                          コマンドラインから追加のグローバルディレクティブとして指定する。
#                          これによりmasterプロセスはrootのまま起動しつつ、
#                          workerプロセス(実際にリクエストを処理する側)は${APP_USER}に権限を落として動作する。
nginx -p "${NGINX_PREFIX}" -c "${NGINX_PREFIX}/config/nginx.conf" -g "user ${APP_USER};"

# --- コンテナを起動し続ける ---
while true; do
    sleep 1000
done
