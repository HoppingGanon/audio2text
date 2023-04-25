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
from pykakasi import kakasi
from pathlib import Path
from common import get_ffmpeg_path, get_ffprobe_path, load_settings, include_ext

# 読み方変換オブジェクトをインスタンス化
kakasi = kakasi()

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

def get_text_wav(org_path, path, model):
    # 音声ファイルの読み込み
    wf = wave.open(path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        messagebox("警告", "入力可能な音声ファイルはモノラル・リニアPCMのWAVサウンドのみです")
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
    print(f"'{org_path}'の解析を完了しました")
    return result


def convert_to_wav(fullname, name, output_folder_path, ffmpeg_path):
    wav_file_path = os.path.join(output_folder_path, f"{name}.wav")
    subprocess.call([ffmpeg_path, "-i", fullname, "-vn", "-acodec", "pcm_s16le", "-ar", "48000", "-ac", "1", "-loglevel", "quiet", "-y", wav_file_path])
    return wav_file_path


class TextResult():
    path: str
    obj: any
    duration: float

    def __init__(self) -> None:
        self.path = ""
        self.obj = {}
        self.duration = 0
        pass

def get_text(dirName, filename, model, ffmpeg_path, ffprobe_path, path_reduce_count, target_ext) -> TextResult:
    r = TextResult()
    lower = filename.lower()
    
    if include_ext(lower, target_ext):
        org_file_path = os.path.join(dirName, filename).replace("\\", "/")
        output_folder_path = os.path.join(os.environ["LOCALAPPDATA"], "HoppingGanon", "soundgrep", "cache").replace("\\", "/")

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        wav_file_path = convert_to_wav(org_file_path, filename, output_folder_path, ffmpeg_path)
        r.path = os.path.abspath(org_file_path)[path_reduce_count:]
        r.obj = get_text_wav(org_file_path, wav_file_path, model)
        r.duration = get_duration(ffprobe_path, wav_file_path)

        os.remove(wav_file_path)

    return r

def get_duration(ffprobe_path, path):
    result = subprocess.run([ffprobe_path, path, "-loglevel", "quiet", "-show_streams", "-print_format", "json"], capture_output=True, text=True)
    data = json.loads(result.stdout)

    duration = data["streams"][0]["duration"]
    try:
        return float(duration)
    except ValueError:
        return 0

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

def to_hiragana(text: str):
    # モードの設定：J(Kanji) to H(Hiragana)
    kakasi.setMode('J', 'H') 

    # 変換して出力
    conv = kakasi.getConverter()
    s = conv.do(text)

    kakasi.setMode('K', 'H') 
    conv = kakasi.getConverter()
    return conv.do(s)

def analyze(analyze_path: str = "", save_path: str = ""):
    settings = load_settings()

    ffmpeg_path = get_ffmpeg_path()
    ffprobe_path = get_ffprobe_path()

    if ffmpeg_path == "":
        messagebox.showwarning("警告", "ffmpeg.exeがありません。ffmpeg.exeをこのスクリプトと同じディレクトリに配置するか、環境変数PATHを通してください。ffmpegは外部のサイトからダウンロードする必要があります。")
        return ""

    # フォルダを開くダイアログを表示して、選択されたフォルダをrootDirに代入する
    root = tk.Tk()
    root.withdraw()

    if analyze_path == "":
        root_dir = filedialog.askdirectory(title="解析対象のフォルダを指定")
    else:
        root_dir = analyze_path

    if root_dir == "":
        return ""

    if save_path == "":
        loop_f = True
        while loop_f:
            json_path = filedialog.asksaveasfilename(
                title="プロジェクトファイル",
                initialdir=analyze_path,
                filetypes=[('プロジェクトファイル','*.json')],
                initialfile="project.json"
                )
            
            if json_path == "":
                loop_f = False
            elif Path(json_path).parent.resolve() != Path(root_dir).resolve():
                loop_f = not messagebox.askyesno("注意", "プロジェクトファイルは解析対象の直下に配置する必要があります。続行しますか？")
            else:
                loop_f = False
    else:
        json_path = save_path

    if json_path == "":
        return ""

    # スクリプトと同じディレクトリにあるモデルを読み込む
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
    if not os.path.exists(model_path):
        messagebox.showwarning("警告", "モデルフォルダが見つかりません。モデルをダウンロードして配置してください。")
        return ""
    model = vosk.Model(model_path)

    # 認識結果を格納する辞書を初期化
    final_results = []

    # 再帰的に検索
    for dirName, _, fileList in os.walk(root_dir):
        for filename in fileList:
            r = get_text(dirName, filename, model, ffmpeg_path, ffprobe_path, len(os.path.abspath(root_dir)) + 1, settings["target_ext"])
            if r.path != "":
                data = r.obj
                del data["text"]
                if "result" in data:
                    for result in data["result"]:
                        result["yomi"] = to_hiragana(result["word"])
                data["path"] = r.path
                data["duration"] = r.duration
                final_results.append(data)

    # final_resultsをJSONファイルとして出力
    json_obj = {}
    json_obj["data"] = final_results

    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(json_obj, ensure_ascii=False))
        f.close()

    return json_path

def clear_cache():
    cache_path = os.path.join(os.environ["LOCALAPPDATA"], "HoppingGanon", "soundgrep", "cache")
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    for filename in os.listdir(cache_path):
        file_path = os.path.join(cache_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

if __name__ == '__main__':
    analyze("", "")
