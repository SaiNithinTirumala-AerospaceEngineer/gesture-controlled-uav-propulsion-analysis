"""
gesture_performance.py
----------------------
Gesture recognition performance analysis for the quadrotor UAV
gesture control pipeline.

Analyses recognition accuracy across 8 gesture classes using three
evaluation conditions:
  1. FB Method  — Feature-based method (FFT + position features)
  2. ML Method  — Machine learning classifier (threshold + trained model)
  3. Flying UAV — Recognition rate under real flight vibration and noise

Generates:
  - Grouped bar chart comparing all three methods per gesture
  - Confusion matrix (ML method — highest accuracy)
  - Method comparison radar chart
  - Sensor threshold distribution plot

Sources:
  - Tables 2.6.1, 2.6.2, 2.6.3 from project report
  - Togo & Ukida (2022) SICE Journal — FB vs ML method comparison
  - Lee & Yu (2023) Sensors — wearable gesture recognition benchmark

Inputs : data/gesture_recognition_data.csv
Outputs: results/gesture_accuracy_bar.png
         results/gesture_confusion_matrix.png
         results/gesture_method_comparison.png
         results/gesture_sensor_thresholds.png

Usage:
    python src/gesture_performance.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

# ── Paths ─────────────────────────────────────────────────────────────────────
SRC_DIR     = os.path.dirname(__file__)
DATA_PATH   = os.path.join(SRC_DIR, "..", "data", "gesture_recognition_data.csv")
RESULTS_DIR = os.path.join(SRC_DIR, "..", "results")

# ── Colours ───────────────────────────────────────────────────────────────────
C_FB      = "#378ADD"    # Feature-based method
C_ML      = "#1D9E75"    # ML method
C_FLY     = "#D85A30"    # Flying UAV condition
C_GRID    = 0.25


# ── Confusion matrix construction ─────────────────────────────────────────────

def build_confusion_matrix(df, method_col="ML_Method_Rate_pct"):
    """
    Construct a synthetic 8x8 confusion matrix from per-gesture accuracy.

    Diagonal = recognition rate for each gesture.
    Off-diagonal errors distributed to most likely confusion pairs
    based on sensor value proximity (gestures with overlapping
    sensor ranges are more likely to be confused).
    """
    gestures = df["Gesture"].tolist()
    n = len(gestures)
    cm = np.zeros((n, n))

    for i, (_, row) in enumerate(df.iterrows()):
        acc   = row[method_col] / 100.0
        error = 1.0 - acc
        cm[i, i] = acc * 100

        # Distribute errors to adjacent gestures by sensor proximity
        sensor_mid = (row["Sensor_Value_Low"] + row["Sensor_Value_High"]) / 2
        distances  = []
        for j, (_, other) in enumerate(df.iterrows()):
            if i != j:
                other_mid = (other["Sensor_Value_Low"] +
                             other["Sensor_Value_High"]) / 2
                distances.append((j, abs(sensor_mid - other_mid)))

        distances.sort(key=lambda x: x[1])
        # Assign 60% of error to nearest gesture, 40% to second nearest
        if len(distances) >= 2:
            cm[i, distances[0][0]] = error * 0.60 * 100
            cm[i, distances[1][0]] = error * 0.40 * 100

    return cm, gestures


# ── Plot functions ────────────────────────────────────────────────────────────

def plot_accuracy_bar(df, output_path):
    """Grouped bar chart — three methods side by side per gesture."""
    gestures = df["Gesture"].tolist()
    x = np.arange(len(gestures))
    width = 0.26

    fig, ax = plt.subplots(figsize=(13, 6))

    b1 = ax.bar(x - width, df["FB_Method_Rate_pct"], width,
                label="Feature-Based (FB)", color=C_FB,
                edgecolor="white", linewidth=0.8)
    b2 = ax.bar(x,          df["ML_Method_Rate_pct"], width,
                label="Machine Learning (ML)", color=C_ML,
                edgecolor="white", linewidth=0.8)
    b3 = ax.bar(x + width,  df["Flying_UAV_Rate_pct"], width,
                label="Flying UAV Condition", color=C_FLY,
                edgecolor="white", linewidth=0.8)

    ax.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=7.5, fontweight="bold")
    ax.bar_label(b2, fmt="%.1f%%", padding=3, fontsize=7.5, fontweight="bold")
    ax.bar_label(b3, fmt="%.1f%%", padding=3, fontsize=7.5, fontweight="bold")

    ax.set_xlabel("Gesture Class", fontsize=11)
    ax.set_ylabel("Recognition Rate (%)", fontsize=11)
    ax.set_title(
        "Gesture Recognition Accuracy by Method — 8 Gesture Classes\n"
        "FB Method vs ML Method vs Flying UAV Condition",
        fontsize=12, fontweight="bold"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(gestures, fontsize=10)
    ax.set_ylim(75, 102)
    ax.axhline(90, color="grey", linewidth=0.8, linestyle=":",
               alpha=0.7, label="90% target threshold")
    ax.legend(fontsize=10, loc="lower right")
    ax.grid(axis="y", alpha=C_GRID)
    ax.set_facecolor("#FAFAFA")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_confusion_matrix(cm, gestures, output_path):
    """Heatmap confusion matrix for ML method."""
    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(cm, interpolation="nearest", cmap="Blues", vmin=0, vmax=100)
    plt.colorbar(im, ax=ax, label="Recognition Rate (%)")

    ax.set_xticks(np.arange(len(gestures)))
    ax.set_yticks(np.arange(len(gestures)))
    ax.set_xticklabels(gestures, rotation=30, ha="right", fontsize=10)
    ax.set_yticklabels(gestures, fontsize=10)

    # Annotate cells
    thresh = cm.max() / 2.0
    for i in range(len(gestures)):
        for j in range(len(gestures)):
            val = cm[i, j]
            if val > 0.1:
                ax.text(j, i, f"{val:.1f}",
                        ha="center", va="center", fontsize=9,
                        color="white" if val > thresh else "black",
                        fontweight="bold" if i == j else "normal")

    ax.set_xlabel("Predicted Gesture", fontsize=11)
    ax.set_ylabel("True Gesture", fontsize=11)
    ax.set_title(
        "Gesture Recognition Confusion Matrix — ML Method\n"
        "Re = 500,000  ·  8 Gesture Classes  ·  IR Sensor Pipeline",
        fontsize=12, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_method_comparison(df, output_path):
    """Bar chart comparing mean accuracy across the three methods."""
    methods = ["FB Method", "ML Method", "Flying UAV"]
    means   = [
        df["FB_Method_Rate_pct"].mean(),
        df["ML_Method_Rate_pct"].mean(),
        df["Flying_UAV_Rate_pct"].mean(),
    ]
    colours = [C_FB, C_ML, C_FLY]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(methods, means, color=colours, width=0.45,
                  edgecolor="white", linewidth=1.2)
    ax.bar_label(bars, fmt="%.2f%%", padding=5,
                 fontsize=12, fontweight="bold")

    # Annotate per-gesture range as error bars
    stds = [
        df["FB_Method_Rate_pct"].std(),
        df["ML_Method_Rate_pct"].std(),
        df["Flying_UAV_Rate_pct"].std(),
    ]
    ax.errorbar(methods, means, yerr=stds, fmt="none",
                color="black", capsize=6, linewidth=1.5)

    ax.set_ylabel("Mean Recognition Rate (%)", fontsize=11)
    ax.set_title(
        "Mean Gesture Recognition Rate by Method\n"
        "Error bars show ±1σ across 8 gesture classes",
        fontsize=12, fontweight="bold"
    )
    ax.set_ylim(80, 102)
    ax.axhline(90, color="grey", linewidth=0.8, linestyle=":",
               alpha=0.7, label="90% target")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=C_GRID)
    ax.set_facecolor("#FAFAFA")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_sensor_thresholds(df, output_path):
    """
    Horizontal bar chart showing IR sensor value ranges per gesture.
    Shows how each gesture is distinguished by threshold bands.
    """
    gestures = df["Gesture"].tolist()
    colours  = plt.cm.Set2(np.linspace(0, 1, len(gestures)))

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, (_, row) in enumerate(df.iterrows()):
        low  = row["Sensor_Value_Low"]
        high = row["Sensor_Value_High"]
        ax.barh(i, high - low, left=low,
                color=colours[i], edgecolor="white",
                height=0.6, linewidth=1.0,
                label=row["Gesture"])
        ax.text(low + (high - low) / 2, i,
                f"{row['Gesture']} ({int(low)}–{int(high)})",
                ha="center", va="center",
                fontsize=9, fontweight="bold", color="white")

    ax.set_xlabel("IR Sensor Value (ADC counts, 0–1023)", fontsize=11)
    ax.set_title(
        "IR Sensor Threshold Bands per Gesture Class\n"
        "Arduino Uno ADC — 10-bit resolution (0–1023)",
        fontsize=12, fontweight="bold"
    )
    ax.set_yticks(range(len(gestures)))
    ax.set_yticklabels(gestures, fontsize=10)
    ax.set_xlim(0, 1023)
    ax.grid(axis="x", alpha=C_GRID)
    ax.set_facecolor("#FAFAFA")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    # ── Print summary ─────────────────────────────────────────────────────
    print("Gesture Recognition Performance Analysis")
    print(f"\n  {'Gesture':<12} {'FB (%)':>8} {'ML (%)':>8} {'Flying (%)':>11} {'Command'}")
    print("  " + "─" * 65)
    for _, row in df.iterrows():
        print(f"  {row['Gesture']:<12} {row['FB_Method_Rate_pct']:>8.1f} "
              f"{row['ML_Method_Rate_pct']:>8.1f} "
              f"{row['Flying_UAV_Rate_pct']:>11.1f}  {row['Command']}")

    print(f"\n  Mean accuracy — FB method    : {df['FB_Method_Rate_pct'].mean():.2f}%")
    print(f"  Mean accuracy — ML method    : {df['ML_Method_Rate_pct'].mean():.2f}%")
    print(f"  Mean accuracy — Flying UAV   : {df['Flying_UAV_Rate_pct'].mean():.2f}%")
    print(f"  ML improvement over FB       : "
          f"+{df['ML_Method_Rate_pct'].mean() - df['FB_Method_Rate_pct'].mean():.2f}%")
    print(f"  Flying UAV degradation vs ML : "
          f"{df['ML_Method_Rate_pct'].mean() - df['Flying_UAV_Rate_pct'].mean():.2f}%")

    above_90_ml = (df["ML_Method_Rate_pct"] >= 90).sum()
    print(f"  Gestures meeting 90% target  : {above_90_ml}/{len(df)} (ML method)")

    # ── Generate plots ────────────────────────────────────────────────────
    print("\nGenerating plots...")

    plot_accuracy_bar(
        df, os.path.join(RESULTS_DIR, "gesture_accuracy_bar.png"))

    cm, gestures = build_confusion_matrix(df)
    plot_confusion_matrix(
        cm, gestures,
        os.path.join(RESULTS_DIR, "gesture_confusion_matrix.png"))

    plot_method_comparison(
        df, os.path.join(RESULTS_DIR, "gesture_method_comparison.png"))

    plot_sensor_thresholds(
        df, os.path.join(RESULTS_DIR, "gesture_sensor_thresholds.png"))

    print("\nGesture performance analysis complete.")
    print("  4 plots saved to results/")


if __name__ == "__main__":
    main()