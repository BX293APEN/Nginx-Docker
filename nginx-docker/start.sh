#!/usr/bin/env bash

set -eu

# アプリを実行するユーザ (DockerfileでENV化された${USER_NAME})
readonly APP_USER="${USER_NAME}"

# パス設定 (絶対パス指定)
readonly NGINX_PREFIX="$(pwd)/nginx"
readonly NGINX_HTML="${NGINX_PREFIX}/html"
readonly CGI_BIN_DIR="${NGINX_HTML}/cgi-bin"

# fcgiwrap の待受アドレス (nginx.conf の fastcgi_pass と合わせること)
readonly FCGI_HOST="127.0.0.1"
readonly FCGI_PORT="9001"

# Nginxが書き込みに使う実行時ディレクトリを用意 & 所有者変更
mkdir -p \
    "${NGINX_PREFIX}/run/tmp/client_body" \
    "${NGINX_PREFIX}/run/tmp/proxy" \
    "${NGINX_PREFIX}/run/tmp/fastcgi" \
    "${NGINX_PREFIX}/run/tmp/uwsgi" \
    "${NGINX_PREFIX}/run/tmp/scgi"

chown -R "${APP_USER}:${APP_USER}" "${NGINX_PREFIX}/run"

# cgi-bin直下のCGIスクリプトに実行権限を付与
find "${CGI_BIN_DIR}" -maxdepth 1 -type f -name '*.py' -exec chmod +x {} +

# fcgiwrap をバックグラウンドで起動
spawn-fcgi \
    -a "${FCGI_HOST}" \
    -p "${FCGI_PORT}" \
    -F 5  \
    -u "${APP_USER}" \
    -g "${APP_USER}" \
    -- /usr/sbin/fcgiwrap

# Nginxを起動
nginx -p "${NGINX_PREFIX}" -c "${NGINX_PREFIX}/config/nginx.conf" -g "user ${APP_USER};"

# --- コンテナを起動し続ける ---
while true; do
    sleep 1000
done
