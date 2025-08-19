from flask import Flask, request, jsonify
import numpy as np
from ScreamDetention import ScreamDetector
from KeywordDetection import KeywordDetector
from KeywordManagement import Keyword_Manager

app = Flask(__name__)

# サーバー起動時に一度だけインスタンスを生成
print("Initializing detectors and managers...")
scream_detector = ScreamDetector()
keyword_detector = KeywordDetector()
keyword_manager = Keyword_Manager()
print("Initialization complete. Server is ready.")

# 設計書で定められたサンプリングレート
# YAMNet (Scream) と Whisper (Keyword) は共に16000Hzを期待する
EXPECTED_SAMPLE_RATE = 16000

@app.route('/detect/scream', methods=['POST'])
def detect_scream():
    """悲鳴検知エンドポイント"""
    try:
        # Rawバイナリデータを取得
        audio_data_raw = request.data
        # np.frombufferでNumPy配列に変換 (16bit整数として)
        audio_data_np = np.frombuffer(audio_data_raw, dtype=np.int16)
        # float32に正規化
        audio_data_float = audio_data_np.astype(np.float32) / 32768.0

        # 悲鳴検知を実行
        is_scream, confidence = scream_detector.detect(audio_data_float, EXPECTED_SAMPLE_RATE)
        top_classes = scream_detector.get_top_classes(audio_data_float, EXPECTED_SAMPLE_RATE)

        response = {
            "scream_detected": bool(is_scream),
            "confidence": float(confidence),
            "top_classes": top_classes
        }
        return jsonify(response)

    except Exception as e:
        print(f"Error in /detect/scream: {e}")
        return jsonify({"error": "An error occurred during scream detection."}), 500

@app.route('/detect/keyword', methods=['POST'])
def detect_keyword():
    """合言葉検知エンドポイント"""
    try:
        # Rawバイナリデータを取得
        audio_data_raw = request.data
        # np.frombufferでNumPy配列に変換 (16bit整数として)
        audio_data_np = np.frombuffer(audio_data_raw, dtype=np.int16)
        # float32に正規化
        audio_data_float = audio_data_np.astype(np.float32) / 32768.0

        # 合言葉検知を実行
        detected, recognized_text, matched_keyword = keyword_detector.detect(audio_data_float, keyword_manager)

        response = {
            "keyword_detected": bool(detected),
            "recognized_text": recognized_text,
            "matched_keyword": matched_keyword
        }
        return jsonify(response)

    except Exception as e:
        print(f"Error in /detect/keyword: {e}")
        return jsonify({"error": "An error occurred during keyword detection."}), 500

@app.route('/keywords', methods=['GET'])
def get_keywords():
    """登録済み合言葉リスト取得エンドポイント"""
    try:
        keywords = keyword_manager.get_keyword()
        return jsonify({"keywords": keywords})
    except Exception as e:
        print(f"Error in GET /keywords: {e}")
        return jsonify({"error": "Could not retrieve keywords."}), 500

@app.route('/keywords', methods=['POST'])
def add_keyword():
    """合言葉登録エンドポイント"""
    try:
        return keyword_manager.register()
    except Exception as e:
        print(f"Error in POST /keywords: {e}")
        return jsonify({"error": "An error occurred while adding the keyword."}), 500

@app.route('/keywords/<string:keyword_text>', methods=['DELETE'])
def delete_keyword(keyword_text):
    """合言葉削除エンドポイント"""
    try:
        success = keyword_manager.delete(keyword_text)
        if success:
            return jsonify({"status": "success", "message": f"合言葉「{keyword_text}」を削除しました。"})
        else:
            return jsonify({"status": "error", "message": f"合言葉「{keyword_text}」が見つかりませんでした。"}), 404
    except Exception as e:
        print(f"Error in DELETE /keywords/{keyword_text}: {e}")
        return jsonify({"error": "An error occurred while deleting the keyword."}), 500

if __name__ == '__main__':
    # 外部からアクセス可能にするために host='0.0.0.0' を指定
    app.run(host='0.0.0.0', port=5000, debug=True)