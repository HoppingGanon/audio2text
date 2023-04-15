import os
import wave
import json
import vosk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# フォルダを開くダイアログを表示して、選択されたフォルダをrootDirに代入する
root = tk.Tk()
root.withdraw()
rootDir = filedialog.askdirectory()

# スクリプトと同じディレクトリにあるモデルを読み込む
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
if not os.path.exists(model_path):
    messagebox.showwarning("警告", "モデルフォルダが見つかりません。アプリケーションを終了します。")
    exit(1)
model = vosk.Model(model_path)

# 認識結果を格納する辞書を初期化
final_results = {}

# 再帰的に検索
for dirName, subdirList, fileList in os.walk(rootDir):
    for filename in fileList:
        # WAVファイルであれば処理を実行
        if filename.lower().endswith(".wav"):
            filePath = os.path.join(dirName, filename)

            # 音声ファイルの読み込み
            print(filePath)
            wf = wave.open(filePath, "rb")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                print ("Audio file must be WAV format mono PCM.")
                exit (1)

            # VOSKでの音声認識
            rec = vosk.KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)

            # 認識結果をfinal_resultsに追加
            result = json.loads(rec.FinalResult())["text"]
            final_results[filePath] = result
            print(result)

# final_resultsをJSONファイルとして出力
outPath = os.path.join(rootDir, "results.json")
with open(outPath, "w") as f:
    f.write(json.dumps(final_results, ensure_ascii=False))
