import os
import time
import glob
import socket
import urllib.request
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
import scipy.signal as sp
from pylsl import resolve_streams, StreamInlet
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

FS = 500
CH_IDX = 5  # Pin A5 = Channel 6
ESP32_IP = "192.168.1.100"
UDP_PORT = 4210

# Causal filters: 50 Hz Notch + 20-180 Hz Bandpass
b_n, a_n = sp.iirnotch(50.0, 30.0, FS)
b_b, a_b = sp.butter(4, [20.0, 180.0], btype='bandpass', fs=FS)
SOS = sp.tf2sos(np.polymul(b_n, b_b), np.polymul(a_n, a_b))

def beep(freq=800, ms=150):
    try:
        import winsound
        winsound.Beep(freq, ms)
    except Exception:
        pass

def flush_stream(inlet):
    while True:
        chunk, _ = inlet.pull_chunk(timeout=0.0, max_samples=500)
        if not chunk:
            break

def sample_window(inlet, zi, duration_sec=0.5):
    target = int(duration_sec * FS)
    buf = []
    t0 = time.time()
    while len(buf) < target and (time.time() - t0) < (duration_sec + 1.5):
        chunk, _ = inlet.pull_chunk(timeout=0.04, max_samples=128)
        if chunk:
            for s in chunk:
                v = float(s[CH_IDX] if len(s) > CH_IDX else s[0])
                fv, zi = sp.sosfilt(SOS, np.array([v]), zi=zi)
                buf.append(fv[0])
        else:
            time.sleep(0.005)

    if len(buf) < target:
        buf.extend([0.0] * (target - len(buf)))

    data = np.array(buf[:target])
    rms = float(np.sqrt(np.mean(data**2)))
    wl = float(np.sum(np.abs(np.diff(data))))  # Waveform Length: Dense EMG vs Wire Shake
    p2p = float(np.ptp(data))
    return rms, wl, p2p, data, zi

def interactive_diagnostics(inlet, zi):
    print("\n" + "="*60)
    print(" 🔍 STEP 1: GEL ELECTRODE DIAGNOSTICS")
    print("="*60)
    print("Measuring noise floor... Keep forearm relaxed and still.")
    flush_stream(inlet)

    vals = []
    for _ in range(6):
        rms, _, _, _, zi = sample_window(inlet, zi, duration_sec=0.4)
        vals.append(rms)
        time.sleep(0.05)

    avg_rms = float(np.mean(vals))
    print(f" -> Rest Baseline: {avg_rms:.1f} RMS")

    if avg_rms > 45.0:
        print(" ❌ FAIL: Baseline > 45 RMS. Unplug charger & press REF gel pad firmly.")
        return False, avg_rms, zi
    print(" ✅ PASS: Clean baseline confirmed.")

    print("\n👉 CLENCH your fist or TAP the forearm gel pad NOW (8s timeout)...")
    t0 = time.time()
    while time.time() - t0 < 8.0:
        rms, _, _, _, zi = sample_window(inlet, zi, duration_sec=0.25)
        bar = "#" * min(30, int(rms / 3))
        print(f"  Live RMS: {rms:5.1f} | {bar:<30}", end="\r")
        if rms > max(55.0, avg_rms * 2.0):
            beep(1200, 200)
            print(f"\n\n ✅ PASS: Spike detected ({rms:.1f} RMS). Hardware locked in!")
            return True, avg_rms, zi

    print("\n ❌ FAIL: No spike detected on Pin A5. Check snap wire.")
    return False, avg_rms, zi

