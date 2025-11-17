"""
easyStat - Flask版統計分析Webアプリケーション
さくらのレンタルサーバー対応
"""

from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import io
import json
import pandas as pd
import numpy as np
from datetime import timedelta

# ユーティリティモジュールのインポート
from utils.file_handler import FileHandler
from utils.statistics import StatisticsAnalyzer
from utils.validators import DataValidator

app = Flask(__name__)

# セキュリティ設定
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# 許可するファイル形式
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}


def allowed_file(filename):
    """ファイル形式の検証"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """トップページ"""
    return render_template('index.html')


@app.route('/correlation')
def correlation():
    """相関分析ページ"""
    return render_template('correlation.html')


@app.route('/eda')
def eda():
    """探索的データ分析ページ"""
    return render_template('eda.html')


@app.route('/ttest')
def ttest():
    """t検定ページ"""
    return render_template('ttest.html')


@app.route('/anova')
def anova():
    """分散分析ページ"""
    return render_template('anova.html')


@app.route('/regression')
def regression():
    """回帰分析ページ"""
    return render_template('regression.html')


@app.route('/chi_square')
def chi_square():
    """カイ二乗検定ページ"""
    return render_template('chi_square.html')


@app.route('/cleansing')
def cleansing():
    """データクレンジングページ"""
    return render_template('cleansing.html')


@app.route('/factor_analysis')
def factor_analysis():
    """因子分析ページ"""
    return render_template('factor_analysis.html')


@app.route('/pca')
def pca():
    """主成分分析ページ"""
    return render_template('pca.html')


@app.route('/text_mining')
def text_mining():
    """テキストマイニングページ"""
    return render_template('text_mining.html')


# API エンドポイント

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    ファイルアップロードAPI
    ファイルをメモリに読み込み、セッションIDと紐付けて保持
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルが選択されていません'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'ファイル名が空です'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': '対応していないファイル形式です。CSV, Excel(.xlsx/.xls)を使用してください'}), 400

        # ファイルをメモリに読み込み
        file_bytes = file.read()
        filename = secure_filename(file.filename)

        # データフレームに変換
        df = FileHandler.load_dataframe(file_bytes, filename)

        if df is None:
            return jsonify({'error': 'ファイルの読み込みに失敗しました'}), 400

        # セッションにデータを保存（JSONに変換）
        session['data'] = df.to_json(orient='split', date_format='iso')
        session['filename'] = filename
        session.permanent = True

        # プレビューデータを返す
        preview = {
            'filename': filename,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'head': df.head(10).to_dict(orient='records'),
            'dtypes': df.dtypes.astype(str).to_dict()
        }

        return jsonify(preview), 200

    except Exception as e:
        return jsonify({'error': f'アップロード処理中にエラーが発生しました: {str(e)}'}), 500


@app.route('/api/demo_data/<dataset_name>', methods=['GET'])
def load_demo_data(dataset_name):
    """デモデータの読み込み"""
    try:
        demo_files = {
            'correlation': 'datasets/correlation_demo.xlsx',
            'ttest': 'datasets/ttest_demo.xlsx',
            'anova': 'datasets/anova_demo.xlsx',
        }

        if dataset_name not in demo_files:
            return jsonify({'error': '指定されたデモデータが存在しません'}), 404

        filepath = demo_files[dataset_name]

        if not os.path.exists(filepath):
            return jsonify({'error': 'デモデータファイルが見つかりません'}), 404

        df = pd.read_excel(filepath)

        # セッションにデータを保存
        session['data'] = df.to_json(orient='split', date_format='iso')
        session['filename'] = f'{dataset_name}_demo.xlsx'
        session.permanent = True

        # プレビューデータを返す
        preview = {
            'filename': session['filename'],
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'head': df.head(10).to_dict(orient='records'),
            'dtypes': df.dtypes.astype(str).to_dict()
        }

        return jsonify(preview), 200

    except Exception as e:
        return jsonify({'error': f'デモデータの読み込み中にエラーが発生しました: {str(e)}'}), 500


@app.route('/api/correlation/analyze', methods=['POST'])
def analyze_correlation():
    """相関分析API"""
    try:
        # セッションからデータを取得
        if 'data' not in session:
            return jsonify({'error': 'データがアップロードされていません'}), 400

        df = pd.read_json(io.StringIO(session['data']), orient='split')

        # リクエストパラメータ
        params = request.get_json()
        selected_columns = params.get('columns', [])
        remove_missing = params.get('remove_missing', True)

        # バリデーション
        if len(selected_columns) < 2:
            return jsonify({'error': '少なくとも2つの変数を選択してください'}), 400

        # 欠損値の処理
        if remove_missing:
            df = df[selected_columns].dropna()

        # 相関分析の実行
        analyzer = StatisticsAnalyzer(df)
        results = analyzer.correlation_analysis(selected_columns)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': f'分析中にエラーが発生しました: {str(e)}'}), 500


@app.route('/api/eda/analyze', methods=['POST'])
def analyze_eda():
    """探索的データ分析API"""
    try:
        if 'data' not in session:
            return jsonify({'error': 'データがアップロードされていません'}), 400

        df = pd.read_json(io.StringIO(session['data']), orient='split')

        params = request.get_json()
        column = params.get('column')

        if not column or column not in df.columns:
            return jsonify({'error': '有効な変数を選択してください'}), 400

        analyzer = StatisticsAnalyzer(df)
        results = analyzer.eda_analysis(column)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': f'分析中にエラーが発生しました: {str(e)}'}), 500


@app.route('/api/ttest/analyze', methods=['POST'])
def analyze_ttest():
    """t検定API"""
    try:
        if 'data' not in session:
            return jsonify({'error': 'データがアップロードされていません'}), 400

        df = pd.read_json(io.StringIO(session['data']), orient='split')

        params = request.get_json()
        test_type = params.get('test_type', 'independent')  # 'independent' or 'paired'

        analyzer = StatisticsAnalyzer(df)

        if test_type == 'independent':
            group_col = params.get('group_col')
            value_col = params.get('value_col')
            results = analyzer.ttest_independent(group_col, value_col)
        else:
            var1 = params.get('var1')
            var2 = params.get('var2')
            results = analyzer.ttest_paired(var1, var2)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': f'分析中にエラーが発生しました: {str(e)}'}), 500


@app.route('/api/chi_square/analyze', methods=['POST'])
def analyze_chi_square():
    """カイ二乗検定API"""
    try:
        if 'data' not in session:
            return jsonify({'error': 'データがアップロードされていません'}), 400

        df = pd.read_json(io.StringIO(session['data']), orient='split')

        params = request.get_json()
        var1 = params.get('var1')
        var2 = params.get('var2')

        analyzer = StatisticsAnalyzer(df)
        results = analyzer.chi_square_test(var1, var2)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': f'分析中にエラーが発生しました: {str(e)}'}), 500


@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """セッションデータのクリア"""
    try:
        session.clear()
        return jsonify({'message': 'セッションをクリアしました'}), 200
    except Exception as e:
        return jsonify({'error': f'セッションのクリアに失敗しました: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """ファイルサイズ超過エラー"""
    return jsonify({'error': 'ファイルサイズが大きすぎます。16MB以下のファイルをアップロードしてください。'}), 413


@app.errorhandler(500)
def internal_server_error(error):
    """サーバーエラー"""
    return jsonify({'error': 'サーバー内部エラーが発生しました。'}), 500


if __name__ == '__main__':
    # 開発サーバーとして実行
    app.run(debug=True, host='0.0.0.0', port=5000)
