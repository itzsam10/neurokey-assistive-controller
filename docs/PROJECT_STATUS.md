# NeuroKey project status

**Updated:** 21 October 2026
**Project stage:** laptop-side EMG development; multimodal integration has not started.

## Roadmap

The current design handoff defines a modular controller:

1. **SSVEP EEG** chooses a major mode such as Home, Mobility, Communication, or Alert.
2. **EOG** moves focus through commands within the selected mode.
3. **Forearm EMG** confirms the focused action. A deliberate EMG rule is also planned to request an emergency stop.
4. **Laptop software** processes and logs the signals and sends a local Wi-Fi command.
5. **Output nodes** operate a low-voltage model home and a small unoccupied car.

For the practical build order, EMG and EOG come first. SSVEP follows only after electrode placement, display timing, and a no-selection state have been tested. The earlier 3D-printed OpenBCI-derived headset is a historical mechanical prototype, not a dependency for the present EMG/EOG stage.

A focused EOG menu option is planned to open a **2-second EMG confirmation window**. EMG confirmation must be ignored outside that window. Emergency-stop behavior should override the normal mode and command path. These rules are proposed, not implemented or validated.

## Evidence completed

- Beast Pack firmware flashed; connection to Chords Web over Bluetooth demonstrated.
- Active acquisition route for laptop experiments: ChordsPy BLE bridge publishing to LSL.
- Forearm contraction and rest recordings captured. A 21 October session contains 22,500 samples: 11,250 labelled rest and 11,250 labelled contraction across nine paired trials.
- In that session, the filtered RMS was higher in the contraction segment than its paired rest segment in all nine trials; ratio range 1.83×–5.22×. This only shows signal change within one session.
- Separate Chords Web recordings from 28 September have exploratory RMS plots and group summaries in `results/emg_initial_analysis/`.
- Laptop detector locally dispatched UDP datagrams to port 4210. No powered/listening ESP32 receiver or relay was present in that test.
- The OpenBCI-derived headset frame was printed; scalp EEG or SSVEP has not been demonstrated.

## Known problems and evidence limits

- False activations have occurred during lead movement and ordinary arm movement.
- A large electrode-snap touch is a contact artifact; it must not be labelled as intentional EMG.
- The current detector has cooldown behavior but no verified one-shot latch or EOG command gate.
- The current training code uses 250-sample windows while live inference uses 0.15-second windows. The reported 94.44% is from a random 80/20 overlapping-window split, not session-held-out validation.
- Chords Web CSV counters show non-increment and wrap anomalies. The analysis timeline assumes nominal 500 Hz; timing and dropped-sample handling need verification.
- No EOG, SSVEP, ESP32 receiver, physical relay, car, or home-load result is complete.

## Next pass gates

| Gate | Evidence required | Status |
|---|---|---|
| EMG acquisition | Repeatable rest/action recordings across separate sessions and electrode reapplication | In progress |
| EMG event logic | One event per sustained contraction; release required before re-arming; logged artifact negatives | Planned |
| EOG navigation | Recorded left/right and vertical/blink classes; neutral and artifact rejection | Not started |
| Context confirmation | Focused menu option opens a 2-second gate; EMG ignored outside it | Planned |
| Output node | Manual, bounded Wi-Fi commands; STOP, timeout, and Wi-Fi-loss tests with a safe load | Not verified |
| SSVEP | Verified EEG alpha, timed stimulus, one target, then multi-target decoding with NO_SELECTION | Not started |
| Integrated demo | Modality-specific tests plus scripted end-to-end tasks on unoccupied low-voltage demonstrators | Not started |

## Reporting

Report methods, session boundaries, trial counts, test duration, false activations per minute, missed intended events, latency, and dropped/invalid samples. Keep measurements distinct from goals. Do not describe the prototype as patient-ready or suitable for a powered wheelchair.
