import pyaudio
import numpy as np
# import matplotlib.pyplot as plt
import time
from Detection import KeywordDetector
from KeywordManagement import Keyword_Manager

if __name__ == "__main__":
    # 最初に一度だけモデルをロードする
    detector = KeywordDetector(model_size="medium")
    manager = Keyword_Manager()
    # テスト用の合言葉を登録
    manager.register("こんにちはといえばよる")
    manager.register("りんごをたべたいきぶん") # 複数登録も可能

    # --- 音声ストリームの基本的なパラメータ ---
    CHUNK_SECONDS = 5  # 区切る秒数 ★2秒に設定
    RATE = 16000  # サンプリングレート、whisperモデルが対応している16kHzに
    CHANNELS = 1  # モノラル
    FORMAT = pyaudio.paInt16  # 整数形式の方が扱いやすい
    CHUNK_SIZE = int(RATE * CHUNK_SECONDS)  # 2秒分のフレーム数を計算

    # PyAudioのインスタンスを作成
    p = pyaudio.PyAudio()

    # 音声ストリームを開く
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    """リアルタイム波形描画はシステムにおいては必要ないためコメントアウト"""
    # # --- 可視化の準備 ---
    # plt.ion()  # Matplotlibをインタラクティブモードに設定
    # fig, ax = plt.subplots()

    # # 横軸（時間）のデータを作成
    # time_axis = np.linspace(0, CHUNK_SECONDS, CHUNK_SIZE)
    # ax.set_xlabel("Time (s)")
    # ax.set_ylabel("Amplitude")
    # ax.set_ylim(-32768, 32767) # int16の範囲
    # line, = ax.plot(time_axis, np.zeros(CHUNK_SIZE))

    print(f"{CHUNK_SECONDS}秒ごとの音声入力を開始します。ウィンドウを閉じるかCtrl+Cで終了します。")

    try:
        while True:
            # 2秒分のデータをストリームから読み込む（処理が終わるまで待機）
            data_bytes = stream.read(CHUNK_SIZE)
            
            # 読み込んだバイトデータをNumpy配列に変換
            chunk_data_int16 = np.frombuffer(data_bytes, dtype=np.int16)
            
            # 1. Whisperのために、int16からfloat32にデータを変換
            audio_float32 = chunk_data_int16.astype(np.float32) / 32768.0

            # 2. 変換したデータを検知システムに渡す
            if detector.detect(audio_float32, manager):
                print("\n★★★ 合言葉を検知しました！ ★★★\n")
                break # 検知したらループを抜ける
            else:
                print("合言葉は検知されませんでした。")

            """リアルタイム波形描画は以下略"""
            # # グラフのデータを更新
            # line.set_ydata(chunk_data_int16)
            # fig.canvas.draw()
            # fig.canvas.flush_events()
            
    except (KeyboardInterrupt, SystemExit):
        print("プログラムを終了します。")

    finally:
        # ストリームを閉じる
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("ストリームをクリーンアップしました。")