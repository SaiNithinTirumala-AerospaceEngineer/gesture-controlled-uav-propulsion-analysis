"""
propulsion_analysis.py
----------------------
AIML-based propulsion system analysis for a gesture-controlled quadrotor UAV.

Computes eight propulsion and system metrics from flight test data:
  1. Thrust-to-Weight Ratio       — hover and manoeuvre margin
  2. Flight Time                  — endurance prediction (minutes)
  3. Motor Power Consumption      — electrical load per motor bank
  4. Gesture System Power         — GSPC overhead from recognition pipeline
  5. Total Power Consumption      — combined system draw
  6. Battery Capacity             — Ah sizing from mission profile
  7. Battery Voltage Selection    — optimal pack voltage
  8. Payload Consideration        — payload fraction vs thrust

Source: Reconstructed from project report "Design and Analysis of Propulsion
System of Gesture Control UAV Using AIML", Malla Reddy College of Engineering
& Technology, 2023–2024.

Inputs : data/drone_propulsion_data.csv
Outputs: results/thrust_weight_ratio.png
         results/flight_time.png
         results/power_consumption.png
         results/gspc_output.png
         results/total_power_consumption.png
         results/battery_capacity.png
         results/battery_voltage_selection.png
         results/payload_consideration.png
         results/propulsion_dashboard.png

Usage:
    python src/propulsion_analysis.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Paths ─────────────────────────────────────────────────────────────────────
SRC_DIR     = os.path.dirname(__file__)
DATA_PATH   = os.path.join(SRC_DIR, "..", "data", "drone_propulsion_data.csv")
RESULTS_DIR = os.path.join(SRC_DIR, "..", "results")

# ── Plot style ────────────────────────────────────────────────────────────────
COLOUR = "#1A6BAD"       # Primary line colour — aerospace blue
ACCENT = "#D85A30"       # Accent — highlight colour
GRID_A = 0.25            # Grid alpha


# ── Metric calculations ───────────────────────────────────────────────────────

def thrust_to_weight_ratio(thrust_N, weight_N):
    """T/W ratio — must exceed 1.0 for hover, target > 1.5 for manoeuvre."""
    return thrust_N / weight_N


def flight_time_minutes(battery_mAh, current_A):
    """
    Endurance estimate (minutes).
    t = (Battery_mAh / (Current_A * 1000)) * 60 * 0.8
    0.8 factor: 80% usable depth of discharge (safe LiPo limit).
    """
    return (battery_mAh / (current_A * 1000)) * 60 * 0.8


def motor_power_consumption(rpm, current_A):
    """
    Motor bank power consumption (W).
    P = RPM * I / k  where k ≈ 1000 (empirical RPM/V constant scaling)
    """
    return (rpm / 1000.0) * current_A


def gesture_system_power(gesture_power_W, gesture_flag):
    """
    Gesture recognition system power consumption (W).
    Only consumed when gesture is actively being recognised.
    """
    return gesture_power_W * gesture_flag


def total_power(motor_P, gesture_P):
    """Total system power draw (W) — motor bank + gesture pipeline."""
    return motor_P + gesture_P


def battery_capacity_Ah(battery_mAh):
    """Battery capacity in Amp-hours."""
    return battery_mAh / 1000.0


def battery_voltage_selection(total_P, current_A):
    """
    Required pack voltage (V).
    V = P / I  (Ohm's law at system level)
    """
    return total_P / current_A


def payload_consideration(payload_kg, thrust_N):
    """
    Payload fraction — ratio of payload mass force to total thrust.
    Lower is better for performance margin.
    """
    g = 9.81
    return (payload_kg * g) / thrust_N


# ── Individual plot functions ─────────────────────────────────────────────────

def _style_ax(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, alpha=GRID_A)
    ax.set_facecolor("#FAFAFA")


def plot_single(x, y, title, xlabel, ylabel, filename, colour=COLOUR,
                hline=None, hline_label=None):
    """Standard single-metric line plot."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, y, color=colour, linewidth=2.2, marker="o",
            markersize=4, markerfacecolor="white", markeredgecolor=colour)
    if hline is not None:
        ax.axhline(hline, color=ACCENT, linewidth=1.2,
                   linestyle="--", label=hline_label)
        ax.legend(fontsize=9)
    _style_ax(ax, title, xlabel, ylabel)
    ax.annotate(f"Max: {y.max():.3f}",
                xy=(x[y.argmax()], y.max()),
                xytext=(x[y.argmax()] + 0.5, y.max() * 1.02),
                fontsize=8.5, color=colour,
                arrowprops=dict(arrowstyle="->", color=colour, lw=1.0))
    ax.annotate(f"Min: {y.min():.3f}",
                xy=(x[y.argmin()], y.min()),
                xytext=(x[y.argmin()] + 0.5, y.min() * 0.97),
                fontsize=8.5, color=ACCENT,
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.0))
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ── Dashboard ─────────────────────────────────────────────────────────────────

