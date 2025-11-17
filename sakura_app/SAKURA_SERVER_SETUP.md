# さくらのレンタルサーバー側の設定手順

## 前提条件

- さくらのレンタルサーバー（スタンダードプラン以上）
- SSHアクセス可能な状態
- Python 3.9以上が利用可能

## 1. サーバーコントロールパネルでの設定

### 1.1 Pythonバージョンの確認

さくらのレンタルサーバーでは、デフォルトでPythonが利用可能ですが、バージョンを確認する必要があります。

1. **サーバーコントロールパネルにログイン**
   - https://secure.sakura.ad.jp/rscontrol/ にアクセス

2. **スクリプト設定を確認**
   - 左メニュー「スクリプト設定」→「言語のバージョン設定」
   - Pythonのバージョンを確認（3.9以上を推奨）

### 1.2 SSHの有効化

1. コントロールパネル左メニュー「サーバー情報」→「サーバー設定」
2. 「SSH設定」で「SSHを有効にする」をON
3. 公開鍵認証または、パスワード認証を設定

## 2. SSHでサーバーに接続

```bash
ssh ユーザー名@ユーザー名.sakura.ne.jp
```

初回接続時はホストの信頼性を確認されるので `yes` を入力します。

## 3. Pythonバージョンの確認

```bash
# デフォルトのPythonバージョンを確認
python3 --version

# 利用可能なPythonバージョンを確認
ls /usr/local/bin/python*
```

さくらサーバーでは通常、`/usr/local/bin/python3.9` や `/usr/local/bin/python3.10` などが利用可能です。

## 4. ディレクトリ構造の準備

さくらのレンタルサーバーでは、以下のディレクトリ構造が推奨されます：

```
/home/ユーザー名/
├── www/                    # 公開ディレクトリ
│   └── sakura_app/        # アプリケーション（ここにアップロード）
├── local/                  # ローカルインストール用
│   └── python/
│       └── bin/
└── tmp/                    # 一時ファイル
    └── flask_session/      # セッション保存用
```

### ディレクトリ作成

```bash
# ホームディレクトリに移動
cd ~

# 必要なディレクトリを作成
mkdir -p tmp/flask_session
mkdir -p local/python/bin
mkdir -p www
```

## 5. アプリケーションのアップロード

### 5.1 FTP/SFTPでアップロード

FTPクライアント（FileZilla、WinSCPなど）を使用：

- **ホスト**: ユーザー名.sakura.ne.jp
- **ユーザー名**: さくらサーバーのユーザー名
- **パスワード**: さくらサーバーのパスワード
- **ポート**: 22 (SFTP)

`sakura_app` フォルダ全体を `~/www/` ディレクトリにアップロードします。

### 5.2 Gitでクローン（推奨）

```bash
cd ~/www
git clone https://github.com/itou-daiki/easy_Stat_pages.git
cd easy_Stat_pages
```

## 6. Python仮想環境のセットアップ

```bash
cd ~/www/sakura_app

# 仮想環境の作成（Python 3.9以上を使用）
/usr/local/bin/python3.9 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# pipのアップグレード
pip install --upgrade pip

# 依存パッケージのインストール
pip install -r requirements.txt
```

**注意**: パッケージのインストールには数分〜10分程度かかる場合があります。

### インストール中にエラーが出た場合

```bash
# メモリ不足エラーの場合
pip install --no-cache-dir -r requirements.txt

# 個別にインストール
pip install Flask==3.0.0
pip install pandas==2.0.3
pip install numpy==1.24.3
# ... 以下、requirements.txtの内容を1つずつ
```

## 7. .htaccessの設定

`sakura_app/.htaccess` ファイルを編集します：

```bash
cd ~/www/sakura_app
nano .htaccess
```

以下の行を**自分のユーザー名に変更**してください：

```apache
PassengerAppRoot /home/[YOUR_USERNAME]/www/sakura_app
```

例：ユーザー名が `example` の場合
```apache
PassengerAppRoot /home/example/www/sakura_app
```

**Ctrl + X** → **Y** → **Enter** で保存して終了します。

## 8. passenger_wsgi.pyの確認

`sakura_app/passenger_wsgi.py` を確認します：

```bash
nano passenger_wsgi.py
```

以下の部分が正しいか確認：

```python
INTERP = os.path.expanduser("~/local/python/bin/python3")
```

さくらサーバーのPythonパスを使用する場合は、以下のように変更：

```python
INTERP = "/usr/local/bin/python3.9"  # または使用するPythonバージョン
```

## 9. 環境変数の設定（セキュリティ）

本番環境用の秘密鍵を設定します：

