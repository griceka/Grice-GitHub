import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import tkinter as tk
from tkinter import filedialog, messagebox


def browse_for_file():
    """Open a file browser dialog and return the selected file path."""
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    root.attributes('-topmost', True)  # Bring dialog to front

    filepath = filedialog.askopenfilename(
        title="Select Sensor Data CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )

    root.destroy()

    if not filepath:
        print("No file selected. Exiting.")
        sys.exit(0)

    return Path(filepath)


def load_and_parse_data(filepath):
    """Load CSV and extract temperature/humidity from readings_json"""
    df = pd.read_csv(filepath)

    # Parse timestamp
    df['server_timestamp'] = pd.to_datetime(df['server_timestamp'], errors='coerce', utc=True)
    df = df.dropna(subset=['server_timestamp']).sort_values('server_timestamp')

    # Extract temperature and humidity from readings_json
    temps = []
    hums = []

    for idx, row in df.iterrows():
        try:
            readings = json.loads(row['readings_json'])
            temp = readings.get('temperature_F') or readings.get('temperature_C') or readings.get('temperature')
            hum = readings.get('humidity_percent') or readings.get('humidity')
            temps.append(temp)
            hums.append(hum)
        except:
            temps.append(np.nan)
            hums.append(np.nan)

    df['temperature'] = temps
    df['humidity'] = hums

    return df


def compute_stats(series):
    """Compute summary statistics"""
    series = pd.to_numeric(series, errors='coerce').dropna()
    return {
        "count": int(series.count()),
        "mean": float(series.mean()) if series.size else np.nan,
        "std": float(series.std(ddof=1)) if series.size > 1 else np.nan,
        "min": float(series.min()) if series.size else np.nan,
        "max": float(series.max()) if series.size else np.nan,
    }


def main():
    print("Opening file browser...")
    in_path = browse_for_file()
    print(f"Loading data from: {in_path}")

    df = load_and_parse_data(in_path)

    t = df['server_timestamp']
    temp = pd.to_numeric(df['temperature'], errors='coerce')
    hum = pd.to_numeric(df['humidity'], errors='coerce')

    # Compute statistics
    temp_stats = compute_stats(temp)
    hum_stats = compute_stats(hum)

    print(f"\nTemperature Statistics:")
    print(f"  Count: {temp_stats['count']}")
    print(f"  Mean:  {temp_stats['mean']:.3f} °F")
    print(f"  Std:   {temp_stats['std']:.3f} °F")
    print(f"  Min:   {temp_stats['min']:.3f} °F")
    print(f"  Max:   {temp_stats['max']:.3f} °F")

    print(f"\nHumidity Statistics:")
    print(f"  Count: {hum_stats['count']}")
    print(f"  Mean:  {hum_stats['mean']:.3f} %")
    print(f"  Std:   {hum_stats['std']:.3f} %")
    print(f"  Min:   {hum_stats['min']:.3f} %")
    print(f"  Max:   {hum_stats['max']:.3f} %")

    # Create plot
    date_label = in_path.stem
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f"Sensor Data — {date_label}", fontsize=14, fontweight='bold')

    # Temperature plot
    ax1.plot(t, temp, color='tab:red', linewidth=1.5, label='Temperature (°F)')
    if not np.isnan(temp_stats['mean']):
        ax1.axhline(temp_stats['mean'], color='tab:red', linestyle='--', linewidth=1.5,
                    label=f"Mean = {temp_stats['mean']:.2f} °F")
        ax1.axhline(temp_stats['mean'] + temp_stats['std'], color='tab:gray', linestyle=':', linewidth=1,
                    label=f"+1σ = {temp_stats['mean'] + temp_stats['std']:.2f} °F")
        ax1.axhline(temp_stats['mean'] - temp_stats['std'], color='tab:gray', linestyle=':', linewidth=1,
                    label=f"-1σ = {temp_stats['mean'] - temp_stats['std']:.2f} °F")
        ax1.fill_between(t,
                         temp_stats['mean'] - temp_stats['std'],
                         temp_stats['mean'] + temp_stats['std'],
                         color='tab:red', alpha=0.08)
    ax1.set_ylabel('Temperature (°F)', fontsize=11)
    ax1.set_title('Temperature vs. Time', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', fontsize=9)

    # Humidity plot
    ax2.plot(t, hum, color='tab:blue', linewidth=1.5, label='Humidity (%)')
    if not np.isnan(hum_stats['mean']):
        ax2.axhline(hum_stats['mean'], color='tab:blue', linestyle='--', linewidth=1.5,
                    label=f"Mean = {hum_stats['mean']:.2f} %")
        ax2.axhline(hum_stats['mean'] + hum_stats['std'], color='tab:gray', linestyle=':', linewidth=1,
                    label=f"+1σ = {hum_stats['mean'] + hum_stats['std']:.2f} %")
        ax2.axhline(hum_stats['mean'] - hum_stats['std'], color='tab:gray', linestyle=':', linewidth=1,
                    label=f"-1σ = {hum_stats['mean'] - hum_stats['std']:.2f} %")
        ax2.fill_between(t,
                         hum_stats['mean'] - hum_stats['std'],
                         hum_stats['mean'] + hum_stats['std'],
                         color='tab:blue', alpha=0.08)
    ax2.set_ylabel('Humidity (%)', fontsize=11)
    ax2.set_xlabel('Time (UTC)', fontsize=11)
    ax2.set_title('Humidity vs. Time', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=9)

    fig.autofmt_xdate()
    plt.tight_layout()

    # Save outputs next to the input file
    out_dir = in_path.parent
    out_png = out_dir / f"{in_path.stem}_analysis.png"
    out_csv = out_dir / f"{in_path.stem}_summary.csv"

    fig.savefig(out_png, dpi=150, bbox_inches='tight')
    print(f"\n✓ Plot saved:    {out_png}")

    summary_df = pd.DataFrame({
        'Metric': ['Temperature (°F)', 'Humidity (%)'],
        'Count': [temp_stats['count'], hum_stats['count']],
        'Mean': [round(temp_stats['mean'], 3), round(hum_stats['mean'], 3)],
        'Std Dev': [round(temp_stats['std'], 3), round(hum_stats['std'], 3)],
        'Min': [round(temp_stats['min'], 3), round(hum_stats['min'], 3)],
        'Max': [round(temp_stats['max'], 3), round(hum_stats['max'], 3)],
    })
    summary_df.to_csv(out_csv, index=False)
    print(f"✓ Summary saved: {out_csv}")

    plt.show()


if __name__ == "__main__":
    main()
