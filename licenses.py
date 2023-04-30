import json
import tkinter as tk
import subprocess

def show():
    # Tkinterウィンドウの作成
    root = tk.Tk()
    root.title("ライセンス一覧")
    root.geometry("400x340")

    def show_my_license():
        with open("LICENSE", "r") as f:
            text = f.read()
            show_license("soundgrep", text)
            f.close()

    # 選択されたアイテムに対応するライセンス本文を表示する関数
    def show_license(licence_title: str, license_text: str):
        license_window = tk.Toplevel(frame)
        license_window.title(licence_title)

        # テキストボックスの作成と配置
        text_box = tk.Text(license_window, wrap=tk.WORD)
        text_box.pack(fill=tk.BOTH, expand=True)

        # テキストボックスにライセンス本文を表示
        text_box.insert(tk.END, license_text)

    # soundgrepのライセンス情報作成
    frame3 = tk.Frame(root)
    frame3.pack(side=tk.TOP, padx=3, pady=3, anchor="w")

    # ラベルの作成と配置
    label = tk.Label(frame3, text="soundgrep", font=("Helvetica", 14))
    label.pack(side=tk.LEFT, padx=10)
    label = tk.Label(frame3, text=" v.0.1.0")
    label.pack(side=tk.LEFT)

    frame4 = tk.Frame(root)
    frame4.pack(side=tk.TOP, padx=3, pady=3, anchor="n")

    # ラベルの作成と配置
    label = tk.Label(frame4, text="このアプリは'HoppingGanon'が作成したクソアプリです。\nライセンスは'GNU GENERAL PUBLIC LICENSE Version 3'です。", wraplength=350, anchor="w")
    label.pack(side=tk.TOP)

    # soundgrepのライセンス情報作成
    frame2 = tk.Frame(root)
    frame2.pack(side=tk.TOP, padx=3, pady=3, anchor="n")

    # ボタンの作成と配置
    button = tk.Button(frame2, text="ライセンスファイルを開く", command=show_my_license)
    button.pack(side=tk.TOP)

    # リストボックスの作成
    frame = tk.Frame(root)
    frame.pack(side=tk.TOP, padx=3, pady=3, anchor="n")

    listbox = tk.Listbox(frame, width=60)
    listbox.pack(pady=5)

    # JSONファイルからライセンス情報を読み込む
    with open("./licenses.json") as f:
        licenses = json.load(f)

    # "licenses"の中身をリストで表現
    license_list = [f"{license['Name']} {license['Version']}" for license in licenses]

    # リストボックスにライセンス一覧を表示
    for license in license_list:
        listbox.insert(tk.END, license)

    def show_external_license():
        if 0 < len(listbox.curselection()):
            index = listbox.curselection()[0]
            license_text = licenses[index]["LicenseText"]
            licence_title = license_list[index]
            show_license(licence_title, license_text)

    # ボタンの作成と配置
    button = tk.Button(frame, text="ライセンスファイルを開く", command=show_external_license)
    button.pack()


    # Tkinterウィンドウの実行
    root.mainloop()

if __name__ == "__main__":
    show()
