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

def create_command(main_command, path, start=-1, end=-1):
    cmd = []
    cmd.append(main_command)
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