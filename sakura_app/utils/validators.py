"""
データ検証ユーティリティ
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Optional


class DataValidator:
    """データ検証クラス"""

    @staticmethod
    def validate_sample_size(data: pd.DataFrame, min_size: int = 3) -> tuple:
        """
        サンプルサイズの検証

        Parameters:
        -----------
        data : pd.DataFrame
            検証するデータ
        min_size : int
            最小サンプルサイズ

        Returns:
        --------
        tuple : (bool, str)
            (検証結果, エラーメッセージ)
        """
        if len(data) < min_size:
            return False, f"サンプルサイズが不足しています。最低{min_size}件必要です。現在: {len(data)}件"
        return True, ""

    @staticmethod
    def check_missing_values(data: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
        """
        欠損値のチェック

        Parameters:
        -----------
        data : pd.DataFrame
            チェックするデータ
        columns : list
            チェックする列名のリスト

        Returns:
        --------
        dict
            {列名: 欠損値の数}
        """
        missing_info = {}
        for col in columns:
            if col in data.columns:
                missing_count = data[col].isnull().sum()
                missing_info[col] = int(missing_count)
        return missing_info

    @staticmethod
    def validate_numeric_columns(data: pd.DataFrame, columns: List[str]) -> tuple:
        """
        数値型列の検証

        Parameters:
        -----------
        data : pd.DataFrame
            検証するデータ
        columns : list
            検証する列名のリスト

        Returns:
        --------
        tuple : (bool, str, list)
            (検証結果, エラーメッセージ, 非数値列のリスト)
        """
        non_numeric = []
        for col in columns:
            if col in data.columns:
                if not pd.api.types.is_numeric_dtype(data[col]):
                    non_numeric.append(col)

        if non_numeric:
            return False, f"以下の列が数値型ではありません: {', '.join(non_numeric)}", non_numeric
        return True, "", []

    @staticmethod
    def check_normality(data: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
        """
        正規性の検定

        Parameters:
        -----------
        data : pd.Series
            検定するデータ
        alpha : float
            有意水準

        Returns:
        --------
        dict
            検定結果の辞書
        """
        clean_data = data.dropna()

        if len(clean_data) < 3:
            return {
                'test': 'insufficient_data',
                'p_value': None,
                'is_normal': False,
                'message': 'データが不足しています'
            }

        try:
            # Shapiro-Wilk検定
            if len(clean_data) <= 5000:
                stat, p_value = stats.shapiro(clean_data)
                test_name = 'Shapiro-Wilk'
            else:
                # サンプルサイズが大きい場合はKolmogorov-Smirnov検定
                stat, p_value = stats.kstest(clean_data, 'norm',
                                             args=(clean_data.mean(), clean_data.std()))
                test_name = 'Kolmogorov-Smirnov'

            is_normal = p_value > alpha

            return {
                'test': test_name,
                'statistic': float(stat),
                'p_value': float(p_value),
                'is_normal': is_normal,
                'message': f'{test_name}検定の結果、p値={p_value:.4f}'
            }
        except Exception as e:
            return {
                'test': 'error',
                'p_value': None,
                'is_normal': False,
                'message': f'正規性検定でエラーが発生しました: {str(e)}'
            }

    @staticmethod
    def check_equal_variances(group1: pd.Series, group2: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
        """
        等分散性の検定（Levene検定）

        Parameters:
        -----------
        group1 : pd.Series
            グループ1のデータ
        group2 : pd.Series
            グループ2のデータ
        alpha : float
            有意水準

        Returns:
        --------
        dict
            検定結果の辞書
        """
        try:
            clean1 = group1.dropna()
            clean2 = group2.dropna()

            if len(clean1) < 2 or len(clean2) < 2:
                return {
                    'statistic': None,
                    'p_value': None,
                    'equal_variances': False,
                    'message': 'データが不足しています'
                }

            stat, p_value = stats.levene(clean1, clean2)
            equal_variances = p_value > alpha

            return {
                'statistic': float(stat),
                'p_value': float(p_value),
                'equal_variances': equal_variances,
                'message': f'Levene検定の結果、p値={p_value:.4f}'
            }
        except Exception as e:
            return {
                'statistic': None,
                'p_value': None,
                'equal_variances': False,
                'message': f'等分散性検定でエラーが発生しました: {str(e)}'
            }

    @staticmethod
    def detect_outliers(data: pd.Series, method: str = 'iqr') -> Dict[str, Any]:
        """
        外れ値の検出

        Parameters:
        -----------
        data : pd.Series
            検出対象のデータ
        method : str
            検出方法 ('iqr' or 'zscore')

        Returns:
        --------
        dict
            外れ値の情報
        """
        clean_data = data.dropna()

        if method == 'iqr':
            Q1 = clean_data.quantile(0.25)
            Q3 = clean_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = clean_data[(clean_data < lower_bound) | (clean_data > upper_bound)]

            return {
                'method': 'IQR',
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'outlier_count': len(outliers),
                'outlier_percentage': float(len(outliers) / len(clean_data) * 100),
                'outliers': outliers.tolist()
            }

        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(clean_data))
            outliers = clean_data[z_scores > 3]

            return {
                'method': 'Z-score',
                'threshold': 3.0,
                'outlier_count': len(outliers),
                'outlier_percentage': float(len(outliers) / len(clean_data) * 100),
                'outliers': outliers.tolist()
            }

        return {'error': '未対応の検出方法です'}
