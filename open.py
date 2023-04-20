import json
from tkinter import filedialog

class Context:
    def __init__(self) -> None:
        self.text = ""
    text: str

def open_json(path: str = ""):
    if path == "":
        path = filedialog.askopenfilename(title="プロジェクトを開く", filetypes=[('プロジェクトファイル','*.json')])

    if path == "":
        data = {}
        data["data"] = {}
        return "", data
    
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
        f.close()
    
    text_sb = []
    yomi_sb = []

    for d in data["data"]:
        text_sb.clear()
        yomi_sb.clear()
        for r in d["result"]:
            text_sb.append(r["word"])
            yomi_sb.append(r["yomi"])
        d["text"] = "".join(text_sb).replace(" ", "")
        d["yomi"] = "".join(yomi_sb).replace(" ", "")
        d["is_text"] = True
        d["start"] = -1
        d["end"] = -1
    return path, data

if __name__ == '__main__':
    print(open_json())
