from flask import request, jsonify

class Keyword_Manager:
    def __init__(self):
        # 合言葉保存用リスト初期化
        self.keyword_list = []


    def register(self):
        # Webリクエストから直接キーワードを登録する
        data = request.get_json()
        if not data or 'keyword' not in data:
            return jsonify({"status": "error", "message": "Request must be JSON with a 'keyword' field."}), 400

        keyword = data['keyword']
        
        if not keyword:
            # 空文字は登録できないようにする処理
            print("登録エラー：空文字は登録できません。")
            return jsonify({"status": "error", "message": "無効なキーワードです。"}), 400 # 400 Bad Requestがより適切
        
        if keyword in self.keyword_list:
            # 二重登録できないようにするための処理
            print(f"登録エラー：「{keyword}」はすでに登録済みです。")
            return jsonify({"status": "error", "message": f"合言葉「{keyword}」はすでに登録済みです。"}), 409 # 409 Conflictが適切
        
        # 登録処理
        self.keyword_list.append(keyword)
        print(f"成功：合言葉「{keyword}」を登録できました。")
        return jsonify({"status": "success", "message": f"合言葉「{keyword}」を登録しました。"})
    
    def delete(self, keyword:str) -> bool:
        # ここで合言葉を削除するメソッドを定義
        """ボタンを押されたときこのメソッドが呼ばれるようにしたいね"""

        if keyword in self.keyword_list:
            # 削除処理
            self.keyword_list.remove(keyword)
            print(f"成功：「{keyword}」を削除しました。")
            return True
        else:
            print(f"削除エラー：該当する「{keyword}」が見つかりません。")
            return False # 失敗時にFalseを返すように修正

    def change(self, old_keyword:str, new_keyword:str) -> bool:
        # ここで登録した合言葉を変更するメソッドを定義

        if not old_keyword in self.keyword_list:
            # 変更したい合言葉の特定不可処理
            print(f"変更エラー：変更したい「{old_keyword}」が見つかりません。")
            return False
        if new_keyword in self.keyword_list:
            # 二重登録っできないようにするための処理
            print(f"変更エラー：すでに「{new_keyword}」は登録済みです。")
            return False
        
        # 合言葉変更処理
        index = self.keyword_list.index(old_keyword)
        self.keyword_list[index] = new_keyword
        print(f"成功：「{old_keyword}」を「{new_keyword}」に変更しました。")
        return True

    def get_keyword(self) -> list:
        # 登録されている合言葉を確認するためのメソッド
        return self.keyword_list
