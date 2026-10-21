# Signal-processing status

## Current EMG stream

The active laptop route is:

```text
Beast Pack BLE → ChordsPy bridge → Lab Streaming Layer → unified_pipeline.py
```

The current pipeline applies a 50 Hz notch and a 20–180 Hz bandpass to the selected forearm channel. It extracts RMS, waveform length, and peak-to-peak features and has an RBF-SVM training/inference path. The detector is preliminary and has generated false activations during lead movement and ordinary arm movement.

## Important model-evaluation limits

The training code makes 250-sample (500 ms at nominal 500 Hz) windows with 50% overlap and then randomly splits windows 80/20. Adjacent windows may contain highly similar samples, so this split can leak session-specific patterns. It is not cross-validation and not a reliable estimate for a new session.

The live detector currently computes its features from 0.15-second windows, unlike the 0.5-second training windows. The 94.44% result should not be interpreted as live-controller accuracy until the mismatch is fixed and a session-grouped evaluation is run.

The experimental training routine also needs a review of how it forms windows across class transitions and concatenated files; its current split is not grouped by session. Live acquisition pads a timed-out partial window with zeros, so incomplete windows should be rejected before performance testing.

The current feature detector has a cooldown but no verified one-shot latch. Clench-like threshold activity is not proof of user intent. Measure event recall, missed events, false activations per test duration, and latency against ordinary movement and lead-motion negatives.

## Exploratory Chords Web analysis

The initial September recordings were analyzed with a 20–150 Hz bandpass, a 50 Hz notch, 250 ms RMS windows, and a 50 ms step. The chart time axes assume 500 Hz; they do not correct for counter discontinuities. The relaxed and fist-labelled file groups show a shift in RMS distribution but also overlap. These figures are exploratory signal summaries, not a validated classifier or event-level result.

## Reproduce the 21 October trial summary

With the private session CSV available locally, run:

```powershell
python signal-processing/summarize_forearm_session.py --input path\\to\\session_20261021_122529.csv --output results\\forearm_emg_session_20261021_trial_summary.csv
```

The script checks the nine ordered 1,250-row rest/action pairs and reports RMS in the recorded filtered signal units. It does not publish or copy the input data.

## Next analysis

1. Verify CSV schema and counter-wrap semantics before estimating actual sample rate or loss.
2. Keep trial/session labels intact and do not create windows across session boundaries.
3. Split by complete session for training and evaluation.
4. Calibrate thresholds on training sessions only; evaluate on held-out sessions.
5. Include lead movement, arm movement, rest, intentional clench, and electrode-contact artifacts as separate labels.
6. Compare a simple calibrated threshold baseline with ML; keep a reject/no-command outcome.

Raw physiological CSVs remain outside the public repository. Aggregate summaries and plots are published under `results/`.
