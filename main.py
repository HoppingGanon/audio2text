import os
import subprocess
import wave
import json
import vosk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

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
    result = json.loads(rec.FinalResult())
    return result


def convert_mp3_to_wav(fullname, name, output_folder_path, ffmpeg_path):
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
    # WAVファイルまたはMP3ファイルであれば処理を実行
    r = TextResult()

    if filename.lower().endswith(".wav"):
        filePath = os.path.join(dirName, filename).replace("\\", "/")
        r.path = filePath
        r.obj = get_text_wav(filePath, model)
    elif filename.lower().endswith(".mp3"):
        mp3_file_path = os.path.join(dirName, filename).replace("\\", "/")
        output_folder_path = os.path.join(os.environ["LOCALAPPDATA"], "HoppingGanon", "audio2text", "cache").replace("\\", "/")

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        wav_file_path = convert_mp3_to_wav(mp3_file_path, filename, output_folder_path, ffmpeg_path)
        r.path = mp3_file_path
        r.obj = get_text_wav(wav_file_path, model)

        os.remove(wav_file_path)

    return r


def main():
    ffmpeg_path = get_ffmpeg_path()

    if ffmpeg_path == "":
        messagebox.showwarning("警告", "ffmpeg.exeがありません。ffmpeg.exeをこのスクリプトと同じディレクトリに配置するか、環境変数PATHを通してください。ffmpegは外部のサイトからダウンロードする必要があります。")
        exit(1)

    # フォルダを開くダイアログを表示して、選択されたフォルダをrootDirに代入する
    root = tk.Tk()
    root.withdraw()
    rootDir = filedialog.askdirectory()

    if rootDir == "":
        exit(0)

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
            r = get_text(dirName, filename, model, ffmpeg_path)
            if r.path != "":
                final_results[r.path] = r.obj

    # final_resultsをJSONファイルとして出力
    outPath = os.path.join(rootDir, "results.json")
    with open(outPath, "w", encoding="utf-8") as f:
        f.write(json.dumps(final_results, ensure_ascii=False))
        f.close()


if __name__ == '__main__':
    main()
