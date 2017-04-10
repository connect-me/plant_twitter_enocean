# Plant Twitter for EnOcean
植物ったー EnOcean版アプリケーション

    アプリケーションバージョン: 1.0.0
    更新日: 2017.1.2
    作成者: Iori Nishida

### 概要

「植物ったー EnOcean版」は、EnOcean GmbH社の「温度センサ モジュールSTM 431J」と土壌湿度センサー（SEN0114）を使って植物の状態をツイートするIoT（Internet of Things）アプリケーションです。
例えば、植物の土壌水分が少なくなると「土が乾いてきたよ。お水ちょうだい。」とつぶやき、水をあげると「水やりしてくれてありがとう。」とつぶやきます。

Notes: You can get this information in English at  [README_en.md](https://github.com/connect-me/plant_twitter_enocean/blob/master/README_en.md).

## ファイル構成

| ファイル名 | 概要 |
|---|---|
| .gitignore | GitHub用の設定ファイル |
| LICENSE | 本アプリケーションのライセンス|
| README.md | GitHub用の簡易ドキュメント |
| README_en.md | GitHub用の簡易ドキュメント（英語版） |
| config.ini | 本アプリケーションの設定情報 |
| config.py | 設定情報を読み込むモジュール |
| datastore.py | データベースに読み書きするモジュール |
| logger.py | ログを出力するモジュール |
| message.py | ツイートするメッセージを生成するモジュール |
| parse.py | EnOceanデバイスから受信したデータを解析するモジュール |
| profile.py | EnOcean Equipment Profiles毎にセンサー情報を取得するモジュール |
| receiver.py | EnOceanデバイスから受信したデータを受信するアプリケーション |
| register.py | EnOceanデバイスから受信したデータをデーターベースに登録するモジュール |
| setup_db.sh | データベースファイルを作成するスクリプト |
| test_receiver.py | EnOceanデバイスからのパケットを受信するテストプログラム |
| test_tweet.py | データベースに保存したセンサーデータをツイートするテストプログラム |
| tweet.py | データベースに保存したセンサーデータをツイートするアプリケーション |
| debug.log | Plant Twitter用ログファイル。プログラム実行時に自動生成 |
| sensorlogs.db | Plant Twitter用データベースファイル。setup_db.shで生成 |

## 動作環境

### アプリケーション使用言語
    Python: バージョン 3.x（動作確認 Python3.4.2)

### アプリケーション概要

| 項目 | 内容 |
|---|---|
| 動作タイプ | STM431JS：温度と土壌湿度（デフォルト）<br> STM431J：温度のみ<br> STM431JH：温度と湿度 |
| 対応EnOceanモジュール | STM 431J、USB 400J、HSM 100、PTM 210J、STM 429J<br> ※ PTM 210J、STM 429Jはセンサーデータ受信のみ |
| 対応EnOcean Equipment Profiles | STM 431J + 土壌湿度センサー（デフォルト）: A5-10-03<br> STM 431J: A5-02-05<br> STM 431J + HSM 100: A5-04-01<br> PTM 210J: F6-02-04<br> STM 429J: D5-00-01 |
| センサー仕様 | 温度センサー（0℃〜40℃）、土壌湿度センサー（0〜255）、湿度センサー（0％〜100％）<br> ※ 土壌湿度センサー、湿度センサーはどちらか一方のみ使用可能 |
| ツイート条件 | 直近60分以内にセンサーデータを受信したとき |
| ツイート時間帯 | 4:00から21:00まで |
| ツイート間隔 | 30分毎 |
| 水やり反応検知 | 30分以内に水分量の数値が向上したときにツイート |
| メッセージ種類 | 12種類（気温7種、土壌湿度4種、湿度1種） |

## インストール
* 本アプリケーションのインストール

    $ git clone https://github.com/connect-me/plant_twitter_enocean.git

* sqlite3, twitterモジュールのインストール

    $ sudo apt-get install sqlite3  
    $ sudo pip3 install twitter

* データベースの作成

    $ ./setup_db.sh 

* Twitterのアクセストークン、コンシューマーキーの設定

Twitter APIの利用するためには、Twitterアカウントのアクセストークン、コンシューマーキーが必要です。  
Twitterのデベロッパーサイト https://dev.twitter.com/ で作成して、config.ini に記載してください。

    TWITTER_ACCESS_TOKEN : Access Token
    TWITTER_ACCESS_SECRET : Access Token Secret
    TWITTER_CONSUMER_KEY : Consumer Key (API Key)
    TWITTER_CONSUMER_SECRET : Consumer Secret (API Secret)

* EnOceanデバイスの設定

利用するEnOceanデバイスのデバイスIDとデバイスモデルを config.ini に記載してください。
EnOceanデバイスのデバイスIDは、DolphinView Advancedで確認できます。
デバイスモデルと対応デバイスの対応は以下のとおりです。

| デバイスモデル | 対応デバイス | 対応EnOcean Equipment Profiles |
|---|---|---|
| STM431J | STM431J | A5-02-05 |
| STM431JS | STM431J + SEN0114(Soil Moisture) | A5-10-03 |
| STM431JH | STM431J + HSM100 | A5-04-01 |
| PTM210J | PTM210J | F6-02-04 |
| STM429J | STM429J | D5-00-01 |

デバイスIDとデバイスモデルはコロン(:)で区切り、複数記載する場合はカンマ(,)で繋げてください。  

    ENOCEAN_DEVICE_LIST:  {originator id}:{device model}
    例) ENOCEAN_DEVICE_LIST:  040154f1:STM431JS,002b93c6:PTM210J

    DolphinView Advanced -  EnOcean Development Tools
    https://www.enocean.com/en/download/

## 動作テスト
* EnOceanデバイスからのパケット受信テスト

    $ python3 ./test_receiver.py

* センサーデータのツイートテスト

    $ python3 ./test_tweet.py

上記の動作テストの結果は、debug.logに出力されます。  
詳細のログを確認したい場合は、config.iniのDEBUG_LOG_LEVELをDEBUGに変更してください。

## アプリケーションの実行

    $ python3 ./receiver.py &
    $ python3 ./tweet.py &


## ライセンス
本アプリケーションは、MIT LICENSE に準拠しています。  
詳しくは、[LICENSE](https://github.com/connect-me/plant_twitter_enocean/blob/master/LICENSE) を確認してください。

「植物ったー」は、コネクト・ミーが開発した植物コミュニケーションアプリケーションです。  
詳しくは、以下を参照してください。  
http://connect-me-net.tumblr.com/

EnOcean は、EnOcean GmbH社のエネルギーハーベスティング無線センサー技術です。  
詳しくは、以下を参照してください。  
https://www.enocean.com/jp/

## 著作者

Copyright (c) 2017 Iori Nishida <iori.nishida@connect-me.net>


