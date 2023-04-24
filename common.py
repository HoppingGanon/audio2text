import json
import os

def get_ffmpeg_path():
    fmpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
    if os.path.isfile(fmpath):
        return fmpath

    for p in os.environ["PATH"].split(";"):
        fmpath = os.path.join(p, "ffmpeg.exe")
        if os.path.isfile(fmpath):
            return fmpath
    return ""

def get_ffplay_path():
    fmpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffplay.exe")
    if os.path.isfile(fmpath):
        return fmpath

    for p in os.environ["PATH"].split(";"):
        fmpath = os.path.join(p, "ffplay.exe")
        if os.path.isfile(fmpath):
            return fmpath
    return ""

def get_ffprobe_path():
    fmpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffprobe.exe")
    if os.path.isfile(fmpath):
        return fmpath

    for p in os.environ["PATH"].split(";"):
        fmpath = os.path.join(p, "ffprobe.exe")
        if os.path.isfile(fmpath):
            return fmpath
    return ""

def create_command(main_command, path, start=-1, end=-1, pre_args = []):
    cmd = []
    cmd.append(main_command)
    cmd += pre_args
    if start >= 0:
        cmd.append("-ss")
        cmd.append(str(start))
    else:
        start = 0
    if end >= 0:
        cmd.append("-t")
        cmd.append(str(end - start))
    
    cmd.append("-i")
    cmd.append(path)

    return cmd

def load_json(path: str, default, create_new_file: bool):
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
                f.close()
                return d
    except:
        pass

    if create_new_file:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps(default, ensure_ascii=False))
        except:
            pass
    return default
    
def load_settings():
    data = {}
    data["target_ext"] = [".mp3", ".wav", ".aac", ".mp4", ".avi"]
    data["audio_bit_rate"] = "160k"
    data["audio_sampling_rate"] = "48000"
    data["additional_args"] = []
    return load_json("settings.json", data, True)

def include_ext(filename: str, ary: list):
    for s in ary:
        if filename.endswith(s):
            return True
    return False
