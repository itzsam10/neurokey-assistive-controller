#!/usr/bin/env python3
"""Summarize paired rest/contraction blocks from a labelled NeuroKey session.

The current recorder writes 2.5-second blocks at the nominal 500 Hz rate:
1,250 rest rows followed by 1,250 contraction rows for each trial. Values in
the ch6 column are already filtered by the recorder. This script computes
RMS only; it does not filter, repair missing samples, or claim classifier
performance.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Session CSV with ch6 and label columns")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/forearm_emg_session_summary.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--samples-per-block",
        type=int,
        default=1250,
        help="Rows in each 2.5-second rest/action block at nominal 500 Hz",
    )
    args = parser.parse_args()

    with args.input.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or not {"ch6", "label"}.issubset(reader.fieldnames):
            parser.error("input must contain 'ch6' and 'label' columns")
        rows = list(reader)

    pair_size = 2 * args.samples_per_block
    if args.samples_per_block <= 0 or len(rows) == 0 or len(rows) % pair_size:
        parser.error("row count must contain complete rest/action pairs")

    output_rows = []
    for trial_idx, start in enumerate(range(0, len(rows), pair_size), start=1):
        rest_rows = rows[start : start + args.samples_per_block]
        action_rows = rows[start + args.samples_per_block : start + pair_size]
        try:
            rest_labels = {int(float(row["label"])) for row in rest_rows}
            action_labels = {int(float(row["label"])) for row in action_rows}
            rest = [float(row["ch6"]) for row in rest_rows]
            action = [float(row["ch6"]) for row in action_rows]
        except (TypeError, ValueError) as exc:
            parser.error(f"invalid numeric data near trial {trial_idx}: {exc}")
        if rest_labels != {0} or action_labels != {1}:
            parser.error(
                f"trial {trial_idx} must contain label 0 in the rest block "
                "and label 1 in the contraction block"
            )

        rest_rms = rms(rest)
        action_rms = rms(action)
        output_rows.append(
            [
                trial_idx,
                len(rest),
                len(action),
                f"{rest_rms:.6f}",
                f"{action_rms:.6f}",
                f"{action_rms / rest_rms:.3f}" if rest_rms else "",
            ]
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(
            ["trial", "rest_rows", "contraction_rows", "rest_rms", "contraction_rms", "ratio"]
        )
        writer.writerows(output_rows)

    print(f"Wrote {len(output_rows)} paired-trial summaries to {args.output}")
    print("RMS uses the recorded filtered signal units; time assumes the recorder's nominal sample rate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
