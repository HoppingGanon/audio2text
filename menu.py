import tkinter as tk

class SearchForm(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        self.search_results = []

        # ウィンドウの設定
        self.master = master
        self.master.title("Search Form")
        self.master.geometry("500x400")

        # ラベルとエントリーの作成
        self.label = tk.Label(self, text="Search:")
        self.label.pack(side=tk.TOP, padx=10, pady=10)
        self.entry = tk.Entry(self, width=50)
        self.entry.pack(side=tk.TOP, padx=10, pady=10)

        # 検索ボタンの作成
        self.button = tk.Button(self, text="Search", command=self.search)
        self.button.pack(side=tk.TOP, padx=10, pady=10)

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

        self.update_canvas()

    def update_canvas(self):
        # 検索ボタンが押された時に呼ばれる関数
        # フレーム内の既存のラベルを削除
        for widget in self.frame.winfo_children():
            widget.destroy()

        # フレーム内にグリッドレイアウトを作成
        for i in range(4):
            self.frame.rowconfigure(i, weight=1)
            for j in range(2):
                self.frame.columnconfigure(j, weight=1)

                label = tk.Label(self.frame, text="Label " + str(i) + "," + str(j))
                label.grid(row=i, column=j, padx=10, pady=10)


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
        self.update_canvas()

if __name__ == "__main__":
    root = tk.Tk()
    form = SearchForm(master=root)
    form.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
