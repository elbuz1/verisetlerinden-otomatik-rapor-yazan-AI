import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Optional
import warnings

warnings.filterwarnings("ignore")


class AnalysisService:

    def run_full_analysis(self, df: pd.DataFrame) -> dict:
        numeric_df = df.select_dtypes(include=[np.number])
        categorical_df = df.select_dtypes(include=["object", "category"])

        return {
            "basic_stats": self._basic_statistics(df, numeric_df),
            "missing_data": self._missing_data_analysis(df),
            "correlation_matrix": self._correlation_analysis(numeric_df),
            "distribution_info": self._distribution_analysis(numeric_df),
            "trend_analysis": self._trend_analysis(df, numeric_df),
            "anomalies": self._anomaly_detection(numeric_df),
            "category_analysis": self._category_analysis(categorical_df),
            "column_analysis": self._column_deep_analysis(df),
            "data_quality_score": self._data_quality_score(df),
        }

    def _basic_statistics(self, df: pd.DataFrame, numeric_df: pd.DataFrame) -> dict:
        result = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_df.columns),
            "categorical_columns": len(df.select_dtypes(include=["object", "category"]).columns),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "duplicate_rows": int(df.duplicated().sum()),
            "columns": {},
        }

        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if len(series) == 0:
                continue
            result["columns"][col] = {
                "count": int(series.count()),
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "std": round(float(series.std()), 4),
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
                "q25": round(float(series.quantile(0.25)), 4),
                "q75": round(float(series.quantile(0.75)), 4),
                "iqr": round(float(series.quantile(0.75) - series.quantile(0.25)), 4),
                "skewness": round(float(series.skew()), 4),
                "kurtosis": round(float(series.kurtosis()), 4),
                "cv": round(float(series.std() / series.mean() * 100), 2) if series.mean() != 0 else 0,
                "range": round(float(series.max() - series.min()), 4),
            }

        return result

    def _missing_data_analysis(self, df: pd.DataFrame) -> dict:
        missing = df.isnull().sum()
        total = len(df)
        missing_info = {}

        for col in df.columns:
            miss_count = int(missing[col])
            if miss_count > 0:
                missing_info[col] = {
                    "count": miss_count,
                    "percentage": round(miss_count / total * 100, 2),
                    "severity": (
                        "dusuk" if miss_count / total < 0.05
                        else "orta" if miss_count / total < 0.2
                        else "yuksek"
                    ),
                }

        return {
            "total_missing": int(missing.sum()),
            "total_cells": int(total * len(df.columns)),
            "missing_percentage": round(missing.sum() / (total * len(df.columns)) * 100, 2),
            "columns_with_missing": missing_info,
            "complete_rows": int((~df.isnull().any(axis=1)).sum()),
            "complete_rows_percentage": round((~df.isnull().any(axis=1)).sum() / total * 100, 2),
        }

    def _correlation_analysis(self, numeric_df: pd.DataFrame) -> dict:
        if len(numeric_df.columns) < 2:
            return {"matrix": {}, "strong_correlations": []}

        corr = numeric_df.corr()
        matrix = {}
        for col in corr.columns:
            matrix[col] = {c: round(float(v), 4) for c, v in corr[col].items()}

        strong = []
        for i, col1 in enumerate(corr.columns):
            for j, col2 in enumerate(corr.columns):
                if i < j:
                    val = abs(corr.iloc[i, j])
                    if val > 0.7 and not np.isnan(val):
                        strong.append({
                            "column1": col1,
                            "column2": col2,
                            "value": round(float(corr.iloc[i, j]), 4),
                            "strength": "cok_guclu" if val > 0.9 else "guclu",
                            "direction": "pozitif" if corr.iloc[i, j] > 0 else "negatif",
                        })

        strong.sort(key=lambda x: abs(x["value"]), reverse=True)
        return {"matrix": matrix, "strong_correlations": strong}

    def _distribution_analysis(self, numeric_df: pd.DataFrame) -> dict:
        distributions = {}
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if len(series) < 10:
                continue

            try:
                stat_normal, p_normal = stats.normaltest(series)
            except Exception:
                stat_normal, p_normal = 0, 0

            hist, bin_edges = np.histogram(series, bins=min(30, len(series) // 5 + 1))

            distributions[col] = {
                "is_normal": bool(p_normal > 0.05),
                "normality_p_value": round(float(p_normal), 6),
                "skewness": round(float(series.skew()), 4),
                "skew_direction": (
                    "simetrik" if abs(series.skew()) < 0.5
                    else "saga_carpik" if series.skew() > 0
                    else "sola_carpik"
                ),
                "kurtosis": round(float(series.kurtosis()), 4),
                "kurtosis_type": (
                    "normal" if abs(series.kurtosis()) < 1
                    else "sivri" if series.kurtosis() > 0
                    else "basik"
                ),
                "histogram": {
                    "counts": hist.tolist(),
                    "bins": [round(float(b), 4) for b in bin_edges.tolist()],
                },
            }

        return distributions

    def _trend_analysis(self, df: pd.DataFrame, numeric_df: pd.DataFrame) -> dict:
        trends = {}
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if len(series) < 5:
                continue

            values = series.values
            x = np.arange(len(values))

            try:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            except Exception:
                continue

            segments = min(4, len(values) // 10 + 1)
            if segments >= 2:
                segment_size = len(values) // segments
                segment_means = [
                    float(np.mean(values[i * segment_size:(i + 1) * segment_size]))
                    for i in range(segments)
                ]
                changes = [
                    round((segment_means[i] - segment_means[i - 1]) / abs(segment_means[i - 1]) * 100, 2)
                    if segment_means[i - 1] != 0 else 0
                    for i in range(1, len(segment_means))
                ]
            else:
                segment_means = [float(np.mean(values))]
                changes = []

            overall_change = (
                round((float(values[-1]) - float(values[0])) / abs(float(values[0])) * 100, 2)
                if values[0] != 0 else 0
            )

            if abs(slope) < std_err:
                direction = "yatay"
            elif slope > 0:
                direction = "yukari"
            else:
                direction = "asagi"

            trends[col] = {
                "direction": direction,
                "slope": round(float(slope), 6),
                "r_squared": round(float(r_value ** 2), 4),
                "p_value": round(float(p_value), 6),
                "is_significant": bool(p_value < 0.05),
                "overall_change_percent": overall_change,
                "segment_means": [round(v, 4) for v in segment_means],
                "segment_changes_percent": changes,
                "volatility": round(float(series.std() / series.mean() * 100), 2) if series.mean() != 0 else 0,
            }

        return trends

    def _anomaly_detection(self, numeric_df: pd.DataFrame) -> dict:
        anomalies = {"by_column": {}, "total_anomalies": 0}

        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if len(series) < 10:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outliers = series[(series < lower) | (series > upper)]
            z_scores = np.abs(stats.zscore(series))
            z_outliers = series[z_scores > 3]

            if len(outliers) > 0:
                anomalies["by_column"][col] = {
                    "iqr_outlier_count": int(len(outliers)),
                    "iqr_outlier_percentage": round(len(outliers) / len(series) * 100, 2),
                    "z_score_outlier_count": int(len(z_outliers)),
                    "lower_bound": round(float(lower), 4),
                    "upper_bound": round(float(upper), 4),
                    "outlier_values": sorted([round(float(v), 4) for v in outliers.head(10).tolist()]),
                    "severity": (
                        "dusuk" if len(outliers) / len(series) < 0.02
                        else "orta" if len(outliers) / len(series) < 0.05
                        else "yuksek"
                    ),
                }
                anomalies["total_anomalies"] += len(outliers)

        if len(numeric_df.columns) >= 2 and len(numeric_df.dropna()) >= 20:
            try:
                clean_df = numeric_df.dropna()
                scaler = StandardScaler()
                scaled = scaler.fit_transform(clean_df)
                iso_forest = IsolationForest(contamination=0.05, random_state=42)
                predictions = iso_forest.fit_predict(scaled)
                multi_anomaly_count = int((predictions == -1).sum())
                anomalies["multivariate"] = {
                    "method": "isolation_forest",
                    "anomaly_count": multi_anomaly_count,
                    "anomaly_percentage": round(multi_anomaly_count / len(clean_df) * 100, 2),
                }
            except Exception:
                pass

        return anomalies

    def _category_analysis(self, categorical_df: pd.DataFrame) -> dict:
        analysis = {}
        for col in categorical_df.columns:
            series = categorical_df[col].dropna()
            if len(series) == 0:
                continue

            value_counts = series.value_counts()
            total = len(series)

            analysis[col] = {
                "unique_count": int(series.nunique()),
                "most_common": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                "most_common_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                "most_common_percentage": round(
                    value_counts.iloc[0] / total * 100, 2
                ) if len(value_counts) > 0 else 0,
                "least_common": str(value_counts.index[-1]) if len(value_counts) > 0 else None,
                "distribution": {
                    str(k): {"count": int(v), "percentage": round(v / total * 100, 2)}
                    for k, v in value_counts.head(20).items()
                },
                "entropy": round(float(stats.entropy(value_counts.values / total)), 4),
                "is_high_cardinality": bool(series.nunique() > 50),
            }

        return analysis

    def _column_deep_analysis(self, df: pd.DataFrame) -> dict:
        analysis = {}
        for col in df.columns:
            series = df[col]
            col_analysis = {
                "name": col,
                "dtype": str(series.dtype),
                "total": len(series),
                "non_null": int(series.count()),
                "null_count": int(series.isnull().sum()),
                "unique_count": int(series.nunique()),
                "uniqueness_ratio": round(series.nunique() / len(series) * 100, 2),
            }

            if pd.api.types.is_numeric_dtype(series):
                s = series.dropna()
                if len(s) > 0:
                    col_analysis["type"] = "numeric"
                    col_analysis["has_negative"] = bool((s < 0).any())
                    col_analysis["has_zero"] = bool((s == 0).any())
                    col_analysis["is_integer_like"] = bool((s == s.astype(int)).all()) if not s.empty else False
            elif pd.api.types.is_datetime64_any_dtype(series):
                col_analysis["type"] = "datetime"
                s = series.dropna()
                if len(s) > 0:
                    col_analysis["min_date"] = str(s.min())
                    col_analysis["max_date"] = str(s.max())
            else:
                col_analysis["type"] = "categorical"
                s = series.dropna().astype(str)
                if len(s) > 0:
                    col_analysis["avg_length"] = round(s.str.len().mean(), 1)
                    col_analysis["max_length"] = int(s.str.len().max())

            analysis[col] = col_analysis

        return analysis

    def _data_quality_score(self, df: pd.DataFrame) -> dict:
        scores = {}

        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        completeness = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 100
        scores["completeness"] = round(completeness, 1)

        duplicate_ratio = df.duplicated().sum() / len(df) * 100 if len(df) > 0 else 0
        scores["uniqueness"] = round(100 - duplicate_ratio, 1)

        consistency_score = 100
        for col in df.columns:
            if df[col].dtype == "object":
                stripped = df[col].dropna().astype(str).str.strip()
                if not stripped.equals(df[col].dropna().astype(str)):
                    consistency_score -= 5
        scores["consistency"] = max(round(consistency_score, 1), 0)

        scores["overall"] = round(
            (scores["completeness"] * 0.4 + scores["uniqueness"] * 0.3 + scores["consistency"] * 0.3), 1
        )

        if scores["overall"] >= 90:
            scores["grade"] = "A"
            scores["label"] = "Mükemmel"
        elif scores["overall"] >= 75:
            scores["grade"] = "B"
            scores["label"] = "İyi"
        elif scores["overall"] >= 60:
            scores["grade"] = "C"
            scores["label"] = "Orta"
        else:
            scores["grade"] = "D"
            scores["label"] = "Düşük"

        return scores


analysis_service = AnalysisService()
