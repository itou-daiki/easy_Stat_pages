"""
統計分析ユーティリティ
既存のStreamlitアプリケーションのロジックを移植
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Optional
import json


class StatisticsAnalyzer:
    """統計分析クラス"""

    def __init__(self, dataframe: pd.DataFrame):
        """
        Parameters:
        -----------
        dataframe : pd.DataFrame
            分析対象のデータフレーム
        """
        self.df = dataframe

    def correlation_analysis(self, columns: List[str]) -> Dict[str, Any]:
        """
        相関分析

        Parameters:
        -----------
        columns : list
            分析する列名のリスト

        Returns:
        --------
        dict
            分析結果
        """
        try:
            # 相関行列の計算
            corr_matrix = self.df[columns].corr()

            # p値の計算
            n = len(self.df[columns])
            p_values = pd.DataFrame(
                np.zeros((len(columns), len(columns))),
                index=columns,
                columns=columns
            )

            for i, col1 in enumerate(columns):
                for j, col2 in enumerate(columns):
                    if i != j:
                        r = corr_matrix.loc[col1, col2]
                        # t統計量を計算
                        t_stat = r * np.sqrt((n - 2) / (1 - r ** 2))
                        # p値を計算
                        p_val = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
                        p_values.loc[col1, col2] = p_val
                    else:
                        p_values.loc[col1, col2] = 0.0

            # 散布図用のデータ
            scatter_data = []
            for col in columns:
                scatter_data.append({
                    'name': col,
                    'values': self.df[col].dropna().tolist()
                })

            return {
                'correlation_matrix': corr_matrix.to_dict(),
                'p_values': p_values.to_dict(),
                'columns': columns,
                'scatter_data': scatter_data,
                'sample_size': n
            }

        except Exception as e:
            raise Exception(f"相関分析でエラーが発生しました: {str(e)}")

    def eda_analysis(self, column: str) -> Dict[str, Any]:
        """
        探索的データ分析（EDA）

        Parameters:
        -----------
        column : str
            分析する列名

        Returns:
        --------
        dict
            分析結果
        """
        try:
            data = self.df[column].dropna()

            # 記述統計量
            stats_summary = {
                'count': int(data.count()),
                'mean': float(data.mean()),
                'std': float(data.std()),
                'min': float(data.min()),
                'q1': float(data.quantile(0.25)),
                'median': float(data.median()),
                'q3': float(data.quantile(0.75)),
                'max': float(data.max()),
                'skewness': float(data.skew()),
                'kurtosis': float(data.kurtosis())
            }

            # ヒストグラム用のデータ
            hist_data = data.tolist()

            # 箱ひげ図用のデータ
            box_data = {
                'min': stats_summary['min'],
                'q1': stats_summary['q1'],
                'median': stats_summary['median'],
                'q3': stats_summary['q3'],
                'max': stats_summary['max']
            }

            # 正規性検定
            if len(data) >= 3:
                shapiro_stat, shapiro_p = stats.shapiro(data)
                normality_test = {
                    'test': 'Shapiro-Wilk',
                    'statistic': float(shapiro_stat),
                    'p_value': float(shapiro_p),
                    'is_normal': shapiro_p > 0.05
                }
            else:
                normality_test = {
                    'test': 'insufficient_data',
                    'statistic': None,
                    'p_value': None,
                    'is_normal': False
                }

            return {
                'column': column,
                'statistics': stats_summary,
                'histogram_data': hist_data,
                'box_data': box_data,
                'normality_test': normality_test
            }

        except Exception as e:
            raise Exception(f"EDA分析でエラーが発生しました: {str(e)}")

    def ttest_independent(self, group_col: str, value_col: str) -> Dict[str, Any]:
        """
        対応なしt検定

        Parameters:
        -----------
        group_col : str
            グループ列名
        value_col : str
            値列名

        Returns:
        --------
        dict
            検定結果
        """
        try:
            # グループの取得
            groups = self.df[group_col].unique()

            if len(groups) != 2:
                raise ValueError("グループ列は2つのグループを含む必要があります")

            group1_data = self.df[self.df[group_col] == groups[0]][value_col].dropna()
            group2_data = self.df[self.df[group_col] == groups[1]][value_col].dropna()

            # t検定の実行（Welchのt検定）
            t_stat, p_value = stats.ttest_ind(group1_data, group2_data, equal_var=False)

            # 効果量（Cohen's d）の計算
            mean1 = group1_data.mean()
            mean2 = group2_data.mean()
            std1 = group1_data.std()
            std2 = group2_data.std()
            n1 = len(group1_data)
            n2 = len(group2_data)

            pooled_std = np.sqrt(((n1 - 1) * std1 ** 2 + (n2 - 1) * std2 ** 2) / (n1 + n2 - 2))
            cohens_d = (mean1 - mean2) / pooled_std

            # 等分散性の検定
            levene_stat, levene_p = stats.levene(group1_data, group2_data)

            return {
                'test_type': '対応なしt検定（Welchのt検定）',
                'group1_name': str(groups[0]),
                'group2_name': str(groups[1]),
                'group1_stats': {
                    'mean': float(mean1),
                    'std': float(std1),
                    'n': int(n1),
                    'data': group1_data.tolist()
                },
                'group2_stats': {
                    'mean': float(mean2),
                    'std': float(std2),
                    'n': int(n2),
                    'data': group2_data.tolist()
                },
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'degrees_of_freedom': int(n1 + n2 - 2),
                'effect_size': float(cohens_d),
                'equal_variance_test': {
                    'statistic': float(levene_stat),
                    'p_value': float(levene_p),
                    'equal_variances': levene_p > 0.05
                },
                'significant': p_value < 0.05
            }

        except Exception as e:
            raise Exception(f"対応なしt検定でエラーが発生しました: {str(e)}")

    def ttest_paired(self, var1: str, var2: str) -> Dict[str, Any]:
        """
        対応ありt検定

        Parameters:
        -----------
        var1 : str
            変数1の列名
        var2 : str
            変数2の列名

        Returns:
        --------
        dict
            検定結果
        """
        try:
            # 欠損値を除いてペアのデータを取得
            paired_data = self.df[[var1, var2]].dropna()
            data1 = paired_data[var1]
            data2 = paired_data[var2]

            # 対応ありt検定の実行
            t_stat, p_value = stats.ttest_rel(data1, data2)

            # 差の平均と標準偏差
            diff = data1 - data2
            mean_diff = diff.mean()
            std_diff = diff.std()
            n = len(diff)

            # 効果量（Cohen's d）の計算
            cohens_d = mean_diff / std_diff

            return {
                'test_type': '対応ありt検定',
                'var1_name': var1,
                'var2_name': var2,
                'var1_stats': {
                    'mean': float(data1.mean()),
                    'std': float(data1.std()),
                    'n': int(n),
                    'data': data1.tolist()
                },
                'var2_stats': {
                    'mean': float(data2.mean()),
                    'std': float(data2.std()),
                    'n': int(n),
                    'data': data2.tolist()
                },
                'difference_stats': {
                    'mean': float(mean_diff),
                    'std': float(std_diff),
                    'data': diff.tolist()
                },
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'degrees_of_freedom': int(n - 1),
                'effect_size': float(cohens_d),
                'significant': p_value < 0.05
            }

        except Exception as e:
            raise Exception(f"対応ありt検定でエラーが発生しました: {str(e)}")

    def chi_square_test(self, var1: str, var2: str) -> Dict[str, Any]:
        """
        カイ二乗検定

        Parameters:
        -----------
        var1 : str
            変数1の列名
        var2 : str
            変数2の列名

        Returns:
        --------
        dict
            検定結果
        """
        try:
            # クロス集計表の作成
            contingency_table = pd.crosstab(self.df[var1], self.df[var2])

            # カイ二乗検定の実行
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

            # Cramér's V（効果量）の計算
            n = contingency_table.sum().sum()
            min_dim = min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)
            cramers_v = np.sqrt(chi2 / (n * min_dim))

            return {
                'test_type': 'カイ二乗検定',
                'var1': var1,
                'var2': var2,
                'contingency_table': contingency_table.to_dict(),
                'expected_frequencies': pd.DataFrame(expected,
                                                     index=contingency_table.index,
                                                     columns=contingency_table.columns).to_dict(),
                'chi2_statistic': float(chi2),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'cramers_v': float(cramers_v),
                'significant': p_value < 0.05,
                'sample_size': int(n)
            }

        except Exception as e:
            raise Exception(f"カイ二乗検定でエラーが発生しました: {str(e)}")

    def one_way_anova(self, group_col: str, value_col: str) -> Dict[str, Any]:
        """
        一要因分散分析（対応なし）

        Parameters:
        -----------
        group_col : str
            グループ列名
        value_col : str
            値列名

        Returns:
        --------
        dict
            分析結果
        """
        try:
            groups = self.df[group_col].unique()

            if len(groups) < 2:
                raise ValueError("少なくとも2つのグループが必要です")

            # 各グループのデータを取得
            group_data = []
            group_stats = {}

            for group in groups:
                data = self.df[self.df[group_col] == group][value_col].dropna()
                group_data.append(data)
                group_stats[str(group)] = {
                    'mean': float(data.mean()),
                    'std': float(data.std()),
                    'n': int(len(data)),
                    'data': data.tolist()
                }

            # 一要因分散分析の実行
            f_stat, p_value = stats.f_oneway(*group_data)

            # 効果量（η²）の計算
            all_data = self.df[value_col].dropna()
            ss_total = ((all_data - all_data.mean()) ** 2).sum()
            ss_between = sum([len(data) * (data.mean() - all_data.mean()) ** 2 for data in group_data])
            eta_squared = ss_between / ss_total

            # 自由度
            df_between = len(groups) - 1
            df_within = len(all_data) - len(groups)

            return {
                'test_type': '一要因分散分析（対応なし）',
                'group_col': group_col,
                'value_col': value_col,
                'groups': [str(g) for g in groups],
                'group_statistics': group_stats,
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'df_between': int(df_between),
                'df_within': int(df_within),
                'eta_squared': float(eta_squared),
                'significant': p_value < 0.05
            }

        except Exception as e:
            raise Exception(f"一要因分散分析でエラーが発生しました: {str(e)}")

    def simple_regression(self, x_col: str, y_col: str) -> Dict[str, Any]:
        """
        単回帰分析

        Parameters:
        -----------
        x_col : str
            説明変数の列名
        y_col : str
            目的変数の列名

        Returns:
        --------
        dict
            分析結果
        """
        try:
            # 欠損値を除去
            data = self.df[[x_col, y_col]].dropna()
            x = data[x_col].values
            y = data[y_col].values
            n = len(x)

            # 回帰係数の計算
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

            # 決定係数
            r_squared = r_value ** 2

            # 予測値と残差
            y_pred = slope * x + intercept
            residuals = y - y_pred

            # F統計量
            mse = np.sum(residuals ** 2) / (n - 2)
            f_stat = (r_squared / 1) / ((1 - r_squared) / (n - 2))
            f_pvalue = 1 - stats.f.cdf(f_stat, 1, n - 2)

            return {
                'test_type': '単回帰分析',
                'x_variable': x_col,
                'y_variable': y_col,
                'sample_size': int(n),
                'coefficients': {
                    'intercept': float(intercept),
                    'slope': float(slope),
                    'slope_std_error': float(std_err)
                },
                'r_squared': float(r_squared),
                'r_value': float(r_value),
                'p_value': float(p_value),
                'f_statistic': float(f_stat),
                'f_pvalue': float(f_pvalue),
                'data': {
                    'x': x.tolist(),
                    'y': y.tolist(),
                    'y_pred': y_pred.tolist(),
                    'residuals': residuals.tolist()
                },
                'significant': p_value < 0.05
            }

        except Exception as e:
            raise Exception(f"単回帰分析でエラーが発生しました: {str(e)}")
