#!/usr/bin/env bash
# --- コンテナのエントリポイント ---
# 1. libcgipy による CGI 実行用HTTPサーバーを起動 (cgi-bin/main.py を実行する)
# 2. Nginx を起動 (静的ファイル配信 + /cgi-bin/ へのリバースプロキシ)
# 3. コンテナを起動し続けるため無限ループで待機する
#
# 実行時のカレントディレクトリは Dockerfile の WORKDIR (= ${VOLUME} のマウント先) と一致する。

set -eu

# --- パス設定 (WORKDIRからの絶対パスに変換しておく) ---
readonly NGINX_PREFIX="$(pwd)/nginx"
readonly NGINX_HTML="${NGINX_PREFIX}/html"

# --- Nginxが書き込みに使う実行時ディレクトリを用意 ---
# (linux_dataはボリュームマウントのため、イメージビルド時ではなくここで作成する)
# nginx.conf内の *_temp_path で指定した各ディレクトリを全て作成しておく
mkdir -p \
    "${NGINX_PREFIX}/run/tmp/client_body" \
    "${NGINX_PREFIX}/run/tmp/proxy" \
    "${NGINX_PREFIX}/run/tmp/fastcgi" \
    "${NGINX_PREFIX}/run/tmp/uwsgi" \
    "${NGINX_PREFIX}/run/tmp/scgi"

# --- CGI(libcgipy)サーバーをバックグラウンドで起動 ---
# html配下に移動してから起動することで、/cgi-bin/以下のスクリプトを
# 正しいパスで解決できるようにする(既定で 0.0.0.0:8000 で待受ける)
( cd "${NGINX_HTML}" && exec python3 -m httpcgi.http_cgi ) &

# --- Nginxを起動 ---
# 既定でデーモン化してバックグラウンドで動作するため、続けて待機処理に入る
nginx -p "${NGINX_PREFIX}" -c "${NGINX_PREFIX}/config/nginx.conf"

# --- コンテナを起動し続ける ---
while true; do
    sleep 1000
done
