# =============================================================================
# analytics/charts.py
# Chart Generation Module — Matplotlib / Seaborn static charts
# Used by both Flask (image serving) and report generation
# =============================================================================

import os
import io
import base64

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# ── Colour palette ────────────────────────────────────────────────────────────
GREEN_DARK   = "#1B5E20"
GREEN_MID    = "#2E7D32"
GREEN_LIGHT  = "#43A047"
GREEN_PALE   = "#C8E6C9"
AMBER        = "#F9A825"
BLUE         = "#0277BD"
ORANGE       = "#E65100"

TAB20 = plt.cm.tab20(np.linspace(0, 1, 22))

CHART_STYLE = {
    "axes.facecolor":    "#F9FBF9",
    "figure.facecolor":  "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.35,
    "grid.linestyle":    "--",
    "font.family":       "DejaVu Sans",
}


def _fig_to_b64(fig) -> str:
    """Convert a Matplotlib figure to a base-64 PNG string (for <img> tags)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64


def _save_fig(fig, path: str):
    """Save figure to disk and close it."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)


# ── 1. Crop Distribution Pie ──────────────────────────────────────────────────
def crop_distribution_chart(df: pd.DataFrame, as_b64=True):
    counts = df["label"].value_counts()
    colors = TAB20[:len(counts)]

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            counts.values, labels=counts.index,
            autopct="%1.1f%%", colors=colors,
            startangle=140, pctdistance=0.78,
            wedgeprops={"linewidth": 1.5, "edgecolor": "white", "width": 0.65},
        )
        for t in texts:
            t.set_fontsize(8)
        for at in autotexts:
            at.set_fontsize(7.5)
            at.set_fontweight("bold")
        ax.set_title("Crop Distribution", fontsize=14,
                     fontweight="bold", pad=15, color=GREEN_DARK)
        fig.tight_layout()

    return _fig_to_b64(fig) if as_b64 else fig


# ── 2. Avg Soil Nutrients Bar ─────────────────────────────────────────────────
def nutrient_bar_chart(df: pd.DataFrame, as_b64=True):
    means = df.groupby("label")[["N", "P", "K"]].mean().reset_index()
    x     = np.arange(len(means))
    w     = 0.27

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(13, 5))
        ax.bar(x - w, means["N"], w, label="Nitrogen (N)",   color=GREEN_MID,  edgecolor="white")
        ax.bar(x,     means["P"], w, label="Phosphorus (P)", color=AMBER,      edgecolor="white")
        ax.bar(x + w, means["K"], w, label="Potassium (K)",  color=BLUE,       edgecolor="white")
        ax.set_xticks(x)
        ax.set_xticklabels(means["label"], rotation=40, ha="right", fontsize=9)
        ax.set_ylabel("Average (kg/ha)", fontsize=10)
        ax.set_title("Average Soil Nutrients by Crop", fontsize=14,
                     fontweight="bold", color=GREEN_DARK)
        ax.legend(fontsize=9)
        fig.tight_layout()

    return _fig_to_b64(fig) if as_b64 else fig


# ── 3. Rainfall vs Crop Scatter ───────────────────────────────────────────────
def rainfall_scatter_chart(df: pd.DataFrame, as_b64=True):
    crops  = sorted(df["label"].unique())
    colors = TAB20[:len(crops)]
    cmap   = dict(zip(crops, colors))

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(11, 5))
        for crop in crops:
            sub = df[df["label"] == crop]
            ax.scatter(sub["rainfall"], [crop] * len(sub),
                       color=cmap[crop], alpha=0.55, s=18, edgecolors="none")
        ax.set_xlabel("Rainfall (mm)", fontsize=10)
        ax.set_ylabel("Crop", fontsize=10)
        ax.set_title("Rainfall Distribution by Crop", fontsize=14,
                     fontweight="bold", color=GREEN_DARK)
        ax.tick_params(axis="y", labelsize=8)
        fig.tight_layout()

    return _fig_to_b64(fig) if as_b64 else fig


# ── 4. Soil pH Box Plot ───────────────────────────────────────────────────────
def ph_boxplot_chart(df: pd.DataFrame, as_b64=True):
    crops = sorted(df["label"].unique())
    data  = [df[df["label"] == c]["ph"].values for c in crops]
    colors = plt.cm.Greens(np.linspace(0.3, 0.85, len(crops)))

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(13, 5))
        bp = ax.boxplot(data, patch_artist=True, labels=crops,
                        medianprops={"color": GREEN_DARK, "linewidth": 2})
        for patch, clr in zip(bp["boxes"], colors):
            patch.set_facecolor(clr)
        ax.set_xticklabels(crops, rotation=40, ha="right", fontsize=9)
        ax.set_ylabel("Soil pH", fontsize=10)
        ax.set_title("Soil pH Distribution by Crop", fontsize=14,
                     fontweight="bold", color=GREEN_DARK)
        fig.tight_layout()

    return _fig_to_b64(fig) if as_b64 else fig


# ── 5. Feature Correlation Heatmap ────────────────────────────────────────────
def correlation_heatmap(df: pd.DataFrame, as_b64=True):
    cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    corr = df[cols].corr()

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn",
                    ax=ax, linewidths=0.5, square=True,
                    cbar_kws={"shrink": 0.75},
                    annot_kws={"size": 9})
        ax.set_title("Feature Correlation Matrix", fontsize=14,
                     fontweight="bold", color=GREEN_DARK)
        fig.tight_layout()

    return _fig_to_b64(fig) if as_b64 else fig


