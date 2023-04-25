# sound2text
本アプリケーションは、複数の音声ファイルをまとめて音声解析した上で、解析結果の文字列を横断的に検索できるアプリです。動作確認はWindows版しか行ってません。

## 導入方法
### アプリケーションのダウンロード
GitHubのReleaseからもっとも新しいものを選んでダウンロードしてください。

### 音声解析ツールキット「vosk」のモデルを配置する
https://alphacephei.com/vosk/models

### ffmpegの配置
ffmpeg, ffplay, ffprobeのパスを通してください。

パスを通すの意味が分からない方は、以下の手順で必要なファイルを配置してください。

#### 1. ffmpegの入手
以下のサイトにアクセスし、新しいバージョンの「ffmpeg-release-essentials.zip」をダウンロードしてください。

https://www.gyan.dev/ffmpeg/builds/

![](doc/2023-04-25-09-45-07.png)

#### 2.ffmpegの配置
「ffmpeg-release-essentials.zip」をクリックすると、「ffmpeg-x.x-essentials_build」というフォルダの中に「bin」フォルダがあると思います。その中身をすべてコピーしてください。

![](doc/2023-04-25-09-45-20.png)

コピーしたファイルを「soundgrep」のフォルダに貼り付けてください。

![](doc/2023-04-25-09-46-47.png)

## 使い方
加筆予定