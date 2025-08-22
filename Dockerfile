# Python 3.11のスリムなDebian(Linux)
FROM python:3.11-slim

# コンテナ内の /app フォルダに移動し、以降のコマンドはここが基準になる
WORKDIR /app

# 必要なファイルをコンテナにコピー
COPY requirements.txt .


# PyAudio/音声処理ライブラリのビルドに必要な依存を追加
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    libsndfile1 \
    libsoxr0 \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# requirements.txt をUTF-8に正規化（BOMやUTF-16対策）
RUN python - <<'PY'
from pathlib import Path
p = Path('requirements.txt')
b = p.read_bytes()
for enc in ('utf-8','utf-8-sig','utf-16','utf-16le','utf-16be'):
    try:
        s = b.decode(enc).replace('\r\n','\n').replace('\r','\n')
        p.write_text(s, encoding='utf-8')
        break
    except Exception:
        pass
else:
    raise SystemExit('could not decode requirements.txt')
PY

RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードを全てコピーする
COPY . .

# PORT 5000は高記述すればいいのかな？
EXPOSE 5000

# Waitressサーバーを起動するコマンド
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]