# ── 6. Previous Crop Frequency Bar ───────────────────────────────────────────
def prev_crop_bar_chart(df: pd.DataFrame, as_b64=True):
    counts = df["previous_crop"].value_counts()
    colors = plt.cm.Greens(np.linspace(0.35, 0.85, len(counts)))

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(counts.index, counts.values,
                      color=colors, edgecolor="white", linewidth=1.2)
        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                    str(val), ha="center", va="bottom", fontsize=10, fontweight="bold")
        ax.set_ylabel("Count", fontsize=10)
        ax.set_title("Previous Crop Frequency", fontsize=14,
                     fontweight="bold", color=GREEN_DARK)
        ax.set_ylim(0, counts.max() * 1.15)
        fig.tight_layout()

    return _fig_to_b64(fig) if as_b64 else fig


# ── 7. Confusion Matrix Heatmap ───────────────────────────────────────────────
def confusion_matrix_chart(cm: list, class_names: list,
                            save_path: str = None, as_b64=True):
    cm_arr = np.array(cm)

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(14, 10))
        sns.heatmap(cm_arr, annot=True, fmt="d", cmap="YlOrRd",
                    xticklabels=class_names, yticklabels=class_names,
                    ax=ax, linewidths=0.4, cbar_kws={"shrink": 0.75},
                    annot_kws={"size": 8})
        ax.set_title("Confusion Matrix", fontsize=15,
                     fontweight="bold", pad=15, color=GREEN_DARK)
        ax.set_xlabel("Predicted Label", fontsize=11)
        ax.set_ylabel("True Label", fontsize=11)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        fig.tight_layout()

    if save_path:
        _save_fig(fig, save_path)
        return save_path

    return _fig_to_b64(fig) if as_b64 else fig


# ── 8. Feature Importance Bar ─────────────────────────────────────────────────
def feature_importance_chart(importances: list, feature_names: list,
                              save_path: str = None, as_b64=True):
    imp_arr = np.array(importances)
    idx     = np.argsort(imp_arr)
    colors  = plt.cm.RdYlGn(np.linspace(0.25, 0.85, len(idx)))

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.barh(
            [feature_names[i] for i in idx],
            imp_arr[idx],
            color=colors[idx], edgecolor="white", linewidth=1
        )
        for bar, val in zip(bars, imp_arr[idx]):
            ax.text(bar.get_width() + 0.004, bar.get_y() + bar.get_height() / 2,
                    f"{val:.3f}", va="center", fontsize=9)
        ax.set_xlabel("Feature Importance Score", fontsize=10)
        ax.set_title("Feature Importance — Random Forest", fontsize=14,
                     fontweight="bold", color=GREEN_DARK)
        ax.set_xlim(0, imp_arr.max() * 1.22)
        fig.tight_layout()

    if save_path:
        _save_fig(fig, save_path)
        return save_path

    return _fig_to_b64(fig) if as_b64 else fig


# ── 9. Top-5 Prediction Probability Bar ──────────────────────────────────────
def top5_probability_chart(top5: list, as_b64=True):
    """top5: list of {"crop": str, "prob": float}"""
    crops  = [t["crop"] for t in top5][::-1]
    probs  = [t["prob"] for t in top5][::-1]
    colors = plt.cm.Greens(np.linspace(0.3, 0.85, len(crops)))

    with plt.rc_context(CHART_STYLE):
        fig, ax = plt.subplots(figsize=(7, 3.2))
        bars = ax.barh(crops, probs, color=colors, edgecolor="white")
        for bar, val in zip(bars, probs):
            ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2,
                    f"{val}%", va="center", fontsize=10, fontweight="bold")
        ax.set_xlabel("Probability (%)", fontsize=10)
        ax.set_xlim(0, max(probs) * 1.25)
        ax.set_title("Top 5 Crop Probabilities", fontsize=12,
                     fontweight="bold", color=GREEN_DARK)
        fig.tight_layout()

    return _fig_to_b64(fig) if as_b64 else fig


# ── Batch save all training charts ────────────────────────────────────────────
def save_all_charts(df: pd.DataFrame, cm: list, class_names: list,
                    importances: list, feature_names: list, out_dir: str):
    """Generate and save all charts to disk. Called from train_model.py."""
    os.makedirs(out_dir, exist_ok=True)

    confusion_matrix_chart(
        cm, class_names,
        save_path=os.path.join(out_dir, "confusion_matrix.png"), as_b64=False)

    feature_importance_chart(
        importances, feature_names,
        save_path=os.path.join(out_dir, "feature_importance.png"), as_b64=False)

    # Save analytics charts
    for name, fn in [
        ("crop_distribution",   lambda: crop_distribution_chart(df, as_b64=False)),
        ("nutrient_bar",        lambda: nutrient_bar_chart(df, as_b64=False)),
        ("rainfall_scatter",    lambda: rainfall_scatter_chart(df, as_b64=False)),
        ("ph_boxplot",          lambda: ph_boxplot_chart(df, as_b64=False)),
        ("correlation_heatmap", lambda: correlation_heatmap(df, as_b64=False)),
        ("prev_crop_bar",       lambda: prev_crop_bar_chart(df, as_b64=False)),
    ]:
        _save_fig(fn(), os.path.join(out_dir, f"{name}.png"))

    print(f"✅ All charts saved to {out_dir}/")