```bash
cd ~/www/sakura_app

# ランダムな秘密鍵を生成
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

出力された文字列をコピーして、`.env` ファイルを作成：

```bash
nano .env
```

以下を記述（生成した鍵を使用）：

```
SECRET_KEY=ここに生成した秘密鍵を貼り付け
```

## 10. パーミッションの設定

```bash
cd ~/www/sakura_app

# ディレクトリのパーミッション
chmod 755 .
chmod 755 utils/
chmod 755 static/
chmod 755 templates/

# ファイルのパーミッション
chmod 644 app.py
chmod 644 passenger_wsgi.py
chmod 644 .htaccess
chmod 600 .env  # 環境変数ファイルは非公開
```

## 11. アプリケーションの起動

```bash
# セッション保存用ディレクトリの確認
ls -la ~/tmp/flask_session

# Passengerを再起動（アプリケーション起動）
touch ~/www/sakura_app/tmp/restart.txt
```

**注意**: `tmp/restart.txt` が存在しない場合は作成します：

```bash
mkdir -p ~/www/sakura_app/tmp
touch ~/www/sakura_app/tmp/restart.txt
```

## 12. 動作確認

ブラウザで以下のURLにアクセスします：

```
https://ユーザー名.sakura.ne.jp/sakura_app/
```

または独自ドメインを設定している場合：

```
https://your-domain.com/sakura_app/
```

## 13. トラブルシューティング

### アプリケーションが表示されない場合

#### エラーログの確認

```bash
# Apacheエラーログ
tail -f ~/www/sakura_app/log/error.log

# さくらサーバーのエラーログ
tail -f ~/log/error_log
```

#### よくあるエラーと対処法

**1. "Internal Server Error (500)"**

原因: Pythonパスが正しくない、または依存パッケージがインストールされていない

```bash
# passenger_wsgi.pyのPythonパスを確認
which python3
# 出力されたパスを passenger_wsgi.py の INTERP に設定

# 依存パッケージの再インストール
source venv/bin/activate
pip install -r requirements.txt
```

**2. "403 Forbidden"**

原因: パーミッションが正しくない

```bash
chmod 755 ~/www/sakura_app
chmod 644 ~/www/sakura_app/.htaccess
```

**3. "Module not found" エラー**

原因: 仮想環境のPythonが使われていない

`passenger_wsgi.py` を以下のように修正：

```python
import sys
import os

# 仮想環境のパスを追加
VENV_PATH = os.path.expanduser("~/www/sakura_app/venv")
sys.path.insert(0, os.path.join(VENV_PATH, 'lib/python3.9/site-packages'))

# アプリケーションディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application
```

**4. セッションが保存されない**

```bash
# セッション保存ディレクトリの確認とパーミッション設定
mkdir -p ~/tmp/flask_session
chmod 777 ~/tmp/flask_session
```

### アプリケーションの再起動

設定を変更したら、必ずアプリケーションを再起動してください：

```bash
touch ~/www/sakura_app/tmp/restart.txt
```

## 14. 独自ドメインの設定（オプション）

さくらサーバーで独自ドメインを設定する場合：

1. コントロールパネル「ドメイン設定」→「ドメイン/SSL設定」
2. 対象ドメインの「変更」をクリック
3. 「マルチドメインとして使用する」を選択
4. 公開フォルダを `sakura_app` に設定

これにより、`https://your-domain.com/` で直接アクセスできるようになります。

## 15. SSL証明書の設定（Let's Encrypt）

さくらサーバーでは無料のSSL証明書が利用できます：

1. コントロールパネル「ドメイン/SSL設定」
2. 対象ドメインの「SSL証明書」→「無料SSLの設定」
3. 「無料SSLを設定する」をクリック

数分で設定が完了し、HTTPSでアクセスできるようになります。

## 16. 定期的なメンテナンス

### ログのローテーション

```bash
# 古いログを削除（毎月1回程度）
cd ~/www/sakura_app/log
rm -f error.log.*
```

### アップデート

```bash
cd ~/www/sakura_app
source venv/bin/activate

# パッケージのアップデート
pip install --upgrade -r requirements.txt

# アプリケーションの再起動
touch tmp/restart.txt
```

## サポート情報

- さくらのサポート: https://help.sakura.ad.jp/
- Python/Passenger関連: https://help.sakura.ad.jp/rs/2137/
- SSH接続: https://help.sakura.ad.jp/rs/2172/

## チェックリスト

設定が完了したら、以下を確認してください：

- [ ] Pythonバージョンが3.9以上
- [ ] SSHで接続できる
- [ ] 仮想環境が作成されている
- [ ] 依存パッケージがインストールされている
- [ ] .htaccessのユーザー名が正しい
- [ ] SECRET_KEYが設定されている
- [ ] パーミッションが正しい
- [ ] ブラウザでアクセスできる
- [ ] ファイルアップロードが動作する
- [ ] 分析機能が正常に動作する

すべてチェックできたら、デプロイ完了です！
