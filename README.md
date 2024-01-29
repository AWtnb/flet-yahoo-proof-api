# README

[Yahoo!校正支援API](https://developer.yahoo.co.jp/webapi/jlp/kousei/v2/kousei.html)を利用するデスクトップアプリを[Flet](https://flet.dev/)で作ってみる。

## ビルド

1. [Yahoo!デベロッパーネットワークに登録](https://developer.yahoo.co.jp/start/)
1. アプリケーションを登録してアプリIDを取得する
1. `main.py`と同ディレクトリに`.env`ファイルを作り、アプリIDを下記のように指定する

    ```.env
    YAHOO_APPID=（ここにアプリIDを入れる）
    ```

1. 必要なパッケージをインストールする

    ```
    pip install flet
    pip install python-dotenv
    ```

1. 下記コマンドを実行すると、`dist`ディレクトリ内に`yahoo-proof.exe`がビルドされる

    ```
    flet pack main.py --name yahoo-proof
    ```


---
クレジット：

Webサービス by Yahoo! JAPAN （https://developer.yahoo.co.jp/sitemap/）