def record_sessions(inlet, zi):
    print("\n" + "="*60)
    print(" 📋 STEP 2: RECORDING 3 SESSIONS (3 TRIALS EACH)")
    print("="*60)
    os.makedirs("data/sessions", exist_ok=True)
    rows = []

    for s in range(1, 4):
        print(f"\n--- [SESSION {s}/3] ---")
        input(f"Rest arm flat on desk. Press ENTER to start Session {s}...")
        flush_stream(inlet)

        trial = 1
        while trial <= 3:
            print(f"\n[Trial {trial}/3] 🟢 RELAX ARM...")
            for c in range(3, 0, -1):
                print(f"   Rest recording in {c}...", end="\r")
                time.sleep(1.0)
            beep(600, 100)
            flush_stream(inlet)
            print("   >>> RECORDING REST (2.5s) <<<       ")
            r_rms, r_wl, r_p2p, r_sig, zi = sample_window(inlet, zi, duration_sec=2.5)

            if r_rms > 50.0:
                print(f"   ❌ Rest too noisy ({r_rms:.1f} RMS). Retrying trial...")
                continue

            effort = "MILD (30%)" if trial == 1 else ("MEDIUM (60%)" if trial == 2 else "STRONG (100%)")
            print(f"⚡ PREPARE: {effort} CLENCH")
            for c in range(3, 0, -1):
                print(f"   Hold clench in {c}...", end="\r")
                time.sleep(1.0)
            beep(1000, 200)
            print("   >>> CLENCH & HOLD NOW! <<<          ")
            time.sleep(0.4)
            flush_stream(inlet)
            c_rms, c_wl, c_p2p, c_sig, zi = sample_window(inlet, zi, duration_sec=2.5)
            beep(500, 150)
            print("   -> RELAX ARM!")

            ratio = c_rms / (r_rms + 1e-6)
            tag = "✅ PASS" if ratio >= 1.4 else "⚠️ WEAK"
            print(f"   Result: Rest={r_rms:.1f} | Active={c_rms:.1f} | Ratio={ratio:.2f}x [{tag}]")

            now = time.time()
            for v in r_sig: rows.append([now, v, 0, r_rms])
            for v in c_sig: rows.append([now, v, 1, r_rms])
            trial += 1
            time.sleep(1.2)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"data/sessions/session_{ts}.csv"
    pd.DataFrame(rows, columns=["timestamp", "ch6", "label", "base_rms"]).to_csv(fname, index=False)
    print(f"\n[SAVED SESSION]: {fname}")
    return zi

def train_scaled_svm():
    print("\n" + "="*60)
    print(" 🧠 STEP 3: TRAINING PRELIMINARY RBF-SVM (RANDOM WINDOW SPLIT)")
    print("="*60)
    files = glob.glob("data/sessions/*.csv")
    dfs = []
    for f in sorted(set(files)):
        try:
            df = pd.read_csv(f)
            if {"ch6", "label", "base_rms"}.issubset(df.columns):
                dfs.append(df)
                print(f"  [LOADED] {f} ({len(df)} rows)")
        except Exception:
            continue

    if not dfs:
        print("[ERROR] No valid CSV files found.")
        return

    full_df = pd.concat(dfs, ignore_index=True)
    win, step = 250, 125
    X, y, rest_r, clench_r = [], [], [], []

    for i in range(0, len(full_df) - win, step):
        seg = full_df.iloc[i:i+win]
        sig = seg["ch6"].values
        lbl = int(seg["label"].iloc[0])
        base = float(seg["base_rms"].iloc[0])

        if lbl == 0 and base > 50.0:
            continue

        rms = float(np.sqrt(np.mean(sig**2)))
        ratio = rms / (base + 1e-6)
        wl = float(np.sum(np.abs(np.diff(sig))))
        wl_ratio = wl / ((base * len(sig) * 0.3) + 1e-6)

        # 3 normalized, scale-invariant features
        X.append([ratio, wl_ratio, rms])
        y.append(lbl)
        if lbl == 0:
            rest_r.append(ratio)
        else:
            clench_r.append(ratio)

    X, y = np.array(X), np.array(y)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    clf = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=2.0, probability=True))
    clf.fit(X_tr, y_tr)

    tr_acc = accuracy_score(y_tr, clf.predict(X_tr)) * 100
    te_acc = accuracy_score(y_te, clf.predict(X_te)) * 100

    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, "models/gesture_model.pkl")

    r95 = float(np.percentile(rest_r, 95)) if rest_r else 1.25
    c10 = float(np.percentile(clench_r, 10)) if clench_r else 1.80
    thresh = float(np.clip((r95 + c10) / 2.0, 1.80, 2.50))

    with open("models/threshold.txt", "w") as fp:
        fp.write(f"{thresh:.3f}\n")

    print("-" * 60)
    print(f"  🎯 Train Accuracy : {tr_acc:.2f}% | Test Accuracy : {te_acc:.2f}%")
    print(f"  🔥 Calibrated Ratio Threshold: {thresh:.2f}x")
    print("  [SAVED] models/gesture_model.pkl & models/threshold.txt")
    print("=" * 60)

