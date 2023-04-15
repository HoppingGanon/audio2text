import os
import subprocess
import wave
import json
import vosk
import tkinter as tk
from tkinter import filedialog, messagebox
import random
import string
import json

def generate_filename(parent_dir, filename_length):
    while True:
        # ランダムなファイル名を生成
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for i in range(filename_length))
        filename = random_string + '.json' # 拡張子も含める
        
        # 同じ名前のファイルが存在するか確認
        full_name = os.path.join(parent_dir, filename)
        if not os.path.isfile(full_name):
            return full_name

def get_ffmpeg_path():
    fmpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
    if os.path.isfile(fmpath):
        return fmpath

    for p in os.environ["PATH"].split(";"):
        fmpath = os.path.join(p, "ffmpeg.exe")
        if os.path.isfile(fmpath):
            return fmpath
    return ""


def get_text_wav(filePath, model):
    # 音声ファイルの読み込み
    wf = wave.open(filePath, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        messagebox("警告", "入力可能な音声ファイルはMP3ファイルまたはモノラルリニアPCMのWAVサウンドのみです")
        return

    # VOSKでの音声認識
    rec = vosk.KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    # 認識結果をfinal_resultsに追加
    result = json.loads(rec.FinalResult())

    wf.close()
    print(f"'{filePath}'の解析を完了しました")
    return result


def convert_to_wav(fullname, name, output_folder_path, ffmpeg_path):
    wav_file_path = os.path.join(output_folder_path, f"{name}.wav")

    subprocess.call([ffmpeg_path, "-i", fullname, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-loglevel", "quiet", "-y", wav_file_path])

    return wav_file_path


class TextResult():
    path: str
    obj: any

    def __init__(self) -> None:
        self.path = ""
        self.obj = {}
        pass


def get_text(dirName, filename, model, ffmpeg_path) -> TextResult:
    r = TextResult()
    lower = filename.lower()
    if lower.endswith(".mp3") or lower.endswith(".wav") or lower.endswith(".aac"):
        mp3_file_path = os.path.join(dirName, filename).replace("\\", "/")
        output_folder_path = os.path.join(os.environ["LOCALAPPDATA"], "HoppingGanon", "audio2text", "cache").replace("\\", "/")

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        wav_file_path = convert_to_wav(mp3_file_path, filename, output_folder_path, ffmpeg_path)
        r.path = mp3_file_path
        r.obj = get_text_wav(wav_file_path, model)

        os.remove(wav_file_path)

    return r

def get_json_name(folder_path, target_path):
    """
    指定されたフォルダ内にある全てのJSONファイルを読み込み、
    キー"path"が空白かどうかをチェックして結果を返す
    folder_path: フォルダのパス
    """

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # フォルダ内の全てのファイル名を取得し、JSONファイルだけを抽出する
    files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1] == ".json"]

    # 各JSONファイルを読み込んで、キー"path"が空白かどうかをチェックする
    for filename in files:
        filepath = os.path.join(folder_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("root") == target_path:
                return filepath.replace("\\", "/")
            
    return generate_filename(folder_path, 16).replace("\\", "/")

def analyze():
    ffmpeg_path = get_ffmpeg_path()

    if ffmpeg_path == "":
        messagebox.showwarning("警告", "ffmpeg.exeがありません。ffmpeg.exeをこのスクリプトと同じディレクトリに配置するか、環境変数PATHを通してください。ffmpegは外部のサイトからダウンロードする必要があります。")
        return

    # フォルダを開くダイアログを表示して、選択されたフォルダをrootDirに代入する
    root = tk.Tk()
    root.withdraw()
    root_dir = filedialog.askdirectory(title="検索対象のフォルダを指定")

    json_path = get_json_name((os.path.join(os.environ["LOCALAPPDATA"], "HoppingGanon", "audio2text", "database")), root_dir)

    if root_dir == "":
        return

    # スクリプトと同じディレクトリにあるモデルを読み込む
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
    if not os.path.exists(model_path):
        messagebox.showwarning("警告", "モデルフォルダが見つかりません。モデルをダウンロードして配置してください。")
        return
    model = vosk.Model(model_path)

    # 認識結果を格納する辞書を初期化
    final_results = {}

    # 再帰的に検索
    for dirName, _, fileList in os.walk(root_dir):
        for filename in fileList:
            r = get_text(dirName, filename, model, ffmpeg_path)
            if r.path != "":
                final_results[r.path] = r.obj

    # final_resultsをJSONファイルとして出力
    json_obj = {}
    json_obj["root"] = root_dir
    json_obj["data"] = final_results

    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(json_obj, ensure_ascii=False))
        f.close()


if __name__ == '__main__':
    analyze()