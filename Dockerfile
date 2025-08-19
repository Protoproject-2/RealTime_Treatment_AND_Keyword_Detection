# Python 3.11のスリムなDebian(Linux)
FROM python:3.11-slim

# コンテナ内の /app フォルダに移動し、以降のコマンドはここが基準になる
WORKDIR /app

# 必要なファイルをコンテナにコピー
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードを全てコピーする
COPY . .

# PORT 5000は高記述すればいいのかな？
EXPOSE 5000

# Waitressサーバーを起動するコマンド
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]