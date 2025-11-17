"""
Passenger WSGI エントリーポイント
さくらのレンタルサーバー用
"""

import sys
import os

# アプリケーションのディレクトリをPythonパスに追加
INTERP = os.path.expanduser("~/local/python/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# アプリケーションディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

# Flaskアプリケーションをインポート
from app import app as application

# 本番環境設定
application.config['DEBUG'] = False
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-in-production-please')

# セッション設定
application.config['SESSION_TYPE'] = 'filesystem'
application.config['SESSION_FILE_DIR'] = os.path.expanduser('~/tmp/flask_session')
application.config['SESSION_PERMANENT'] = False
application.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 2時間
