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

        # スクロールバーとリストボックスの作成
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_listbox = tk.Listbox(self, yscrollcommand=self.scrollbar.set, width=100)
        self.result_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)

        self.scrollbar.config(command=self.result_listbox.yview)


    def search(self):
        # 検索ボタンが押された時に呼ばれる関数
        search_term = self.entry.get()
        self.result_listbox.insert(tk.END, "a" * 150)

if __name__ == "__main__":
    root = tk.Tk()
    form = SearchForm(master=root)
    form.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
