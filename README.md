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
    .\.venv\Scripts\Activate.ps1
    # 終わらせたいときは
    deactivate
    
    
    # Mac / Linux
    python3 -m venv .venv
    source .venv/bin/activate
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
* **AIモデルの変更**: `detector = KeywordDetector(model_size="...")` の部分で、Whisperのモデルサイズ (`"tiny"`, `"small"`, `"medium"`, `"large"`) を変更できます。モデルが大きいほど精度が上がりますが、処理が重くなります。（例：mediumモデルで約1.4GB、制度とサイズの兼ね合いからこれがいい気もする）
* **検知単位の変更**: `CHUNK_SECONDS` の値を変更することで、一度に処理する音声の長さを調整できます。（例：CHUNK_SECONDS=5なら5秒間という意味）

## コード解説  
1.  **main.py**
    * RATE = 16000：サンプリングレートであり、音を16000回/sデータ化するという意味。whisperモデルが学習に使った標準的な値で、合わせることで精度、効率が上がる
    * FORMAT：サンプルフォーマット。音の振幅を16bit整数（-32768~32767）で表現する
    * stream = p.open(...)：pyaudioライブラリで最も重要なメソッド。ユーザーのマイク入力からそれをデータ化して音声データを流す「ストリーム」を作成
    * try/except->finally：ctrl+cの中断があっても必ずfinallyの終了処理が実行されるようになっている
    * data_bytes = stream.read(CHUNK_SIZE)：ストリームから指定されたチャンクサイズ分の音声データが貯まるまでプログラムの実行を一時停止して待つ。返すデータはバイナリデータ
    * chunk_data_int16 = np.frombuffer(data_bytes, dtype=np.int16)：numpyメソッド。バイトデータを指定したデータ型（np.int16）の数値配列に変換する。
    * audio_float32 = chunk_data_int16.astype(np.float32) / 32768.0：whisperが求める-1.0~1.0までの範囲に収まるように音声データの数値を正規化している
    * finallyブロック：マイクをOSに返すための処理。ただ将来的にはこうではなく合言葉検知が成功しても、バックグラウンドで検知を回し続けられるようにしたいなと思っている

2.  **Detection.py**
    * self.model = whisper.load_model(model_size)：whisperライブラリの関数。指定されたモデルをPCのメモリに一度だけロードする（main.pyを複数動かしても最初の一回以降はロードされた状態で始まるから安心して）
        **detectメソッド**
        * result = self.model.transcrobe(audio_data, language="ja")：whisperの最も重要なモデル。音声データ（audio_data）を受け取り、文字に起こす。
        * recognized_text = result["text"]：transcribeが返した辞書データからtextキーを指定して、文字お越しされた文字列本体を取り出している。
        * normalized_text = self.converter.do(recognized_text)：認識された文字列をすべて平仮名に変換する（ここ正味もしかしたらwhisperのみでできるのではないだろうかと思っている）

