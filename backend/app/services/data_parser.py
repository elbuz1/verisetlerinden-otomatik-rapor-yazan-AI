import pandas as pd
import json
import chardet
from pathlib import Path
from typing import Optional


class DataParser:
    SUPPORTED_TYPES = {"csv", "xlsx", "xls", "json"}
    MAX_PREVIEW_ROWS = 100

    def parse(self, file_path: str, file_type: str) -> pd.DataFrame:
        file_type = file_type.lower().strip(".")
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Desteklenmeyen dosya tipi: {file_type}")

        parsers = {
            "csv": self._parse_csv,
            "xlsx": self._parse_excel,
            "xls": self._parse_excel,
            "json": self._parse_json,
        }
        return parsers[file_type](file_path)

    def _parse_csv(self, file_path: str) -> pd.DataFrame:
        encoding = self._detect_encoding(file_path)
        for sep in [",", ";", "\t", "|"]:
            try:
                df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue
        return pd.read_csv(file_path, encoding=encoding)

    def _parse_excel(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path, engine="openpyxl")

    def _parse_json(self, file_path: str) -> pd.DataFrame:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict):
            if "data" in data:
                return pd.DataFrame(data["data"])
            return pd.DataFrame([data])
        raise ValueError("JSON formatı tanınamadı")

    def _detect_encoding(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            raw = f.read(10000)
        result = chardet.detect(raw)
        return result["encoding"] or "utf-8"

    def get_preview(self, df: pd.DataFrame, rows: int = 20) -> dict:
        preview_df = df.head(rows)
        return {
            "columns": list(df.columns),
            "data": preview_df.to_dict(orient="records"),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "shape": {"rows": len(df), "columns": len(df.columns)},
        }

    def get_columns_info(self, df: pd.DataFrame) -> list[dict]:
        info = []
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "null_percentage": round(df[col].isnull().sum() / len(df) * 100, 2),
                "unique_count": int(df[col].nunique()),
                "sample_values": [str(v) for v in df[col].dropna().head(5).tolist()],
            }
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["min"] = float(df[col].min()) if not df[col].isnull().all() else None
                col_info["max"] = float(df[col].max()) if not df[col].isnull().all() else None
                col_info["mean"] = float(df[col].mean()) if not df[col].isnull().all() else None
                col_info["is_numeric"] = True
            else:
                col_info["is_numeric"] = False
            info.append(col_info)
        return info


data_parser = DataParser()
