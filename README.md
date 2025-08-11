# リアルタイム合言葉検知システム

マイクからの音声をリアルタイムで認識し、あらかじめ登録されたキーワード（合言葉）を検知するPythonアプリケーション

## 主な機能

* マイクからの音声をリアルタイムで取得
* OpenAIのWhisperモデルを利用して音声認識
* `pykakasi`を用いた日本語の正規化（ひらがな化）によるキーワード照合の柔軟化
* プログラム内でのキーワードの登録・管理（いずれはユーザーがもっと自由に登録できるように）

## 動作環境

* Python 3.9 以上（自分の実環境は3.11.9で問題なく動いた）
* 必要なライブラリは `requirements.txt` に記載されています。

## 使い方

1.  **リポジトリをクローン**
    ```bash
    git clone [https://github.com/](https://github.com/)[あなたのユーザー名]/RealTime_Treatment_AND_Keyword_Detection.git
    cd RealTime_Treatment_AND_Keyword_Detection
    ```

2.  **仮想環境の作成と有効化**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    
    # Mac / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **必要なライブラリをインストール**
    ```bash
    pip install -r requirements.txt
    ```

4.  **プログラムの実行**
    ```bash
    python main.py
    ```
    マイクに向かって登録されたキーワード（デフォルトでは「こんにちはといえばよる」など）を話すと、検知してプログラムが終了します。

## 設定

いくつかの設定は `main.py` の中で直接変更できます。

* **キーワードの変更**: `manager.register("新しいキーワード")` のようにして、検知したいキーワードを追加・変更できます。
* **AIモデルの変更**: `detector = KeywordDetector(model_size="...")` の部分で、Whisperのモデルサイズ (`"tiny"`, `"small"`, `"medium"`, `"large"`) を変更できます。モデルが大きいほど精度が上がりますが、処理が重くなります。
* **検知単位の変更**: `CHUNK_SECONDS` の値を変更することで、一度に処理する音声の長さを調整できます。（例：CHUNK_SECONDS=5なら5秒間という意味）