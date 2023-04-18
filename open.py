import os
import json
import tkinter as tk

class Context:
    def __init__(self) -> None:
        self.text = ""
    text: str

def pick_json():
    # フォーム作成用関数
    def open_file():
        # 「開く」ボタンが押された際に実行する関数
        selected_index = listbox.curselection()
        if selected_index:
            # リストボックスで選択されているインデックスから対応するJSONファイルのフルパスを取得する
            filename = listbox.get(selected_index[0])
            context.text = os.path.join(folder_path, filename).replace("\\", "/")
        root.destroy()

    def quit():
        context.text = ""
        root.destroy()


    context = Context()
    # フォルダパスの指定
    folder_path = os.path.join(os.environ["LOCALAPPDATA"], "HoppingGanon", "audio2text", "database").replace("\\", "/")
    # フォルダ内のJSONファイルの一覧を取得する
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    # JSONファイルから"name"インデックスの値を取得してリストボックスに表示する
    names = []
    for file in json_files:
        with open(os.path.join(folder_path, file), encoding="utf-8") as f:
            data = json.load(f)
            name = data["name"]
            names.append(name)

    root = tk.Tk()
    root.title("Open File")
    root.geometry("320x200")

    root.protocol("WM_DELETE_WINDOW", quit)

    # フレーム作成
    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack()

    # リストボックス作成
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
    for name in names:
        listbox.insert(tk.END, name)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    # ボタン作成
    button_frame = tk.Frame(root)
    button_frame.pack()
    open_button = tk.Button(button_frame, text="開く", command=open_file)
    open_button.pack(side=tk.LEFT)
    close_button = tk.Button(button_frame, text="閉じる", command=quit)
    close_button.pack(side=tk.LEFT)

    root.mainloop()
    return context.text

if __name__ == '__main__':
    print(pick_json())