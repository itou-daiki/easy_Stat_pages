# easyStat - Flask版（さくらのレンタルサーバー対応）

ブラウザ上で簡単かつ高速に統計分析を行えるWebアプリケーション。
**アップロードされたファイルはサーバーに保存されず、セッション終了後は自動的に削除されます。**

## 特徴

- **Streamlitを使わない**: Flask + Bootstrap 5による標準的なWebアプリケーション
- **さくらのレンタルサーバー対応**: Passenger WSGIで動作
- **ファイルをサーバーに保存しない**: セッションベースで処理、プライバシー保護
- **多彩な統計分析機能**: 相関分析、t検定、分散分析、回帰分析など14種類の分析手法

## 分析機能

### データ前処理
- データクレンジング

### 探索的データ分析
- 探索的データ分析（EDA）
- 相関分析

### 仮説検定
- カイ二乗検定
- t検定（対応あり・なし）
- 一要因分散分析（対応あり・なし）
- 二要因分散分析
- 二要因混合分散分析

### 回帰・予測
- 単回帰分析
- 重回帰分析

### 多変量解析
- 因子分析
- 主成分分析

### テキスト分析
- テキストマイニング

## 技術スタック

### バックエンド
- **Flask 3.0**: Pythonウェブフレームワーク
- **Pandas**: データ処理
- **NumPy**: 数値計算
- **SciPy**: 統計計算
- **scikit-learn**: 機械学習
- **Statsmodels**: 統計モデリング

### フロントエンド
- **Bootstrap 5**: UIフレームワーク
- **Plotly.js**: インタラクティブな可視化
- **Font Awesome**: アイコン

## さくらのレンタルサーバーへのデプロイ方法

### 前提条件
- さくらのレンタルサーバー（スタンダードプラン以上）
- Python 3.9以上が利用可能
- SSHアクセス権限

### デプロイ手順

#### 1. サーバーへのアップロード

FTPまたはSSH経由で`sakura_app`ディレクトリ全体をサーバーにアップロードします。

```bash
# ローカルからさくらサーバーへアップロード（例）
scp -r sakura_app [username]@[your-domain].sakura.ne.jp:~/www/
```

#### 2. SSHでサーバーにログイン

```bash
ssh [username]@[your-domain].sakura.ne.jp
```

#### 3. Python仮想環境のセットアップ

```bash
cd ~/www/sakura_app

# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

#### 4. .htaccessの設定を修正

`.htaccess`ファイルを編集し、以下の部分を自分の環境に合わせて変更してください:

```apache
PassengerAppRoot /home/[YOUR_USERNAME]/www/sakura_app
```

`[YOUR_USERNAME]`を実際のさくらサーバーのユーザー名に置き換えてください。

#### 5. 環境変数の設定

セキュリティのため、`SECRET_KEY`を設定します:

```bash
cd ~/www/sakura_app
echo "SECRET_KEY=your-very-secret-random-key-here" > .env
```

**重要**: 本番環境では必ず強力なランダムなキーを使用してください。

```python
# Pythonで生成する例
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

#### 6. セッション保存ディレクトリの作成

```bash
mkdir -p ~/tmp/flask_session
```

#### 7. デモデータのコピー（オプション）

元の`datasets`フォルダをコピーします:

```bash
cp -r ../easy_Stat_pages/datasets ./
```

#### 8. 画像ファイルのコピー（オプション）

元の`images`フォルダをコピーします:

```bash
cp -r ../easy_Stat_pages/images ./static/
```

#### 9. アプリケーションの再起動

```bash
# Passengerの再起動
touch tmp/restart.txt
```

#### 10. ブラウザでアクセス

`https://your-domain.sakura.ne.jp/sakura_app/`にアクセスして動作確認してください。

## ローカルでの開発・テスト

### 環境構築

```bash
# リポジトリのクローン
git clone [repository-url]
cd sakura_app

# 仮想環境の作成
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 開発サーバーの起動

```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

## ディレクトリ構造

```
sakura_app/
├── app.py                    # Flaskアプリケーション本体
├── passenger_wsgi.py         # さくらサーバー用エントリーポイント
├── .htaccess                 # Apache設定
├── requirements.txt          # Python依存パッケージ
├── README.md                 # このファイル
├── utils/                    # ユーティリティモジュール
│   ├── __init__.py
│   ├── file_handler.py       # ファイル処理
│   ├── statistics.py         # 統計分析
│   └── validators.py         # データ検証
├── static/                   # 静的ファイル
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/               # 分析手法の説明画像
├── templates/                # HTMLテンプレート
│   ├── base.html
│   ├── index.html
│   ├── correlation.html
│   └── ...
└── datasets/                 # デモデータ（オプション）
```

## セキュリティ

### ファイル保存について
- アップロードされたファイルは**サーバーに保存されません**
- データはセッションメモリ上でのみ処理されます
- セッション終了時（ブラウザを閉じる、一定時間操作がない）に自動的に削除されます

### セキュリティ設定
- ファイルサイズ制限: 最大16MB
- セッションタイムアウト: 2時間
- XSS、クリックジャッキング、CSRFなどの対策を実装

## トラブルシューティング

### アプリケーションが起動しない

1. **Pythonのバージョン確認**
   ```bash
   python3 --version  # 3.9以上が必要
   ```

2. **依存パッケージの再インストール**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **ログの確認**
   ```bash
   tail -f ~/www/sakura_app/tmp/log/error.log
   ```

### 分析が実行できない

1. **セッションのクリア**
   - ブラウザのキャッシュとCookieをクリアしてください

2. **ファイル形式の確認**
   - CSV、Excel(.xlsx, .xls)のみサポートしています
   - ファイルサイズは16MB以下にしてください

### パフォーマンスが遅い

1. **データサイズの削減**
   - 大きなデータセットは処理に時間がかかります
   - 必要な列のみを選択してください

2. **ブラウザキャッシュの活用**
   - 静的ファイル（CSS、JS）はブラウザにキャッシュされます

## ライセンス

© 2022-2025 Dit-Lab.(Daiki Ito). All Rights Reserved.

easyStat: Open Source for Ubiquitous Statistics
Democratizing data, everywhere.

## クレジット

- **作成者**: Dit-Lab. (Daiki Ito)
- **協力者**: Toshiyuki
- **フィードバック**: [Google Forms](https://forms.gle/G5sMYm7dNpz2FQtU9)
- **ソースコード**: [GitHub](https://github.com/itou-daiki/easy_stat)

## リンク

- [中の人のページ（Dit-Lab.）](https://dit-lab.notion.site/Dit-Lab-da906d09d3cf42a19a011cf4bf25a673?pvs=4)
- [情報探究ステップアップガイド](https://dit-lab.notion.site/612d9665350544aa97a2a8514a03c77c?v=85ad37a3275b4717a0033516b9cfd9cc)