def live_inference(inlet, zi):
    if not os.path.exists("models/gesture_model.pkl") or not os.path.exists("models/threshold.txt"):
        print("[ERROR] Train the model first (Option 2 or 3).")
        return zi

    clf = joblib.load("models/gesture_model.pkl")
    with open("models/threshold.txt") as f:
        thresh = float(f.read().strip())

    thresh = float(np.clip(thresh, 1.80, 2.40))
    ip = input(f"ESP32 IP (Enter for {ESP32_IP}): ").strip() or ESP32_IP
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        print("\nLocking 3s rest baseline... KEEP FOREARM STILL ON DESK.")
        flush_stream(inlet)
        base_rms, _, _, _, zi = sample_window(inlet, zi, duration_sec=3.0)
        
        if base_rms > 40.0:
            print(f"❌ Baseline noisy ({base_rms:.1f} RMS > 40.0). Keep arm dead still. Retrying...")
            time.sleep(1.0)
            continue
        break

    base_rms = max(10.0, base_rms)
    print(f"✅ Baseline Locked: {base_rms:.1f} RMS | Hard Trigger Ratio: {thresh:.2f}x")
    print("=== EXPERIMENTAL EMG DETECTOR (FALSE TRIGGERS OBSERVED) ===")
    print("Shake wire, move arm, or clench to test.\n")

    streak = 0
    cooldown = 0
    try:
        while True:
            rms, wl, p2p, data, zi = sample_window(inlet, zi, duration_sec=0.15)
            ratio = rms / base_rms
            wl_ratio = wl / ((base_rms * len(data) * 0.3) + 1e-6)

            prob = clf.predict_proba([[ratio, wl_ratio, rms]])[0][1]

            # IMMUNITY LOGIC:
            # Wire shakes have high peak/transient but FAIL the high-frequency Waveform Length ratio.
            # Real clench requires BOTH high RMS ratio (> thresh) AND active Waveform density (wl_ratio > 1.35)
            is_real_contraction = (ratio >= thresh) and (wl_ratio >= 1.35) and (prob >= 0.70)

            if cooldown > 0:
                cooldown -= 1
                status = "⏳ COOLDOWN"
            elif is_real_contraction:
                streak += 1
                status = f"🔥 CLENCH ({streak * 0.15:.2f}s)"
                if streak >= 2:  # Sustained >= 0.30s
                    beep(1200, 200)
                    udp_sock.sendto(b"TOGGLE_1", (ip, UDP_PORT))
                    print(f"\n   ⚡ [EMG THRESHOLDS MET; UDP DATAGRAM SENT] -> (Ratio={ratio:.2f}x, WL_Ratio={wl_ratio:.2f}x, SVM={prob*100:.0f}%)")
                    streak = 0
                    cooldown = 6  # 0.9s cooldown
                    flush_stream(inlet)
            else:
                streak = max(0, streak - 1)
                status = "🟢 IDLE (no event threshold)"

            bar = "#" * min(25, int(ratio * 4))
            print(f" Ratio:{ratio:4.2f}x/{thresh:.2f}x | WL:{wl_ratio:4.2f}x | SVM:{prob*100:3.0f}% | {bar:<25} | {status:<24}", end="\r")
    except KeyboardInterrupt:
        print("\nStopped live controller.")
    return zi

def main():
    print("Searching for LSL BioAmpDataStream...")
    streams = resolve_streams(wait_time=5.0)
    if not streams:
        print("[ERROR] Stream not found. Start Window 1 first!")
        return

    inlet = StreamInlet(streams[0])
    inlet.open_stream()
    zi = sp.sosfilt_zi(SOS) * 0.0

    while True:
        print("\n--- NEUROKEY MASTER PIPELINE ---")
        print("1. Diagnostics (Noise Floor + Spike Check)")
        print("2. Record 3 Sessions + Train Scaled SVM")
        print("3. Train Scaled SVM on Clean Sessions Only")
        print("4. Live Inference & Hardware Trigger")
        print("5. Exit")
        c = input("Select (1-5): ").strip()

        if c == "1":
            _, _, zi = interactive_diagnostics(inlet, zi)
        elif c == "2":
            ok, _, zi = interactive_diagnostics(inlet, zi)
            if ok:
                zi = record_sessions(inlet, zi)
                train_scaled_svm()
        elif c == "3":
            train_scaled_svm()
        elif c == "4":
            zi = live_inference(inlet, zi)
        elif c == "5":
            break

if __name__ == "__main__":
    main()