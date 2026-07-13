# FROM [イメージ] [タグ]
# Docker Hub (https://hub.docker.com/) 参照
FROM ubuntu:25.10

# 環境変数を docker-compose.yml から受け取る
ARG WS
ARG USER_NAME
ARG PASSWORD
ARG ENTRY_DIR
ARG ENTRY_POINT
ARG LANG

# 環境変数を設定
# 1000以上推奨
ENV USER_ID=1001
ENV GROUP_ID=1001

# RUN 命令はなるべく1つにまとめる
# コマンドが長くなる場合は \ で改行すること
# --- 追加したaptパッケージの用途 ---
#
# | パッケージ | 用途 |
# | --- | --- |
# | `nginx` | 静的ファイル配信 + `/cgi-bin/`配下をfcgiwrapへFastCGI中継 |
# | `fcgiwrap` | FastCGI(Nginx側) ⇔ CGI(標準入出力・環境変数)の変換ラッパー本体 |
# | `spawn-fcgi` | `fcgiwrap`をFastCGIプロセスとして起動・待受させるためのスポナー |
RUN apt update && \
    apt upgrade -y && \
    apt install -y \
    sudo nano iproute2 iputils-ping language-pack-ja \
    nginx fcgiwrap spawn-fcgi python3 python3-pip && \
    useradd -m -s /bin/bash -u ${USER_ID} ${USER_NAME} && \
    usermod -aG sudo ${USER_NAME} && \
    echo "root:${PASSWORD}" | chpasswd && \
    echo "${USER_NAME}:${PASSWORD}" | chpasswd && \
    mkdir -p /home/${USER_NAME}/${ENTRY_DIR} && \
    update-locale LANG=${LANG} && \
    pip install --break-system-packages \
    mysql-connector-python libcgipy
    # --- pipパッケージの用途 ---
    #
    # | パッケージ | 用途 |
    # | --- | --- |
    # | `mysql-connector-python` | `MySQAPI.py` がMySQLへ接続するために使用 |
    # | `libcgipy` | `main.py` が使用する`pycgi`(FieldStorage)・`pycgitb`(簡易ロガー)モジュールを提供(依存関係の`libcgi`経由で自動インストールされる) |
    #
    # 補足: 同梱の簡易CGIサーバー(`httpcgi`)はPOST処理にバグがあるため使用しない。
    #       CGI実行はfcgiwrap(Nginx → FastCGI → CGI変換)へ置き換えている。

COPY ${ENTRY_POINT} /home/${USER_NAME}/${ENTRY_DIR}/${ENTRY_POINT}
RUN chmod +x /home/${USER_NAME}/${ENTRY_DIR}/${ENTRY_POINT}

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}/${WS}

# 起動したら実行するコマンド
# 環境変数は使えないので注意
# ENTRYPOINT ["/Programs/start.sh"] 

# 起動したら実行するコマンド
# CMD ["/bin/bash", "-c", "while true; do sleep 1000; done"]
# 無限ループでbashを起動し続ける