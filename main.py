import pyaudio
import numpy as np

# 最大サイズを指定でき、要素が最大数を超えると自動的に古いものから削除される効率的なデータ構造
# 合言葉検知用に過去5秒間のデータを保持
from collections import deque

from KeywordDetection import KeywordDetector
from ScreamDetention import ScreamDetector
from KeywordManagement import Keyword_Manager

if __name__ ==  "__main__":
    # モード設定（on/off）
    """合言葉検知のみモードを推奨, REST APIの仕様ではこのmain.py自体がバックエンド側に移行されるから
    このon/off機能は考慮せず消してしまっても構わないと思われる
    いずれそれぞれの機能のon/offボタンを作りたいが、データベースが必要となり工期が間に合わないのが現状(8/19時点)"""
    KEYWORD_DETECTION_MODE = True
    SCREAM_DETECTION_MODE = True 


    # 各システムの初期化
    if KEYWORD_DETECTION_MODE == True:
        keyword_detector = KeywordDetector(model_size="medium")
        keyword_manager = Keyword_Manager()
        keyword_manager.register("こんにちはといえばよる")
        keyword_manager.register("りんごをたべたいきぶん")

    if SCREAM_DETECTION_MODE == True:
        scream_detector = ScreamDetector()

    print("初期化完了")

    # リアルタイム音声処理の事前情報の定義
    SCREAM_CHUNK_SECONDS = 3
    KEYWORD_CHUNK_SECONDS = 5
    RATE = 16000
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    SCREAM_CHUNK_SIZE = int(RATE * SCREAM_CHUNK_SECONDS)
    # 合言葉検知用に過去五秒間の音声データを保持するためのバッファ（一時的なデータ置き場）作成
    audio_buffer = deque(maxlen=int(RATE * KEYWORD_CHUNK_SECONDS))

    p = pyaudio.PyAudio()
    # マイク入力から音声データを流すストリームの作成
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=SCREAM_CHUNK_SIZE
    )

    print("リアルタイム検知を開始します。Ctrl+Cで終了します。")
    print(f"合言葉検知：{'ON' if KEYWORD_DETECTION_MODE else 'OFF'}\n悲鳴検知：{'ON' if SCREAM_DETECTION_MODE else 'OFF'}")

    # メインループ
    try:
        loop_count = 0
        while True:
            data_bytes = stream.read(SCREAM_CHUNK_SIZE) # 3s分の音声データ（バイトデータ）
            chunk_data_int16 = np.frombuffer(data_bytes, dtype=np.int16)

            audio_float32 = chunk_data_int16.astype(np.float32) / 32768.0

            audio_buffer.extend(audio_float32) # 3s分の新しいデータを5s間データを保持するdequeバッファに追加

            print(f"ループ{loop_count+1}（音声取得：{SCREAM_CHUNK_SECONDS}秒）")

            # 悲鳴検知(毎3秒実行)
            if SCREAM_DETECTION_MODE:
                is_scream, score = scream_detector.detect(audio_float32, RATE)
                if is_scream:
                    print(f"悲鳴を検知しました（信頼度{score:.2f}）")
                else:
                    print("悲鳴は検知されませんでした")
            
            # 合言葉検知(毎5秒実行)
            if KEYWORD_DETECTION_MODE and len(audio_buffer) == audio_buffer.maxlen:
                keyword_audio_data = np.array(audio_buffer)

                if keyword_detector.detect(keyword_audio_data, keyword_manager):
                    print("合言葉を検知しました")
                else:
                    print("合言葉は検知されませんでした")
                
            loop_count += 1

    except (KeyboardInterrupt, SystemExit):
        print("\nプログラムを終了する")
    
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("ストリームをクリーンアップしました")



