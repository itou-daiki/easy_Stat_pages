"""
ファイルアップロードとデータ処理のユーティリティ
サーバーにファイルを保存せず、メモリ上で処理
"""

import io
import pandas as pd
from typing import Optional


class FileHandler:
    """ファイル処理クラス"""

    @staticmethod
    def load_dataframe(file_bytes: bytes, filename: str) -> Optional[pd.DataFrame]:
        """
        バイトデータからDataFrameを作成

        Parameters:
        -----------
        file_bytes : bytes
            ファイルのバイトデータ
        filename : str
            ファイル名（拡張子判定用）

        Returns:
        --------
        pd.DataFrame or None
            読み込んだDataFrame、失敗時はNone
        """
        try:
            file_extension = filename.rsplit('.', 1)[1].lower()

            if file_extension == 'csv':
                # CSVの場合、エンコーディングを自動判定
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(io.BytesIO(file_bytes), encoding='shift_jis')
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(io.BytesIO(file_bytes))
            else:
                return None

            # 基本的なデータ検証
            if df.empty:
                return None

            return df

        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return None

    @staticmethod
    def dataframe_to_csv(df: pd.DataFrame, encoding: str = 'utf-8-sig') -> bytes:
        """
        DataFrameをCSVバイトデータに変換

        Parameters:
        -----------
        df : pd.DataFrame
            変換するDataFrame
        encoding : str
            エンコーディング（デフォルト: utf-8-sig）

        Returns:
        --------
        bytes
            CSVのバイトデータ
        """
        try:
            csv_string = df.to_csv(index=False, encoding=encoding)
            return csv_string.encode(encoding)
        except Exception as e:
            print(f"Error converting to CSV: {str(e)}")
            return None

    @staticmethod
    def dataframe_to_excel(df: pd.DataFrame) -> bytes:
        """
        DataFrameをExcelバイトデータに変換

        Parameters:
        -----------
        df : pd.DataFrame
            変換するDataFrame

        Returns:
        --------
        bytes
            Excelのバイトデータ
        """
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            print(f"Error converting to Excel: {str(e)}")
            return None

    @staticmethod
    def validate_file_size(file_bytes: bytes, max_size_mb: int = 16) -> bool:
        """
        ファイルサイズの検証

        Parameters:
        -----------
        file_bytes : bytes
            検証するファイルのバイトデータ
        max_size_mb : int
            最大ファイルサイズ（MB）

        Returns:
        --------
        bool
            サイズが制限内ならTrue
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        return len(file_bytes) <= max_size_bytes