def plot_dashboard(df, metrics, output_path):
    """
    Six-panel propulsion dashboard — the hero README figure.
    Mirrors the layout of Fig 4.1.9 from the project report.
    """
    fig = plt.figure(figsize=(18, 11))
    fig.suptitle(
        "Propulsion System Analysis Dashboard — Gesture-Controlled Quadrotor UAV\n"
        "AIML Model Output  ·  20 Flight Samples  ·  450mm F450 Frame",
        fontsize=13, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 3, wspace=0.35, hspace=0.42)

    panels = [
        (gs[0, 0], metrics["tw"],       "Thrust-to-Weight Ratio",
         "T/W Ratio",        "#1A6BAD", 1.5, "Hover threshold (T/W=1.5)"),
        (gs[0, 1], metrics["ft"],       "Flight Time (minutes)",
         "Flight Time (min)", "#1D9E75", None, None),
        (gs[0, 2], metrics["mpc"],      "Motor Power Consumption (W)",
         "Power (W)",        "#D85A30", None, None),
        (gs[1, 0], metrics["gspc"],     "Gesture System Power (W)",
         "GSPC (W)",         "#7F77DD", None, None),
        (gs[1, 1], metrics["tpc"],      "Total Power Consumption (W)",
         "Total Power (W)",  "#B5541B", None, None),
        (gs[1, 2], metrics["payload"],  "Payload Consideration",
         "Payload Fraction", "#1A6BAD", None, None),
    ]

    x = df["Sample"].values

    for spec, y, title, ylabel, colour, hline, hlabel in panels:
        ax = fig.add_subplot(spec)
        ax.plot(x, y, color=colour, linewidth=2.0, marker="o",
                markersize=3.5, markerfacecolor="white",
                markeredgecolor=colour)
        if hline is not None:
            ax.axhline(hline, color=ACCENT, linewidth=1.0,
                       linestyle="--", label=hlabel, alpha=0.8)
            ax.legend(fontsize=7.5)
        _style_ax(ax, title, "Sample", ylabel)

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    x  = df["Sample"].values

    # ── Compute all 8 metrics ─────────────────────────────────────────────
    df["TW_Ratio"]          = thrust_to_weight_ratio(
                                  df["Thrust_N"], df["Weight_N"])
    df["Flight_Time_min"]   = flight_time_minutes(
                                  df["Battery_Capacity_mAh"],
                                  df["Current_Draw_A"])
    df["Motor_Power_W"]     = motor_power_consumption(
                                  df["Motor_RPM"], df["Current_Draw_A"])
    df["GSPC_W"]            = gesture_system_power(
                                  df["Gesture_Recognition_Power_W"],
                                  df["Gesture_Recognized"])
    df["Total_Power_W"]     = total_power(
                                  df["Motor_Power_W"], df["GSPC_W"])
    df["Battery_Cap_Ah"]    = battery_capacity_Ah(
                                  df["Battery_Capacity_mAh"])
    df["Battery_Voltage_V"] = battery_voltage_selection(
                                  df["Total_Power_W"],
                                  df["Current_Draw_A"])
    df["Payload_Fraction"]  = payload_consideration(
                                  df["Payload_Mass_kg"], df["Thrust_N"])

    # ── Print summary table ───────────────────────────────────────────────
    print("Propulsion System Analysis — AIML Model Results")
    print(f"\n  {'Metric':<35} {'Min':>8} {'Max':>8} {'Mean':>8}")
    print("  " + "─" * 63)
    metrics_summary = [
        ("Thrust-to-Weight Ratio",       df["TW_Ratio"]),
        ("Flight Time (min)",             df["Flight_Time_min"]),
        ("Motor Power Consumption (W)",   df["Motor_Power_W"]),
        ("Gesture System Power (W)",      df["GSPC_W"]),
        ("Total Power Consumption (W)",   df["Total_Power_W"]),
        ("Battery Capacity (Ah)",         df["Battery_Cap_Ah"]),
        ("Battery Voltage Selection (V)", df["Battery_Voltage_V"]),
        ("Payload Consideration",         df["Payload_Fraction"]),
    ]
    for name, series in metrics_summary:
        print(f"  {name:<35} {series.min():>8.3f} "
              f"{series.max():>8.3f} {series.mean():>8.3f}")

    print(f"\n  Hover T/W > 1.5 requirement met: "
          f"{(df['TW_Ratio'] >= 1.5).sum()}/{len(df)} samples")
    print(f"  Mean endurance               : "
          f"{df['Flight_Time_min'].mean():.1f} minutes")
    print(f"  Peak total power draw        : "
          f"{df['Total_Power_W'].max():.1f} W")

    # ── Generate individual plots ─────────────────────────────────────────
    print("\nGenerating plots...")

    plot_single(x, df["TW_Ratio"].values,
                "Thrust-to-Weight Ratio — 20 Flight Samples",
                "Sample", "T/W Ratio",
                "thrust_weight_ratio.png",
                hline=1.5, hline_label="Minimum hover threshold (T/W = 1.5)")

    plot_single(x, df["Flight_Time_min"].values,
                "Flight Time Prediction — 80% DoD Limit",
                "Sample", "Flight Time (minutes)",
                "flight_time.png", colour="#1D9E75")

    plot_single(x, df["Motor_Power_W"].values,
                "Motor Power Consumption",
                "Sample", "Power Consumption (W)",
                "power_consumption.png", colour="#D85A30")

    plot_single(x, df["GSPC_W"].values,
                "Gesture System Power Consumption (GSPC)",
                "Sample", "GSPC (W)",
                "gspc_output.png", colour="#7F77DD")

    plot_single(x, df["Total_Power_W"].values,
                "Total Power Consumption — Motor + Gesture Pipeline",
                "Sample", "Total Power (W)",
                "total_power_consumption.png", colour="#B5541B")

    plot_single(x, df["Battery_Cap_Ah"].values,
                "Battery Capacity",
                "Sample", "Battery Capacity (Ah)",
                "battery_capacity.png", colour="#1D9E75")

    plot_single(x, df["Battery_Voltage_V"].values,
                "Battery Voltage Selection",
                "Sample", "Voltage (V)",
                "battery_voltage_selection.png", colour="#D85A30")

    plot_single(x, df["Payload_Fraction"].values,
                "Payload Consideration — Payload Force / Total Thrust",
                "Sample", "Payload Fraction",
                "payload_consideration.png", colour="#1A6BAD")

    # ── Generate hero dashboard ───────────────────────────────────────────
    metrics = {
        "tw":      df["TW_Ratio"].values,
        "ft":      df["Flight_Time_min"].values,
        "mpc":     df["Motor_Power_W"].values,
        "gspc":    df["GSPC_W"].values,
        "tpc":     df["Total_Power_W"].values,
        "payload": df["Payload_Fraction"].values,
    }
    plot_dashboard(df, metrics,
                   os.path.join(RESULTS_DIR, "propulsion_dashboard.png"))

    print("\nPropulsion analysis complete.")
    print(f"  9 plots saved to results/")


if __name__ == "__main__":
    main()