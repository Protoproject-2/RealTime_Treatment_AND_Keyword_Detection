

## リアルタイム検知システムAPI化 設計まとめ

### 1\. プロジェクト目標

現在のリアルタイム音声処理スクリプトを、外部アプリケーション（スマートフォンアプリなど）から利用可能なバックグラウンドシステム（REST API）として再構築する。

### 2\. 決定したアーキテクチャ

| 項目 | 決定事項 | 備考 |
| :--- | :--- | :--- |
| **APIフレームワーク** | **Flask** | シンプルで学習しやすく、実績が豊富。 |
| **音声データ送信形式** | **Rawバイナリ形式** | データサイズと実装の容易さのバランスが良く、モバイル環境に適している。 |
| **レスポンスデータ形式**| **JSON** | Web APIにおける標準的なデータ交換形式。 |

\<br\>

### 3\. APIエンドポイント設計

サーバーは以下のエンドポイント（機能の窓口）を提供する。

#### `/detect/scream`

  * **HTTPメソッド**: `POST`
  * **説明**: 悲鳴検知を実行する。
  * **リクエスト**:
      * **ボディ**: 音声データ（Rawバイナリ形式）
      * **ヘッダー**: `Content-Type: audio/wav` または `application/octet-stream`
  * **レスポンス (成功時)**:
    ```json
    {
      "scream_detected": true,
      "confidence": 0.85,
      "top_classes": [
        {"class_name": "Screaming", "score": 0.85},
        {"class_name": "Speech", "score": 0.12},
        {"class_name": "Yell", "score": 0.09}
      ]
    }
    ```

#### `/detect/keyword`

  * **HTTPメソッド**: `POST`
  * **説明**: 合言葉検知を実行する。
  * **リクエスト**:
      * **ボディ**: 音声データ（Rawバイナリ形式）
      * **ヘッダー**: `Content-Type: audio/wav` または `application/octet-stream`
  * **レスポンス (成功時)**:
    ```json
    {
      "keyword_detected": true,
      "recognized_text": "こんにちはといえばよるですね",
      "matched_keyword": "こんにちはといえばよる"
    }
    ```

#### `/keywords`

  * **HTTPメソッド**: `GET`

  * **説明**: 現在登録されている全ての合言葉リストを取得する。

  * **レスポンス**:

    ```json
    {
      "keywords": ["こんにちはといえばよる", "りんごをたべたいきぶん"]
    }
    ```

  * **HTTPメソッド**: `POST`

  * **説明**: 新しい合言葉を登録する。

  * **リクエスト**:

    ```json
    {
      "keyword": "新しい合言葉"
    }
    ```

  * **レスポンス**:

    ```json
    {
      "status": "success",
      "message": "合言葉「新しい合言葉」を登録しました。"
    }
    ```

#### `/keywords/{keyword_text}`

  * **HTTPメソッド**: `DELETE`
  * **説明**: 指定された合言葉を削除する。
  * **レスポンス**:
    ```json
    {
      "status": "success",
      "message": "合言葉「{keyword_text}」を削除しました。"
    }
    ```

### 4\. 実装方針

  * **`KeywordDetection.py`, `ScreamDetection.py`, `KeywordManagement.py`**:

      * これらのファイル内のAIモデルやロジックは、APIからのデータを受け取れるように微調整する可能性があるが、**中心的な処理はほぼそのまま再利用する。**

  * **`main.py` -\> `app.py` (新規作成)**:

      * Flaskアプリケーションを起動するメインファイルとして、`app.py`を新たに作成する。
      * サーバー起動時に、`KeywordDetector`と`ScreamDetector`のインスタンスを**一度だけ**生成し、グローバル変数として保持する。
      * 上記で設計した各エンドポイントに対応するルート（例: `@app.route('/detect/scream', methods=['POST'])`）を作成する。
      * 各ルート関数内で、リクエストからRawバイナリデータを取得し、`np.frombuffer()`でNumPy配列に変換後、対応するDetectorの`.detect()`メソッドに渡す。
      * Detectorからの返り値を基に、指定されたJSON形式でレスポンスを生成してクライアントに返す。

  * **クライアント (例: スマホアプリ)**:

      * マイクから指定秒数（3秒または5秒）の音声を録音する。
      * 録音したデータをRawバイナリ形式のまま、対応するAPIエンドポイントに`POST`リクエストで送信する。
      * サーバーからのJSONレスポンスを受け取り、結果に応じてアプリの動作を制御する。