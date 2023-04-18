import json
from tkinter import filedialog

class Context:
    def __init__(self) -> None:
        self.text = ""
    text: str

def open_json(path: str = ""):
    if path == "":
        path = filedialog.askopenfilename()

    if path == "":
        data = {}
        data["data"] = {}
        return "", data
    
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return path, data

if __name__ == '__main__':
    print(open_json())
