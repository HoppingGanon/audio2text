import tkinter as tk
import tkinter.ttk as ttk
from analyze import analyze
from open import pick_json

class SearchForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.search_results = []

        # ウィンドウの設定
        self.master = master
        self.master.title("Search Form")
        self.master.geometry("500x400")

        # メニューバーの作成
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新規プロジェクト", command=self.new_analysis)  # 新規解析コマンドを追加
        file_menu.add_command(label="プロジェクトを開く", command=self.open_data_file)  # 解析データを開くコマンドを追加
        file_menu.add_command(label="プロジェクトの保存(未実装)")  # 解析データを開くコマンドを追加
        file_menu.add_command(label="プロジェクトの上書き(未実装)")  # 解析データを開くコマンドを追加
        menubar.add_cascade(label="ファイル", menu=file_menu)
        self.master.config(menu=menubar)

        # 検索フレームの作成 ----------------------------
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(side=tk.TOP, padx=3, pady=5, anchor="w")
        # ラベルの作成
        self.label = tk.Label(self.search_frame, text="Search:")
        self.label.pack(side=tk.LEFT)
        # エントリーの作成
        self.entry = tk.Entry(self.search_frame, width=50)
        self.entry.pack(side=tk.LEFT, padx=2)
        # 検索ボタンの作成
        self.button = tk.Button(self.search_frame, text="検索", command=self.search)
        self.button.pack(side=tk.LEFT)

        # チェックボックスの作成 ----------------------------
        self.check_frame = tk.Frame(self)
        self.check_frame.pack(side=tk.TOP, padx=3, pady=10, anchor="w")
        label = tk.Label(self.check_frame, text="表示:")
        label.pack(side=tk.LEFT, padx=2)

        self.disp_fname_val = tk.BooleanVar()
        self.disp_fname_val.set(True)
        self.disp_fname = tk.Checkbutton(self.check_frame, text="ファイル名", variable=self.disp_fname_val)
        self.disp_fname.pack(side=tk.LEFT)
        
        self.disp_text_val = tk.BooleanVar()
        self.disp_text_val.set(True)
        self.disp_text = tk.Checkbutton(self.check_frame, text="テキスト", variable=self.disp_text_val)
        self.disp_text.pack(side=tk.LEFT)
        
        self.disp_kana_val = tk.BooleanVar()
        self.disp_kana_val.set(True)
        self.disp_kana = tk.Checkbutton(self.check_frame, text="よみがな", variable=self.disp_kana_val)
        self.disp_kana.pack(side=tk.LEFT)

        # キャンバスの作成
        self.canvas = tk.Canvas(self, bg="white", height=300, width=450, scrollregion=(0, 0, 500, 600))
        self.frame = tk.Frame(self.canvas, bg="white")

        # スクロールイベントの設定
        self.canvas.bind("<Configure>", self.on_configure)
        self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)

        # キャンバスの表示設定
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.update_canvas(450)
        
    # 解析データを開くコマンドの関数
    def open_data_file(self):
        print("Open data file")
        pick_json()

    # 新規解析コマンドの関数
    def new_analysis(self):
        print("New analysis")
        analyze()

    def update_canvas(self, width):
        # 検索ボタンが押された時に呼ばれる関数
        # フレーム内の既存のラベルを削除
        for widget in self.frame.winfo_children():
            widget.destroy()

        # フレーム内にグリッドレイアウトを作成
        print(width)
        for i in range(4):

            r = i*4
            self.frame.rowconfigure(r, weight=1)
            self.frame.columnconfigure(1, weight=1)
            actions_frame=tk.Frame(self.frame)
            actions_frame.grid(row=r, column=1, columnspan=2, pady=5, sticky="ew")
            button = tk.Button(actions_frame, text="再生", command=self.search)
            button.pack(side=tk.LEFT, padx=2)
            button = tk.Button(actions_frame, text="部分再生", command=self.search)
            button.pack(side=tk.LEFT, padx=2)
            button = tk.Button(actions_frame, text="編集(未実装)", command=self.search)
            button.pack(side=tk.LEFT, padx=2)
            
            r = i*4+1
            self.frame.rowconfigure(r, weight=1)
            self.frame.columnconfigure(1, weight=1)
            label = tk.Label(self.frame, text="s" * i, wraplength=100, anchor="w", background="#E0F0FF")
            label.grid(row=r, column=1, padx=1, pady=1, sticky=tk.EW)
            label = tk.Label(self.frame, text="sa" * i, wraplength=width - 120, anchor="w", background="#F0F7FF")
            label.grid(row=r, column=2, padx=1, pady=1, sticky=tk.EW)

            r = i*4+2
            self.frame.rowconfigure(r, weight=1)
            self.frame.columnconfigure(1, weight=1)
            label = tk.Label(self.frame, text="s" * i, wraplength=100, anchor="w", background="#E0F0FF")
            label.grid(row=r, column=1, padx=1, pady=1, sticky=tk.EW)
            label = tk.Label(self.frame, text="sa" * i, wraplength=width - 120, anchor="w", background="#F0F7FF")
            label.grid(row=r, column=2, padx=1, pady=1, sticky=tk.EW)

            r = i*4+3
            self.frame.rowconfigure(r, weight=1)

            self.frame.columnconfigure(1, weight=1)
            label = tk.Label(self.frame, text="s" * i, wraplength=100, anchor="w", background="#E0F0FF")
            label.grid(row=r, column=1, padx=1, pady=1, sticky=tk.EW)
            label = tk.Label(self.frame, text="sdsfgsdfga" * i, wraplength=width - 120, anchor="w", background="#F0F7FF")
            label.grid(row=r, column=2, padx=1, pady=1, sticky=tk.EW)

    def on_configure(self, event):
        # キャンバスのフレームとウィンドウサイズを合わせる
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def mouse_scroll(self, event):
        # スクロールイベントでキャンバスをスクロール
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def search(self):
        # 検索ボタンが押された時に呼ばれる関数
        search_term = self.entry.get()
        print(search_term)
        self.update_idletasks()
        width = self.canvas.winfo_width() - 33
        self.update_canvas(width)

if __name__ == "__main__":
    root = tk.Tk()
    form = SearchForm(master=root)
    form.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
