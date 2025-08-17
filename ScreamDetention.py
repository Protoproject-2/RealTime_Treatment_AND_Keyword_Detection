import tensorflow_hub as hub
import numpy as np
import csv
import tensorflow as tf

class ScreamDetector:
    """YAMNetモデルを保持し、悲鳴検知を実行するクラス"""
    def __init__(self):
        print("ScreamDetectorを初期化中")

        # YAMNetモデルのロード
        print("YAMNetモデルをロードしている")
        yamnet_model_handle = "https://tfhub.dev/google/yamnet/1"
        self.model = hub.KerasLayer(yamnet_model_handle)

        # YAMNetが分類するクラス名リストをロード
        class_map_path = "yamnet_class_map.csv"
        self.class_names = []
        with open(class_map_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # ヘッダー行をスキップ
            for row in reader:
                self.class_names.append(row[2])
        print("初期化完了 悲鳴検知準備OK")

    def detect(self, audio_data: np.ndarray, sample_rate: int) -> tuple[bool, float]:
        """
        音声データから悲鳴を検知する。
        戻り値：（悲鳴が検知されたか, 信頼度スコア）
        """
        # 失敗条件処理
        if sample_rate != 16000:
            print(f"エラー：YAMNetは16000Hzのサンプリングレートを使用するが{sample_rate}Hzが与えられました。")
            return False, 0.0
        
        # YAMNetモデルに音声データを入力、モデルは521種類のそれぞれの音に対する「出現確率」をスコアとして返す
        scores, embeddings, spectrogram = self.model(audio_data)
        scores_np = scores.numpy()

        # YAMNetは非常に短い間隔でスコアを算出するから受け取った音声チャンク全体の平均スコアを計算して安定した判定結果を得る
        mean_scores = np.mean(scores_np, axis=0)

        # numpyのargsortを使ってスコアが高い順に並べ替え、上位5つの音のインデックスを取得
        top_n = 5
        # np.argsort(.) -> 全521個のスコアを並び替え、そのインデックスを返す
        # [::-1]        -> 並び替えたインデックスを逆順（降順）にする
        # [:top_n]      -> 降順にしたインデックスの先頭5つを取得する
        top_class_indices = np.argsort(mean_scores)[::-1][:top_n]

        is_scream_detected = False
        scream_confidence = 0.0

        print(f"[悲鳴検知] トップ{top_n}の解析結果：")
        for i in top_class_indices:
            class_name = self.class_names[i]
            score = mean_scores[i]
            print(f"- {class_name}: {score:.4f}")
            if "Scream" in class_name:
                is_scream_detected = True
                scream_confidence = score
        
        return is_scream_detected, scream_confidence
