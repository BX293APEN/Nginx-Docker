#!/usr/bin/env bash
# --- コンテナのエントリポイント ---
# 1. cgi-bin配下のCGIスクリプトに実行権限を付与する
# 2. fcgiwrap を起動 (NginxからのFastCGIリクエストをCGIとして実行する)
# 3. Nginx を起動 (静的ファイル配信 + /cgi-bin/ を fcgiwrap へFastCGI中継)
# 4. コンテナを起動し続けるため無限ループで待機する
#
# 実行時のカレントディレクトリは Dockerfile の WORKDIR (= ${VOLUME} のマウント先) と一致する。
#
# --- 旧構成(libcgipy自作サーバー)からの変更点 ---
#
# | 項目 | 旧構成 | 新構成 |
# | --- | --- | --- |
# | CGI実行サーバー | `python3 -m httpcgi.http_cgi`(自作) | `fcgiwrap`(標準ツール) |
# | Nginxとの連携方式 | `proxy_pass`(HTTPリバースプロキシ) | `fastcgi_pass`(FastCGI) |
# | HTTPメソッド対応 | GETのみ(POSTにバグあり) | GET/POSTともに動作 |

set -eu

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

# --- cgi-bin直下のCGIスクリプトに実行権限を付与 ---
# (linux_dataはボリュームマウントのため、イメージビルド時ではなくここで付与する。
#  fcgiwrap は対象ファイルに実行権限が無いと "Permission denied" になる)
find "${CGI_BIN_DIR}" -maxdepth 1 -type f -name '*.py' -exec chmod +x {} +

# --- fcgiwrap をバックグラウンドで起動 ---
# spawn-fcgi が fcgiwrap プロセスを起動し、TCPソケット(127.0.0.1:9001)で待受ける
# -F 5 : リクエストを並行処理できるよう fcgiwrap を5プロセス起動する
spawn-fcgi \
    -a "${FCGI_HOST}" \
    -p "${FCGI_PORT}" \
    -F 5 \
    -- /usr/sbin/fcgiwrap

# --- Nginxを起動 ---
# 既定でデーモン化してバックグラウンドで動作するため、続けて待機処理に入る
nginx -p "${NGINX_PREFIX}" -c "${NGINX_PREFIX}/config/nginx.conf"

# --- コンテナを起動し続ける ---
while true; do
    sleep 1000
done
