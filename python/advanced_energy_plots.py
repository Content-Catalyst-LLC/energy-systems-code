#!/usr/bin/env python3
"""Optional advanced plotting workflow using pandas and matplotlib."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "outputs" / "tables" / "energy_dispatch_summary.csv"
FIGURE = ROOT / "outputs" / "figures" / "battery_state.png"

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError as exc:
    print("Advanced dependencies are missing.")
    print("Install them with: pip install -r requirements-advanced.txt")
    print(f"Original import error: {exc}")
    sys.exit(0)


def main() -> None:
    if not INPUT.exists():
        print("Dispatch summary not found. Running the default Python workflow first is required.")
        print("Run: python3 python/energy_balance.py")
        return

    df = pd.read_csv(INPUT)
    FIGURE.parent.mkdir(parents=True, exist_ok=True)

    ax = df.plot(x="hour", y="battery_state_mwh", legend=False)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Battery state of charge (MWh)")
    ax.set_title("Synthetic Battery State of Charge")
    plt.tight_layout()
    plt.savefig(FIGURE, dpi=160)
    print(f"Saved figure to {FIGURE}")


if __name__ == "__main__":
    main()
