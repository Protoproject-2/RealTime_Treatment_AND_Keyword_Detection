from pykakasi import kakasi
import whisper
from KeywordManagement import Keyword_Manager
import numpy as np
import os

class KeywordDetector:
    """音声認識モデルと各種ツールを保持し、キーワード検知を実行するクラス"""
    def __init__(self, model_size="small"):
        # 初期化時にモデルや変換器のロードを一度だけ行う
        print("KeywordDetectorを初期化中...")

        # キャッシュディレクトリを指定
        cache_dir = ".cache/whisper"
        print(f"whisperのキャッシュディレクトリを設定した：{os.path.abspath(cache_dir)}")

        # Whisperモデルのロード時にキャッシュの場所(download_root)を指定
        print(f"Whisperモデル({model_size})をロードしています...")
        self.model = whisper.load_model(model_size, download_root=cache_dir)
        
        # Kakasi（ひらがな変換器）の準備
        print("ひらがな変換器を準備しています...")
        kakasi_instance = kakasi()
        kakasi_instance.setMode("J", "H")
        kakasi_instance.setMode("K", "H")
        self.converter = kakasi_instance.getConverter()
        print("初期化完了。検知準備OKです。")

    def detect(self, audio_data: np.ndarray, manager: Keyword_Manager) -> bool:
        # 合言葉検知AI
        print("\n検知プロセス開始")

        try:
            # モデル、音声ファイルをロード、認識
            print("メモリ上の音声データを文字起こし中...")
            result = self.model.transcribe(audio_data, language="ja")
            recognized_text = result["text"]
            print(f"-> 認識結果: 「{recognized_text}」")
        except Exception as e:
            print(f"検知エラー：音声認識中にエラーが発生しました: {e}")
            return False
        
        # ここからひらがな化実行
        print("認識結果をひらがなに変換中...")
        normalized_text = self.converter.do(recognized_text)
        print(f"-> ひらがな化後: 「{normalized_text}」")

        # キーワード照合
        print("登録済みキーワードと照合中...")
        registered_keywords = manager.get_keyword()
        print(f"-> 照合対象リスト: {registered_keywords}")

        if not registered_keywords:
            # キーワード合致有無
            print("警告：照合するキーワードが登録されていません。")
            return False

        for keyword in registered_keywords:
            # 合言葉登録リストから今回検出した合言葉を照合
            if keyword in normalized_text:
                print(f"成功：合言葉「{keyword}」が見つかりました！")
                return True, recognized_text, keyword

        print("失敗：登録された合言葉は見つかりませんでした。")
        return False, recognized_text, None