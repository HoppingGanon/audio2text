import tkinter as tk

class Converter(tk.Frame):
    def __init__(self, master, start_limit: float, end_limit: float, init_start: float, init_end: int, ffmpeg_path: str, path: str):
        super().__init__(master)
        self.master = master
        self.is_changing = False
        self.start_limit = start_limit
        self.end_limit = end_limit
        self.start_val = tk.DoubleVar(value=init_start)
        self.end_val = tk.DoubleVar(value=init_end)
        self.ffmpeg_path = ffmpeg_path
        self.path = path
        self.create_widgets()

    def create_widgets(self):
        # フォーム全体
        self.master.geometry("480x180")

        # 開始位置スライダーとエントリー
        self.start_label = tk.Label(self.master, text="開始位置")
        self.start_label.grid(row=0, column=0, padx=5, pady=10)

        self.start_slider = tk.Scale(self.master, from_=self.start_limit, to=self.end_limit, resolution=0.01, orient=tk.HORIZONTAL, variable=self.start_val, command=self.update_start_entry_from_slider, cursor='sb_h_double_arrow')
        self.start_slider.grid(row=0, column=1, sticky="ew")

        self.start_entry_val = tk.StringVar(value=str(self.start_val.get()))
        self.start_entry = tk.Entry(self.master, textvariable=self.start_entry_val)
        self.start_entry.grid(row=0, column=2, padx=5, sticky="ew")

        # 終了位置スライダーとエントリー
        self.end_label = tk.Label(self.master, text="終了位置")
        self.end_label.grid(row=1, column=0, padx=5, pady=10)

        self.end_slider = tk.Scale(self.master, from_=self.start_limit, to=self.end_limit, resolution=0.01, orient=tk.HORIZONTAL, variable=self.end_val, command=self.update_end_entry_from_slider, cursor='sb_h_double_arrow')
        self.end_slider.grid(row=1, column=1, sticky="ew")

        self.end_entry_val = tk.StringVar(value=str(self.end_val.get()))
        self.end_entry = tk.Entry(self.master, textvariable=self.end_entry_val)
        self.end_entry.grid(row=1, column=2, padx=5, sticky="ew")

        # バインドの設定
        self.start_val.trace("w", self.update_start_slider_from_entry)
        self.end_val.trace("w", self.update_end_slider_from_entry)
        self.start_slider.bind("<B1-Motion>", self.update_start_entry_from_slider)
        self.end_slider.bind("<B1-Motion>", self.update_end_entry_from_slider)

        # ボタンのフォーム
        self.button_frame = tk.Frame(self.master)
        self.button_frame.grid(row=2, column=2, pady=10)

        # 抽出ボタン
        self.extract_button = tk.Button(self.button_frame, text="抽出", command=self.extract)
        self.extract_button.pack(side=tk.LEFT)

        # キャンセルボタン
        self.cancel_button = tk.Button(self.button_frame, text="キャンセル", command=self.master.quit)
        self.cancel_button.pack(side=tk.RIGHT)

        # 外側の余白を増やす
        for i in range(3):
            self.master.grid_rowconfigure(i, weight=1)
        
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=3, minsize=200)
        self.master.grid_columnconfigure(2, weight=1)

    def update_start_slider_from_entry(self, *args):
        if self.is_changing:
            return
        
        self.is_changing = True
        if not str.isnumeric(self.start_entry_val.get()):
            self.is_changing = False
            return
        
        start_entry_val = float(self.start_entry_val.get())
        self.start_slider.set(start_entry_val)
        
        self.is_changing = False

    def update_end_slider_from_entry(self, *args):
        if self.is_changing:
            return
        
        self.is_changing = True
        if not str.isnumeric(self.end_entry_val.get()):
            self.is_changing = False
            return
        
        end_entry_val = float(self.end_entry_val.get())
        self.end_slider.set(end_entry_val)
        
        self.is_changing = False

    def update_start_entry_from_slider(self, event=None):
        if self.is_changing:
            return
        
        self.is_changing = True
        self.start_entry_val.set(str(self.start_slider.get()))
        self.is_changing = False

    def update_end_entry_from_slider(self, event=None):
        if self.is_changing:
            return
        
        self.is_changing = True
        self.end_entry_val.set(str(self.end_slider.get()))
        self.is_changing = False

    def extract(self):
        # 抽出ボタンをクリックした時の処理を実装する

        start = self.start_val.get()
        end = self.end_val.get()

        command = []
        command.append(self.ffmpeg_path)
        command.append("-i")
        command.append(self.path)
        command.append("-ss")
        command.append(str(start))
        command.append("-t")
        command.append(str(end - start))
        print(command)
        
        pass

root = tk.Tk()
app = Converter(root, 0, 100, 1, 10, "ffmpeg.exe", "")
app.mainloop()
