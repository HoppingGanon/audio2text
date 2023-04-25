import os
import subprocess
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from analyze import analyze, clear_cache
import convert
from open import open_json
from common import create_command, get_ffplay_path, get_ffmpeg_path, get_ffprobe_path, load_settings
from pathlib import Path
import re

class SearchForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # キャッシュのクリア
        clear_cache()

        self.ffmpeg_path = get_ffmpeg_path()
        self.ffplay_path = get_ffplay_path()
        self.ffprobe_path = get_ffprobe_path()
        if self.ffmpeg_path == "" or self.ffplay_path == "" or self.ffprobe_path == "":
            messagebox.showwarning("警告", "必要なファイルがありません。ffmpeg.exe, ffplay.exe, ffprobe.exeをこのスクリプトと同じディレクトリに配置するか、環境変数PATHを通してください。ffmpegは外部のサイトからダウンロードする必要があります。")
            return
        
        self.settings = load_settings()

        self.search_results = []

        # ウィンドウの設定
        self.master = master
        self.master.title("audio2text")
        self.master.geometry("500x400")

        # ウィンドウの x ボタンが押された時に呼ばれるメソッドを設定
        self.master.protocol("WM_DELETE_WINDOW", self.click_close)

        # メニューバーの作成
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新規プロジェクト", command=self.create_project)  # 新規解析コマンドを追加
        file_menu.add_command(label="プロジェクトを開く", command=self.open_data_file)  # 解析データを開くコマンドを追加
        file_menu.add_command(label="プロジェクトの保存(未実装)")  # 解析データを開くコマンドを追加
        file_menu.add_command(label="プロジェクトの上書き(未実装)")  # 解析データを開くコマンドを追加
        menubar.add_cascade(label="ファイル", menu=file_menu)
        self.master.config(menu=menubar)

        # チェックボックスの作成 ----------------------------
        self.check_frame = tk.Frame(self)
        self.check_frame.pack(side=tk.TOP, padx=3, pady=3, anchor="w")

        self.disp_fname_val = tk.BooleanVar()
        self.disp_fname_val.set(True)
        self.disp_fname = tk.Checkbutton(self.check_frame, text="ファイル名を表示", variable=self.disp_fname_val)
        self.disp_fname.pack(side=tk.LEFT)
        
        self.search_target = tk.IntVar()
        self.search_target.set(0)

        self.disp_text = tk.Radiobutton(self.check_frame, text="文字列検索", value=0, variable=self.search_target)
        self.disp_text.pack(side=tk.LEFT)
        self.disp_kana = tk.Radiobutton(self.check_frame, text="よみがな検索", value=1, variable=self.search_target)
        self.disp_kana.pack(side=tk.LEFT)

        # 検索フレームの作成 ----------------------------
        self.search_frame = tk.Frame(self, relief="solid")
        self.search_frame.pack(side=tk.TOP, padx=3, pady=5, anchor="w", fill=tk.BOTH, expand=True)
        # ラベルの作成
        self.label = tk.Label(self.search_frame, text="Search:")
        self.label.pack(side=tk.LEFT)
        # エントリーの作成
        self.entry = tk.Entry(self.search_frame)
        self.entry.pack(side=tk.LEFT, padx=2, fill = tk.X, expand=True)
        self.entry.bind("<Return>", self.search)

        # 検索ボタンの作成
        self.button = tk.Button(self.search_frame, text="検索", command=self.search)
        self.button.pack(side=tk.RIGHT, padx=5)

        # 検索結果のページ選択用フレームの作成 ----------------------------
        self.page_frame = tk.Frame(self)
        self.page_frame.pack(side=tk.TOP, padx=3, pady=10, anchor="ne")

        # 1ページ当たりの表示数
        self.per_page = 100
        self.page = 0

        # ページのコンボボックスを作成
        self.page_selector = ttk.Combobox(self.page_frame, state="readonly", values=['設定なし'])
        self.page_selector.pack(side=tk.RIGHT, padx=5)
        self.page_selector.set("設定なし")

        # データの定義 ----------------------------
        self.project_path = ""
        self.json_data = {}
        self.json_data["data"] = []

        # キャンバスの作成 ----------------------------
        self.canvas = tk.Canvas(self, bg="white", height=300, width=450, scrollregion=(0, 0, 500, 600))

        # スクロールイベントの設定
        self.canvas.bind("<Configure>", self.on_configure)
        self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)

        self.create_result_frame()
        self.canvas.pack(side="left", fill="both", expand=True)

        # 検索結果の配列
        self.result_data = []
        self.display_data = []

        # 再生処理
        self.playing_process = None

        self.update_canvas(450)

    def update_page_selector(self):
        self.page_selector.destroy()
        pages = []

        page_max = int((len(self.result_data) - 1) / self.per_page) + 1
        for i in range(page_max):
            from_ = i * self.per_page + 1
            if i == page_max - 1:
                to = len(self.result_data)
            else:
                to = (i + 1) * self.per_page
            item = f"{str(from_)}～{str(to)}件目"
            pages.append(item)
        
        self.page_selector = ttk.Combobox(self.page_frame, state="readonly", values=pages)
        self.page_selector.set(pages[0])
        self.page_selector.pack(side=tk.RIGHT, padx=5)
        self.page_selector.bind("<<ComboboxSelected>>", self.change_page)

    def change_page(self, *args):
        self.stop(None)
        self.page = self.page_selector.current()
        self.create_result()
        self.create_display()
    
    def create_result_frame(self):
        # キャンバスの作成
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self.result_frame = tk.Frame(self.canvas, bg="white")

        # キャンバスの表示設定
        self.canvas.create_window((0, 0), window=self.result_frame, anchor="nw")

    # 解析データを開くコマンドの関数
    def open_data_file(self):
        path, obj = open_json()
        if path != "":
            self.project_path = path
            self.json_data = obj
            self.set_all_result()
            self.create_display()
            self.update_canvas()
            self.update_page_selector()

    # 新規解析コマンドの関数
    def create_project(self):
        path = analyze()
        if path != "":
            path2, obj = open_json(path)
            if path2 != "":
                self.project_path = path2
                self.json_data = obj
                self.set_all_result()
                self.create_display()
                self.update_canvas()
                self.update_page_selector()
                print("解析が完了しました")
                messagebox.showinfo("完了", "解析が完了しました")

    def update_canvas(self, width = 0):
        if width == 0:
            width = self.canvas.winfo_width() - 33

        self.scrollbar.destroy()
        self.result_frame.destroy()

        self.create_result_frame()

        if width == 0:
            return

        # フレーム内にグリッドレイアウトを作成
        for i, data in enumerate(self.display_data):
            r = i*4
            self.result_frame.rowconfigure(r, weight=1)
            self.result_frame.columnconfigure(1, weight=1)
            actions_frame=tk.Frame(self.result_frame)
            actions_frame.grid(row=r, column=1, columnspan=2, pady=5, sticky="ew")
            
            button = tk.Button(actions_frame, text="再生", name=f"play_button_{i}")
            button.bind("<ButtonPress>", self.play_all)
            button.pack(side=tk.LEFT, padx=2)
            if data["start"] >= 0 and data["end"] >= 0:
                button = tk.Button(actions_frame, text="部分再生", name=f"play_part_button_{i}")
                button.bind("<ButtonPress>", self.play_part)
                button.pack(side=tk.LEFT, padx=2)
            
            button = tk.Button(actions_frame, text="停止", name=f"stop_button_{i}")
            button.bind("<ButtonPress>", self.stop)
            button.pack(side=tk.LEFT, padx=2)

            button = tk.Button(actions_frame, text="編集(未実装)")
            button.pack(side=tk.LEFT, padx=2)
            
            button = tk.Button(actions_frame, text="抽出", name=f"save_button_{i}")
            button.bind("<ButtonRelease>", self.save)
            button.pack(side=tk.LEFT, padx=2)
            
            r = i*4+1
            if self.disp_fname_val.get():
                self.result_frame.rowconfigure(r, weight=1)
                self.result_frame.columnconfigure(1, weight=1)
                label = tk.Label(self.result_frame, text="ファイル名", wraplength=100, anchor="w", background="#E0F0FF")
                label.grid(row=r, column=1, padx=1, pady=1, sticky=tk.EW)
                label = tk.Label(self.result_frame, text=data["path"], wraplength=width - 120, anchor="w", background="#F0F7FF")
                label.grid(row=r, column=2, padx=1, pady=1, sticky=tk.EW)

            r = i*4+2
            if self.search_target.get() == 0:
                self.result_frame.rowconfigure(r, weight=1)
                self.result_frame.columnconfigure(1, weight=1)
                label = tk.Label(self.result_frame, text="テキスト", wraplength=100, anchor="w", background="#E0F0FF")
                label.grid(row=r, column=1, padx=1, pady=1, sticky=tk.EW)
                label = tk.Label(self.result_frame, text=data["text"], wraplength=width - 120, anchor="w", background="#F0F7FF")
                label.grid(row=r, column=2, padx=1, pady=1, sticky=tk.EW)

            r = i*4+3
            
            if self.search_target.get() == 1:
                self.result_frame.rowconfigure(r, weight=1)
                self.result_frame.columnconfigure(1, weight=1)
                label = tk.Label(self.result_frame, text="読み仮名", wraplength=100, anchor="w", background="#E0F0FF")
                label.grid(row=r, column=1, padx=1, pady=1, sticky=tk.EW)
                label = tk.Label(self.result_frame, text=data["yomi"], wraplength=width - 120, anchor="w", background="#F0F7FF")
                label.grid(row=r, column=2, padx=1, pady=1, sticky=tk.EW)

        # スクロールバーの再設定
        self.canvas.update()
        self.on_configure(None)
        self.canvas.yview_moveto(0)

    def on_configure(self, event):
        # キャンバスのフレームとウィンドウサイズを合わせる
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def mouse_scroll(self, event):
        # スクロールイベントでキャンバスをスクロール
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def set_all_result(self):
        for index, data in enumerate(self.json_data["data"]):
            self.result_data.append(data)

    def search(self, event = None):
        # 検索ボタンが押された時に呼ばれる関数
        self.stop(None)
        self.create_result()
        self.create_display()
        self.update_page_selector()

    def create_display(self):
        self.display_data.clear()
        for index, data in enumerate(self.result_data):
            if self.page * self.per_page <= index < (self.page + 1) * self.per_page:
                self.display_data.append(data)

        self.update_idletasks()
        self.update_canvas()

    def create_result(self):
        prefix_count = 20
        suffix_count = 20

        self.result_data.clear()
        pattern = self.entry.get()
        
        if pattern == "":
            self.set_all_result()
        else:
            for json_index, data in enumerate(self.json_data["data"]):
                target = ""
                is_text = self.search_target.get() == 0
                target: str = ""
                if is_text:
                    target = data["text"]
                else:
                    target = data["yomi"]

                path: str = data["path"]

                loop = True

                base_position = 0
                while loop:
                    # textから検索
                    m = re.search(pattern, target)
                    if m is None:
                        break

                    start = m.start()
                    end = m.end()
                    start2 = max(start - prefix_count, 0)
                    length = len(target)
                    end2 = min(end + suffix_count, length)

                    # 前後の文を含める
                    result_text = target[start2:end2]
                    if 0 != start2:
                        result_text = "... " + result_text
                    if length != end2:
                        result_text = result_text + " ..."

                    target = target[end+1:]

                    result = {}
                    result["path"] = path
                    if is_text:
                        result["text"] = result_text
                        result["yomi"] = ""
                    else:
                        result["text"] = ""
                        result["yomi"] = result_text
                    
                    result["is_text"] = is_text
                    result["start"] = start + base_position
                    result["end"] = end + base_position
                    result["json_index"] = json_index
                    self.result_data.append(result)

                    base_position += end + 1


    def play_all(self, event):
        index = int(event.widget._name[len("play_button_"):])
        r_path = self.display_data[index]["path"]
        d = str(Path(self.project_path).parent)
        fullpath = os.path.join(d, r_path)
        self.ffplay(fullpath)

    def get_part_time(self, data):
        is_text = data["is_text"]
        start = data["start"]
        end = data["end"]
        json_index = data["json_index"]
        json_data = self.json_data["data"][json_index]

        if start < 0 or end < 0:
            return 0, data["duration"]

        cnt = 0
        start_index = 0
        for r in json_data["result"]:
            if is_text:
                cnt += len(r["word"])
            else:
                cnt += len(r["yomi"])
            if start < cnt:
                break
            start_index += 1
        
        cnt = 0
        end_index = 0
        for r in json_data["result"]:
            if is_text:
                cnt += len(r["word"])
            else:
                cnt += len(r["yomi"])
            if end <= cnt:
                break
            end_index += 1
        
        # 有効な文字列の長さが0だった場合の処理
        if start_index == -1 or end_index == -1:
            return -1, -1
        
        start_sec = json_data["result"][start_index]["start"]
        end_sec = json_data["result"][end_index]["end"]

        return start_sec, end_sec

    def play_part(self, event):
        start_index = int(event.widget._name[len("play_part_button_"):])
        data = self.display_data[start_index]
        r_path = data["path"]
        d = str(Path(self.project_path).parent)
        fullpath = os.path.join(d, r_path)
        start_sec, end_sec = self.get_part_time(data)
        self.ffplay(fullpath, start_sec - 0.75, end_sec + 0.75)
    
    def stop(self, event):
        if self.is_playing():
            self.playing_process.kill()
    
    def is_playing(self):
        return (not self.playing_process is None) and self.playing_process.poll() is None
    
    def save(self, event):
        self.stop(None)
        start_index = int(event.widget._name[len("save_button_"):])
        data = self.display_data[start_index]
        r_path = data["path"]
        d = str(Path(self.project_path).parent)
        fullpath = os.path.join(d, r_path)
        json_index = data["json_index"]
        json_data = self.json_data["data"][json_index]
        duration = json_data["duration"]
        start_sec, end_sec = self.get_part_time(data)
        convert.show(0, duration, start_sec, end_sec, fullpath)
        return

    def ffplay(self, path, start=-1, end=-1):
        # 再生中なら強制停止
        if self.is_playing():
            self.stop(None)
            time.sleep(0.15)

        cmd = create_command(self.ffplay_path, path, start, end)
        cmd.append("-vn")
        cmd.append("-showmode")
        cmd.append("0")
        cmd.append("-autoexit")

        self.playing_process = subprocess.Popen(cmd)

    def click_close(self):
        self.stop(None)
        if messagebox.askokcancel("確認", "終了しますか？"):
            clear_cache()
            self.master.destroy()
            self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    form = SearchForm(master=root)
    form.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
