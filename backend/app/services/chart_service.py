import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import pandas as pd
import numpy as np
import os
import uuid
from pathlib import Path

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
sns.set_theme(style="whitegrid", palette="husl")

CHART_COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#818cf8", "#4f46e5",
                "#7c3aed", "#5b21b6", "#3b82f6", "#06b6d4", "#10b981", "#f59e0b"]


class ChartService:

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "reports", "generated", "charts"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_all_charts(self, df: pd.DataFrame, analysis: dict, session_id: str) -> dict:
        chart_dir = os.path.join(self.output_dir, session_id)
        os.makedirs(chart_dir, exist_ok=True)

        charts = {}

        numeric_df = df.select_dtypes(include=[np.number])
        categorical_df = df.select_dtypes(include=["object", "category"])

        if len(numeric_df.columns) > 0:
            charts["distribution"] = self._create_distribution_charts(numeric_df, chart_dir)

        if len(numeric_df.columns) >= 2:
            charts["correlation"] = self._create_correlation_heatmap(numeric_df, chart_dir)

        if len(numeric_df.columns) > 0:
            charts["boxplot"] = self._create_boxplots(numeric_df, chart_dir)
            charts["trend"] = self._create_trend_charts(numeric_df, chart_dir)

        if len(categorical_df.columns) > 0:
            charts["category"] = self._create_category_charts(categorical_df, chart_dir)

        missing = analysis.get("missing_data", {})
        if missing.get("total_missing", 0) > 0:
            charts["missing"] = self._create_missing_data_chart(df, chart_dir)

        quality = analysis.get("data_quality_score", {})
        if quality:
            charts["quality"] = self._create_quality_gauge(quality, chart_dir)

        charts["overview"] = self._create_overview_chart(df, analysis, chart_dir)

        return charts

    def _create_distribution_charts(self, numeric_df: pd.DataFrame, chart_dir: str) -> list[str]:
        paths = []
        cols = list(numeric_df.columns)[:8]
        n_cols = len(cols)
        n_rows = (n_cols + 1) // 2

        fig, axes = plt.subplots(n_rows, 2, figsize=(14, 4 * n_rows))
        if n_rows == 1:
            axes = [axes]
        axes_flat = [ax for row in axes for ax in (row if hasattr(row, "__iter__") else [row])]

        for i, col in enumerate(cols):
            ax = axes_flat[i]
            data = numeric_df[col].dropna()
            ax.hist(data, bins=min(30, len(data) // 5 + 1), color=CHART_COLORS[i % len(CHART_COLORS)],
                    alpha=0.7, edgecolor="white")
            ax.set_title(f"{col} Dağılımı", fontsize=11, fontweight="bold")
            ax.set_xlabel(col, fontsize=9)
            ax.set_ylabel("Frekans", fontsize=9)
            ax.tick_params(labelsize=8)

        for i in range(len(cols), len(axes_flat)):
            axes_flat[i].set_visible(False)

        plt.tight_layout()
        path = os.path.join(chart_dir, "distributions.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        paths.append(path)
        return paths

    def _create_correlation_heatmap(self, numeric_df: pd.DataFrame, chart_dir: str) -> str:
        corr = numeric_df.corr()
        size = max(8, len(corr.columns) * 0.8)
        fig, ax = plt.subplots(figsize=(size, size * 0.8))

        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                    center=0, square=True, linewidths=0.5, ax=ax,
                    cbar_kws={"shrink": 0.8}, vmin=-1, vmax=1)
        ax.set_title("Korelasyon Matrisi", fontsize=14, fontweight="bold", pad=20)
        plt.xticks(rotation=45, ha="right", fontsize=9)
        plt.yticks(fontsize=9)

        plt.tight_layout()
        path = os.path.join(chart_dir, "correlation_heatmap.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _create_boxplots(self, numeric_df: pd.DataFrame, chart_dir: str) -> str:
        cols = list(numeric_df.columns)[:10]
        fig, ax = plt.subplots(figsize=(max(10, len(cols) * 1.2), 6))

        data_to_plot = [numeric_df[col].dropna().values for col in cols]
        bp = ax.boxplot(data_to_plot, tick_labels=cols, patch_artist=True, notch=True)

        for i, patch in enumerate(bp["boxes"]):
            patch.set_facecolor(CHART_COLORS[i % len(CHART_COLORS)])
            patch.set_alpha(0.7)

        ax.set_title("Sayısal Değişkenler - Kutu Grafikleri", fontsize=14, fontweight="bold")
        ax.set_ylabel("Değer", fontsize=10)
        plt.xticks(rotation=45, ha="right", fontsize=9)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        path = os.path.join(chart_dir, "boxplots.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _create_trend_charts(self, numeric_df: pd.DataFrame, chart_dir: str) -> list[str]:
        paths = []
        cols = list(numeric_df.columns)[:4]

        fig, axes = plt.subplots(len(cols), 1, figsize=(14, 4 * len(cols)))
        if len(cols) == 1:
            axes = [axes]

        for i, col in enumerate(cols):
            ax = axes[i]
            data = numeric_df[col].dropna().values
            x = np.arange(len(data))

            ax.plot(x, data, color=CHART_COLORS[i % len(CHART_COLORS)], alpha=0.6, linewidth=1)

            window = max(5, len(data) // 20)
            if len(data) > window:
                rolling = pd.Series(data).rolling(window=window, center=True).mean()
                ax.plot(x, rolling, color=CHART_COLORS[(i + 3) % len(CHART_COLORS)],
                        linewidth=2.5, label=f"Hareketli Ort. ({window})")

            from scipy.stats import linregress
            slope, intercept, _, _, _ = linregress(x, data)
            ax.plot(x, slope * x + intercept, "--", color="#ef4444", linewidth=1.5,
                    alpha=0.8, label="Trend")

            ax.set_title(f"{col} - Trend Analizi", fontsize=11, fontweight="bold")
            ax.set_xlabel("Gözlem Sırası", fontsize=9)
            ax.set_ylabel(col, fontsize=9)
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)

        plt.tight_layout()
        path = os.path.join(chart_dir, "trends.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        paths.append(path)
        return paths

    def _create_category_charts(self, categorical_df: pd.DataFrame, chart_dir: str) -> list[str]:
        paths = []
        cols = list(categorical_df.columns)[:4]

        for col in cols:
            value_counts = categorical_df[col].value_counts().head(10)
            fig, ax = plt.subplots(figsize=(10, 6))

            bars = ax.barh(range(len(value_counts)), value_counts.values,
                           color=[CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(value_counts))])
            ax.set_yticks(range(len(value_counts)))
            ax.set_yticklabels([str(v)[:30] for v in value_counts.index], fontsize=9)
            ax.set_xlabel("Sayı", fontsize=10)
            ax.set_title(f"{col} - Kategori Dağılımı", fontsize=12, fontweight="bold")

            for bar, val in zip(bars, value_counts.values):
                ax.text(bar.get_width() + max(value_counts.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                        f"{val:,}", va="center", fontsize=9)

            ax.grid(axis="x", alpha=0.3)
            plt.tight_layout()
            path = os.path.join(chart_dir, f"category_{col}.png")
            fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            paths.append(path)

        return paths

    def _create_missing_data_chart(self, df: pd.DataFrame, chart_dir: str) -> str:
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=True)

        if len(missing) == 0:
            return ""

        fig, ax = plt.subplots(figsize=(10, max(4, len(missing) * 0.5)))
        colors = ["#ef4444" if v / len(df) > 0.2 else "#f59e0b" if v / len(df) > 0.05 else "#10b981"
                   for v in missing.values]
        bars = ax.barh(range(len(missing)), missing.values, color=colors)
        ax.set_yticks(range(len(missing)))
        ax.set_yticklabels(missing.index, fontsize=9)
        ax.set_xlabel("Eksik Değer Sayısı", fontsize=10)
        ax.set_title("Eksik Veri Analizi", fontsize=13, fontweight="bold")

        for bar, val in zip(bars, missing.values):
            pct = val / len(df) * 100
            ax.text(bar.get_width() + max(missing.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{val:,} (%{pct:.1f})", va="center", fontsize=9)

        ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        path = os.path.join(chart_dir, "missing_data.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _create_quality_gauge(self, quality: dict, chart_dir: str) -> str:
        fig, ax = plt.subplots(figsize=(8, 4))
        score = quality.get("overall", 0)

        categories = ["Tamlık", "Teklik", "Tutarlılık", "Genel"]
        values = [
            quality.get("completeness", 0),
            quality.get("uniqueness", 0),
            quality.get("consistency", 0),
            score,
        ]
        colors = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"]

        bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor="white", linewidth=1)
        ax.set_ylim(0, 110)
        ax.set_title(f"Veri Kalitesi Skoru: {score}/100 ({quality.get('label', '')})",
                     fontsize=13, fontweight="bold")
        ax.set_ylabel("Skor", fontsize=10)
        ax.axhline(y=75, color="#10b981", linestyle="--", alpha=0.5, label="İyi (75)")
        ax.axhline(y=50, color="#f59e0b", linestyle="--", alpha=0.5, label="Orta (50)")

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                    f"{val:.0f}", ha="center", fontsize=11, fontweight="bold")

        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        path = os.path.join(chart_dir, "quality_score.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _create_overview_chart(self, df: pd.DataFrame, analysis: dict, chart_dir: str) -> str:
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle("Veri Seti Genel Bakış", fontsize=16, fontweight="bold", y=0.98)

        basic = analysis.get("basic_stats", {})
        ax1 = fig.add_subplot(2, 3, 1)
        metrics = ["Satır", "Sütun", "Sayısal", "Kategorik"]
        values = [
            basic.get("total_rows", 0),
            basic.get("total_columns", 0),
            basic.get("numeric_columns", 0),
            basic.get("categorical_columns", 0),
        ]
        ax1.bar(metrics, values, color=CHART_COLORS[:4])
        ax1.set_title("Temel Metrikler", fontsize=10, fontweight="bold")
        for i, v in enumerate(values):
            ax1.text(i, v + max(values) * 0.02, f"{v:,}", ha="center", fontsize=9)

        numeric_df = df.select_dtypes(include=[np.number])
        ax2 = fig.add_subplot(2, 3, 2)
        null_pcts = [df[col].isnull().sum() / len(df) * 100 for col in df.columns]
        non_null_pcts = [100 - p for p in null_pcts]
        total_null = sum(null_pcts) / len(null_pcts) if null_pcts else 0
        ax2.pie([100 - total_null, total_null], labels=["Dolu", "Eksik"],
                colors=["#10b981", "#ef4444"], autopct="%1.1f%%", startangle=90)
        ax2.set_title("Veri Tamlığı", fontsize=10, fontweight="bold")

        ax3 = fig.add_subplot(2, 3, 3)
        dtypes = df.dtypes.value_counts()
        ax3.pie(dtypes.values, labels=[str(d) for d in dtypes.index],
                colors=CHART_COLORS[:len(dtypes)], autopct="%1.0f%%")
        ax3.set_title("Veri Tipleri", fontsize=10, fontweight="bold")

        if len(numeric_df.columns) > 0:
            ax4 = fig.add_subplot(2, 3, 4)
            means = {col: numeric_df[col].mean() for col in list(numeric_df.columns)[:6]}
            ax4.bar(means.keys(), means.values(), color=CHART_COLORS[:len(means)])
            ax4.set_title("Ortalama Değerler", fontsize=10, fontweight="bold")
            plt.sca(ax4)
            plt.xticks(rotation=45, ha="right", fontsize=7)

        if len(numeric_df.columns) > 0:
            ax5 = fig.add_subplot(2, 3, 5)
            stds = {col: numeric_df[col].std() for col in list(numeric_df.columns)[:6]}
            ax5.bar(stds.keys(), stds.values(), color=CHART_COLORS[3:3 + len(stds)])
            ax5.set_title("Standart Sapma", fontsize=10, fontweight="bold")
            plt.sca(ax5)
            plt.xticks(rotation=45, ha="right", fontsize=7)

        ax6 = fig.add_subplot(2, 3, 6)
        quality = analysis.get("data_quality_score", {})
        score = quality.get("overall", 0)
        ax6.text(0.5, 0.5, f"{score:.0f}", transform=ax6.transAxes,
                 fontsize=48, fontweight="bold", ha="center", va="center",
                 color="#10b981" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444")
        ax6.text(0.5, 0.2, f"Kalite: {quality.get('label', '')}", transform=ax6.transAxes,
                 fontsize=12, ha="center", va="center")
        ax6.set_title("Kalite Skoru", fontsize=10, fontweight="bold")
        ax6.set_xlim(0, 1)
        ax6.set_ylim(0, 1)
        ax6.axis("off")

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        path = os.path.join(chart_dir, "overview.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path


chart_service = ChartService()
