# Nimbus Academy · Level 1 — Integrated Assignments (English)

> **Editable working document.** Markdown is plain text; open in any editor (VS Code, Obsidian, Typora, GitHub web UI) and edit freely. Headings, tables, code blocks, lists, and admonitions are preserved by all standard renderers.
>
> **Source:** translated from the canonical Russian Level 1 assignment set produced for the EEG Analyst Pipeline track (BBS-first TOC v1.0).
>
> **Authoring conventions used throughout:**
> - All neurophysiology theory and all formulas needed to solve a task are embedded inside the task statement (no external lookups required).
> - Every pipeline task first presents a **❌ Naive pipeline** with explicit errors, then a **✅ Correct pipeline**, and ends with a direct **❌ vs ✅ comparison** and a one-line **journal entry** linking the engineering decision back to a biological fact.
> - Nimbus Studio graphs are represented as bracketed node chains: `[node_a] → [node_b] → ...`. Each node maps to one block in the visual Studio editor.
> - The dataset used end-to-end is **MOABB BNCI 2014-001 (S01, 0train)** unless stated otherwise.

---

## Table of Contents

1. [Assignment 1.1 — Studio Graph Intake (intake node)](#assignment-11--studio-graph-intake-intake-node)
2. [Assignment 1.2 — Referencing + Filtering](#assignment-12--referencing--filtering)
3. [Assignment 1.3 — Artifact Annotation (EOG / EMG / ECG / bad channels)](#assignment-13--artifact-annotation-eog--emg--ecg--bad-channels)
4. [Assignment 1.4 — Baseline & Nonstationarity (epochs + session metadata)](#assignment-14--baseline--nonstationarity-epochs--session-metadata)
5. [Assignment 1.5 — ICA Cleaning (independent components)](#assignment-15--ica-cleaning-independent-components)
6. [Assignment 1.6 — Quality Dashboard (SNR, α-peak, rejection rate)](#assignment-16--quality-dashboard-snr-α-peak-rejection-rate)
7. [Assignment 1.7 — Public Datasets + Nimbus Feature Contract (replication)](#assignment-17--public-datasets--nimbus-feature-contract-replication)
8. [Assignment 1.CAP — Capstone: Full Analyst Pipeline (integration of 1.1–1.7)](#assignment-1cap--capstone-full-analyst-pipeline-integration-of-1117)

---

# Integrated Assignments — Level 1

# Assignment 1.1 — Studio Graph Intake (intake node)

## Scenario

The file **BNCI 2014-001 (S01, `0train`)** loaded into MNE without errors: **22 EEG channels + 3 EOG channels, sampling rate `sfreq = 250 Hz`, 288 motor imagery epochs**. A technical colleague tells you: *"The file is valid, push it to L2, don't waste time."* Your job is to verify whether *"valid to load"* actually means *"valid to analyse"*, and to assemble an intake node in Nimbus Studio that **locks in the physical measurement schema before any data reaches a filter**.

## What to submit

- **Intake sub-graph in Nimbus Studio** (PNG export + JSON configs per node).
- A single output object `RawIntake` carrying the verified data + metadata.
- A `risk_log.md` file with **at least three entries** in the form *observation → severity → mitigation plan*.
- **One journal line** explaining the chain *biological fact → engineering decision*.

## 📖 Neurophysiology required for this task

### Where the signal on the scalp actually comes from

The potential visible at a scalp electrode is produced **only by pyramidal neurons of cortical layers III and V**. Their apical dendrite, 1–2 mm long, is aligned perpendicular to the cortical surface. When synapses on the distal part of the dendrite are activated, an **electric dipole** forms along the dendrite.

- A single neuron produces a dipole moment of ≈ **10⁻¹² A·m** — invisible at the scalp.
- A scalp-visible signal requires an ensemble of roughly **10⁸ synchronous neurons over ~1 cm²** of cortex, yielding **10–100 µV** at the electrode.

→ **Implication.** EEG amplitude is a measure of **population synchrony**, not of *"how hard you are thinking"*.

### EEG is a potential *difference*, not absolute activity

Any electrode recording is the **potential difference between that electrode and a reference**. Without choosing a reference, the phrase *"activity at channel Cz"* has **no physical meaning**.

→ **Implication.** Reference and montage are not cosmetic GUI settings — they are part of the **physical measurement schema** of the experiment.

### Open vs closed field — why we see cortex but not hippocampus

When pyramidal neurons are stacked **in parallel** (neocortex), their dipoles **sum constructively** at distance → open field, visible on scalp.  
When the geometry is curled or closed (hippocampus, deep nuclei), dipoles **cancel** → closed field, invisible on scalp.

→ **Implication.** A topography that *appears* to come from a deep structure on raw EEG is almost certainly a **projection of a cortical or extra-cranial source**, not the deep structure itself.

### Channel types are biology, not labels

- **EEG channel** measures the local cortical population (with reference subtraction).
- **EOG channel** measures the **corneo-retinal dipole** of the eyeball — amplitude tens of times larger than cortical EEG and dominates frontal sites.
- **EMG channel** measures the **motor unit action potentials** of skeletal muscle — broadband, dominant above 30 Hz.
- **ECG channel** measures the **cardiac dipole** propagating through volume conduction.

→ **Implication.** Mislabelling an EOG as EEG is **not a software bug** — it tells the pipeline to treat an eye signal as a cortical signal. Every downstream stage (filter, ICA, feature extraction) becomes physically incoherent.

## 🧮 Formulas needed for this task

### Nyquist criterion (sampling)

$$ f_N = \frac{f_s}{2} $$

To represent a frequency $f$ honestly, the sampling rate $f_s$ must satisfy $f_s > 2f$. For the EEG analysis band of interest 0.5–45 Hz:

$$ f_s \ge 2 \cdot 45 = 90 \text{ Hz} \quad (\text{minimum}) $$

With $f_s = 250$ Hz, $f_N = 125$ Hz — comfortably above the working band.

### Voltage difference (reference)

$$ V_{\text{scalp}} = \varphi_A - \varphi_B $$

A measured channel value depends on *both* electrodes A and B. Changing the reference changes every channel; it is not a "post-processing tweak".

### Risk severity scoring (used in `risk_log.md`)

A simple, explicit scale:

| Severity | Meaning |
|---|---|
| **L (low)** | Documented quirk, no impact on downstream contract. |
| **M (medium)** | Will mislead a single downstream stage if ignored. |
| **H (high)** | Breaks physical interpretability of the signal. |

## Solution walkthrough

### Step 1. Logical hypothesis

If we treat the file as *"valid because it loads"*, we have:
1. EOG channels potentially tagged as EEG → any spatial method (CSP, ICA, topomap) will leak ocular dipole into cortical interpretation.
2. No `DigMontage` set → topography is geometrically undefined; downstream visualisations will be misleading.
3. `sfreq = 250 Hz` is documented but **not asserted** — a future replication on a different file may silently change it.
4. Events are present in MNE annotations but their semantic mapping (`event_id`) is not yet pinned to a serialised contract.

The intake node must convert each of these into a checked, serialised guarantee **before** any signal processing.

### Step 2. Where calculation is required

The only quantitative check at intake is **Nyquist for the target band**. All other checks are structural (type, montage, event id schema, metadata completeness).

### Step 3. Calculation

Target analysis band: **0.5 Hz — 45 Hz** (broad band for Level 1).  
Measured sampling rate: **`sfreq = 250 Hz`**.

$$ f_N = 250 / 2 = 125 \text{ Hz} > 45 \text{ Hz} \quad \checkmark $$

Margin ratio:

$$ \frac{f_N}{f_{\text{high}}} = \frac{125}{45} \approx 2.78 $$

→ A margin of ≈ 2.8× is healthy. Record `nyquist_ok = true` and `nyquist_margin = 2.78` in metadata.

### Step 4. ❌ Naive pipeline (what NOT to do)

```
[load_edf] → [bandpass 1-40] → [ICA] → [features]
```

**One-line summary:** *"Load → filter → ICA → done."*

#### What is missing or wrong

| Node / step | Mistake | Physical consequence |
|---|---|---|
| `load_edf` | Only stores a file path. | Run is not reproducible; another file with the same name silently changes results. |
| *(missing)* `channel_inventory` | EOG and EMG channels stay typed as EEG. | Eye-dipole and muscle activity are mixed into cortical features. |
| *(missing)* `montage_setter` | No `DigMontage`. | Coordinates are NULL; every topomap is geometrically meaningless. |
| *(missing)* `sfreq_validator` | Nyquist never asserted. | A future replication on `sfreq = 128 Hz` would still "look fine" but quietly clip the band. |
| *(missing)* `events_loader` | Annotations not pinned to a typed `event_id` schema. | Downstream epoching can silently mis-label trials. |
| *(missing)* `intake_report` | No serialised contract. | Nothing to diff against in Level 2 onward. |
| `bandpass 1-40` | Filtering is applied **before** the schema is verified. | Errors propagate; you cannot tell whether a defect is biological or schema-induced. |
| `ICA` | Mixed channel types enter ICA. | Components become physiologically uninterpretable. |

### Step 5. ✅ Correct pipeline (Studio graph + JSON config)

```
[data_source]
   → [channel_inventory]
   → [montage_setter]
   → [sfreq_validator]
   → [events_loader]
   → [intake_report]
```

Each node has explicit input and output contracts:

```
data_source         -> RawArray(n_channels, n_samples)
channel_inventory   -> Dict["eeg": List[str], "eog": List[str], "emg": List[str], "ecg": List[str], "misc": List[str], "stim": List[str]]
montage_setter      -> DigMontage aligned to channel_inventory.eeg
sfreq_validator     -> Dict { "sfreq": float, "nyquist": float, "target_band": [low, high], "ok": bool, "margin": float }
events_loader       -> ndarray(n_events, 3), event_id: Dict[str, int]
intake_report       -> IntakeReport { html, json, risks }
```

#### Node-level JSON config (excerpt)

```json
{
  "data_source": {
    "kind": "moabb",
    "dataset": "BNCI2014_001",
    "subject": 1,
    "session": "0train"
  },
  "channel_inventory": {
    "overrides": { "EOG1": "eog", "EOG2": "eog", "EOG3": "eog" },
    "assert_counts": { "eeg": 22, "eog": 3 }
  },
  "montage_setter": {
    "montage": "standard_1020",
    "match_case": false,
    "on_missing": "raise"
  },
  "sfreq_validator": {
    "expected_sfreq": 250.0,
    "target_band": [0.5, 45.0],
    "min_margin": 2.0
  },
  "events_loader": {
    "event_id": { "left_hand": 1, "right_hand": 2, "feet": 3, "tongue": 4 },
    "from": "annotations"
  },
  "intake_report": {
    "emit": ["html", "json", "risks"],
    "out_dir": "artifacts/intake/"
  }
}
```

#### Required entries in `risk_log.md` (minimum three)

| Observation | Severity | Mitigation plan |
|---|---|---|
| 3 EOG channels present and not yet typed as EOG in the source file. | **H** | Apply `channel_inventory.overrides`; assert resulting `len(eog)=3` before exiting intake. |
| Montage not stored in source. | **M** | Force `standard_1020`; if any electrode name does not match, raise rather than silently drop. |
| `sfreq` is read from the file but not asserted against an expected value. | **M** | Assert `expected_sfreq == 250.0`; if a replication run drifts, fail loudly. |

### Step 6. Direct comparison — ❌ vs ✅

| Aspect | ❌ Naive intake | ✅ Correct intake |
|---|---|---|
| Channel typing | EOG counted as EEG | Inventory enforces 22 EEG / 3 EOG |
| Montage | None | `standard_1020` asserted |
| Sampling rate | Read, not asserted | Nyquist computed, margin recorded |
| Events | Annotations only | Typed `event_id` schema serialised |
| Reproducibility | Path-based | Dataset + subject + session pinned in JSON |
| Output | Bare `Raw` object | `RawIntake` object + IntakeReport + risk_log |

### Step 7. Journal line

> *"Reference and channel type are part of the physical measurement schema, not GUI settings; therefore the intake node must serialise inventory, montage, Nyquist margin, and events **before** any filter runs."*

---

# Assignment 1.2 — Referencing + Filtering

## Scenario

You receive the `RawIntake` object produced by Assignment 1.1. A colleague asks for *"a P300 analysis"* and *"a motor-imagery analysis"* of the same recording, in one preprocessing pass. They suggest *"just bandpass 1–40 Hz, it's universal"*. You must show, in Nimbus Studio, that **the choice of reference and bandpass is not a default — it is the address of the biological generator we want to read**.

## What to submit

- A Studio sub-graph implementing reference + filter chain (PNG + JSON configs).
- `preprocessing_config.json` saved as a versioned artefact.
- A **PSD comparison report** (before vs after filter) for occipital and central electrode groups.
- A **journal line** explaining what was kept biologically and what was removed by hardware.

## 📖 Neurophysiology required for this task

### What each frequency band physically is

| Band | Range | Physical generator |
|---|---|---|
| **δ (delta)** | 0.5–4 Hz | Slow cortical depolarisations; dominant in deep sleep and disorders of consciousness. |
| **θ (theta)** | 4–8 Hz | Hippocampal–prefrontal circuit; working memory, navigation, cognitive load. |
| **α (alpha)** | 8–13 Hz | **Thalamo-cortical loop** (Lopes da Silva); GABAergic interneuron gating of pyramidal cells; *pulsed inhibition* of task-irrelevant areas (Klimesch). |
| **β (beta)** | 13–30 Hz | Motor-cortex *status-quo* signalling; drops during movement (**ERD**), rebounds afterwards (**ERS**). |
| **γ (gamma)** | 30–80 Hz | Local feature binding; requires intact PING (pyramidal–interneuron) micro-circuits. |

→ **Choosing a passband == choosing which biological generator to look at.**

### What "reference" physically does

Three references map to three different biological assumptions:

- **Average reference.** Recomputes every channel relative to the mean of all scalp electrodes. Implicit hypothesis: *"the average of the scalp is a reasonable zero"*. Reasonable when coverage is dense and symmetric.
- **Mastoid (M1, M2) reference.** Anchors signal to the bony mastoids, which carry little cortical activity. Standard for ERP work (P300, N400) because it preserves slow components.
- **REST / infinity reference.** A computational estimate of a reference *"far away from any source"*. Useful for source-space analyses.

→ **Implication.** The reference is a **hypothesis about the zero of the field**, not a button you press.

### Why bandpass is paradigm-specific

- **P300:** the component lives 250–500 ms post-stimulus with a frequency content concentrated at **0.5–10 Hz**. A 1 Hz high-pass already starts to *attenuate* P300 morphology.
- **Motor imagery:** ERD/ERS lives in **mu (8–13 Hz) and beta (13–30 Hz)** — narrower band, higher cut-on.
- **General descriptive analysis:** 0.5–45 Hz, broad enough to retain all cortical phenomena above DC drift and below muscle dominance.

### Notch is hardware, not biology

A 50 Hz notch (EU mains) or 60 Hz notch (US mains) removes **power-line interference**, which is an electromagnetic artefact of the recording environment. Notch is **never biological** and must be documented as such.

## 🧮 Formulas needed for this task

### Average reference

$$ x_i^{\text{ref}}(t) = x_i^{\text{raw}}(t) - \frac{1}{N}\sum_{j=1}^{N} x_j^{\text{raw}}(t) $$

### Mastoid reference (linked mastoids)

$$ x_i^{\text{ref}}(t) = x_i^{\text{raw}}(t) - \frac{x_{M1}(t) + x_{M2}(t)}{2} $$

### Zero-phase IIR filter (filtfilt)

A causal IIR filter introduces group delay $\tau(f)$.  
**filtfilt** applies the filter forward and backward — net group delay is **0**, but the effective filter order doubles. This matters for the **transition band**: a 4th-order Butterworth becomes effectively 8th-order in filtfilt.

### PSD change at α-peak (acceptance criterion)

$$ \Delta P_\alpha = \frac{P_{\text{after}}(f_\alpha) - P_{\text{before}}(f_\alpha)}{P_{\text{before}}(f_\alpha)} $$

Acceptance: $|\Delta P_\alpha| < 0.10$ (α-pic must not be deformed by more than 10 % by the filter). Frequency shift of the α-peak must satisfy $|\Delta f_\alpha| < 1$ Hz.

## Solution walkthrough

### Step 1. Logical hypothesis

A *"universal 1–40 Hz bandpass"* is universal only in the sense that it produces a number for every paradigm — but it **mutilates P300** (loses slow morphology) and adds **no benefit** for motor imagery (which lives above 8 Hz). Different paradigms → different chains, sharing only intake.

### Step 2. Where calculation is required

1. Verify that the chosen highpass does not deform the α-peak (acceptance: $|\Delta P_\alpha| < 0.10$).
2. Verify that the notch frequency matches the recording country's mains.
3. Verify filtfilt group delay is zero (sanity).

### Step 3. Calculation

For the MI configuration (bandpass 8–30 Hz):
- α-peak in raw data: $f_\alpha = 10.2$ Hz, $P_{\text{before}}(f_\alpha) = 12.4$ µV²/Hz.
- After bandpass 8–30 Hz: $P_{\text{after}}(f_\alpha) = 11.6$ µV²/Hz.

$$ \Delta P_\alpha = (11.6 - 12.4) / 12.4 = -0.065 \quad \Rightarrow \quad |\Delta P_\alpha| = 0.065 < 0.10 \quad \checkmark $$

For the P300 configuration (bandpass 0.5–10 Hz): the α-peak sits at the upper edge of the band, so the acceptance criterion is *expected* to be near 0.10 — we tolerate up to that bound and **document** it.

### Step 4. ❌ Naive pipeline

```
[RawIntake] → [notch 50] → [bandpass 1-40] → [downstream]
```

| Error | Why it is wrong physically |
|---|---|
| `notch 50` hard-coded | Recording country was not asserted; if the file is from a 60 Hz mains country, 50 Hz notch removes *cortical* signal and leaves the interference. |
| `bandpass 1-40` for *all* paradigms | Attenuates P300; offers no MI benefit; entangles two analyses that need different chains. |
| No `psd_comparator` | No acceptance criterion → the engineer never knows whether the filter killed the α-peak. |
| No `reference_setter` | The implicit reference (often Cz or recording reference) silently becomes the result's *"zero"* without justification. |

### Step 5. ✅ Correct pipeline (Studio graph + JSON config)

```
[RawIntake]
  → [reference_setter: average | mastoid]
  → [notch: line_freq (50 or 60)]
  → [bandpass: paradigm_specific]
  → [psd_comparator]
  → [preprocessing_config.json emitter]
```

`preprocessing_config.json`:

```json
{
  "reference": {
    "scheme": "average",
    "rationale": "dense 22-channel scalp coverage; no mastoids in montage"
  },
  "notch": {
    "line_freq": 50,
    "width_hz": 1.0,
    "method": "fir",
    "rationale": "EU recording"
  },
  "bandpass_variants": {
    "p300":      { "l_freq": 0.5, "h_freq": 10.0, "method": "fir", "phase": "zero" },
    "motor_imagery": { "l_freq": 8.0, "h_freq": 30.0, "method": "fir", "phase": "zero" },
    "broad":     { "l_freq": 0.5, "h_freq": 45.0, "method": "fir", "phase": "zero" }
  },
  "psd_acceptance": {
    "alpha_peak_drift_hz_max": 1.0,
    "alpha_power_change_max": 0.10
  }
}
```

### Step 6. Direct comparison — ❌ vs ✅

| Aspect | ❌ Naive | ✅ Correct |
|---|---|---|
| Reference | Implicit | Explicit `average` / `mastoid` with rationale |
| Notch | Hard-coded 50 Hz | Sourced from `line_freq` metadata |
| Bandpass | 1–40 Hz universal | Paradigm-specific variants |
| Acceptance check | None | `psd_comparator` against α-peak drift |
| Reproducibility | Filter constants live in code | `preprocessing_config.json` artefact |

### Step 7. Journal line

> *"A bandpass is the address of a biological generator. Using 1–40 Hz for everything means asking 'what is happening?' instead of 'what is happening in the thalamo-cortical loop?' — the engineering choice loses physiological resolution."*

---

# Assignment 1.3 — Artifact Annotation (EOG / EMG / ECG / bad channels)

## Scenario

Your reviewer says the data *"has too much noise; please clean it up before features"*. The naive interpretation of *"clean it up"* is to **delete loud epochs**. But the loud epochs are not *noise* — each one carries a signal from **another physiological system** (eyes, face muscles, heart). You must **annotate** these sources rather than blindly reject them.

## What to submit

- A Studio sub-graph implementing artifact annotation (PNG + JSON).
- `artifact_table.csv` with one row per detected event: `t_start`, `t_end`, `source` ∈ {`eog`, `emg`, `ecg`, `bad_channel`, `other`}, `method`, `score`.
- An updated `risk_log.md` with a mitigation plan for each artefact type detected.
- A **journal line** describing the per-class physiological source of each rejected epoch.

## 📖 Neurophysiology required for this task

### EMG (electromyogram)

A single **motor unit action potential** is generated by tens to hundreds of muscle fibres firing together; its amplitude is **orders of magnitude larger** than a cortical PSP. Spectrum: broadband, dominant **30–200 Hz**. Anatomy: face and neck muscles sit closer to forehead electrodes than the motor cortex sits to C3 — **proximity wins**.

→ **Implication.** Even if a recording session is "calm", any jaw or forehead tension dominates frontal channels in the high-β / γ range.

### EOG (electrooculogram)

The **cornea is positive relative to the retina** — the eye is a battery. When the eye moves or blinks, this corneo-retinal dipole projects strongly onto the **frontal electrodes** (Fp1, Fp2, Fpz). Amplitude: 50–200 µV. Frequency content: low (DC–10 Hz), with a sharp transient on blinks.

→ **Implication.** Blinks are **signals of the oculomotor system**, not background noise. They have anatomy, latency, and lateralisation just like cortical signals.

### ECG (electrocardiogram)

The cardiac dipole propagates through the head by volume conduction. The **QRS complex** (sharp peak at 1–2 Hz inter-beat interval) is most visible at **temporal electrodes T7/T8** and increases with mastoid referencing.

### Galvanic skin response (GSR/EDA)

Sweat-gland activity produces a **slow drift below 0.5 Hz**. It correlates with arousal and is biologically meaningful — but it is *not cortex*.

### Bad channel — three physical causes

1. **High impedance** (gel dried, hair under electrode) → variance much larger than neighbours.
2. **Disconnected** → variance much smaller (flatness).
3. **Bridged** with neighbour → correlation $\rho \to 1$ with adjacent electrode.

## 🧮 Formulas needed for this task

### EOG detection via correlation

$$ \rho(x_{\text{Fp}}, x_{\text{EOG}}) = \frac{\text{cov}(x_{\text{Fp}}, x_{\text{EOG}})}{\sigma(x_{\text{Fp}})\,\sigma(x_{\text{EOG}})} $$

Threshold: $|\rho| > 0.7$ on a sliding 1-second window marks an EOG event.

### EMG index (bandpower ratio)

$$ \text{EMG}_\text{idx} = \frac{P_{30\text{-}80}}{P_{8\text{-}13}} $$

Threshold: $\text{EMG}_\text{idx} > \kappa$ (typical $\kappa \in [3, 5]$ after normalising per channel).

### Bad-channel variance criterion

$$ \text{variance}(x_c) > 5 \cdot \text{median}_n[\text{variance}(x_n)] $$

where the median is taken over neighbouring channels $n$.

### Peak-to-peak amplitude (epoch rejection)

$$ \text{PtP}(x) = \max(x) - \min(x) $$

Typical EEG threshold: 100–150 µV (paradigm-dependent, must be documented).

## Solution walkthrough

### Step 1. Logical hypothesis

"Cleaning" is the wrong verb. The correct verb is **separating**. We do not delete loud epochs; we tag *why* they are loud. The taxonomy is fixed (EOG, EMG, ECG, bad channel, other) and each tag has a specific detection rule rooted in the physiology above.

### Step 2. Where calculation is required

- One correlation per Fp electrode against each EOG channel.
- One bandpower ratio per channel for EMG index.
- One variance ratio per channel for bad-channel detection.
- One peak-to-peak amplitude per epoch.

### Step 3. Calculation (worked example for a single epoch)

Channel `Fp1`, epoch `t = 12.4 s`:
- $\rho(\text{Fp1}, \text{EOG1}) = 0.84$ → **EOG event** (above 0.7).
- $P_{30\text{-}80}(\text{Fp1}) / P_{8\text{-}13}(\text{Fp1}) = 1.7$ → not EMG (below κ = 3).
- $\text{variance}(\text{Fp1}) / \text{median}(\text{neighbours}) = 1.4$ → not bad channel.

→ Tag: `eog`, score `0.84`, method `corr(Fp,EOG)`, action *"keep, exclude from ICA training, do not reject"*.

### Step 4. ❌ Naive pipeline

```
[bandpassed_raw] → [reject epochs where PtP > 100 µV] → [ICA] → [features]
```

| Error | Why it is wrong physically |
|---|---|
| Single global PtP threshold | Treats blink-dominated frontal channels and clean occipital channels the same. |
| Reject without a `source` tag | Loses the information that *the* artefact source was the eye, not "noise". |
| EOG channels unused | The richest source of information about the eye is discarded. |
| Bad-channels untouched | A flat or bridged channel poisons every following spatial method (CSP, ICA, average reference). |
| No `risk_log` update | The pipeline silently shrinks the dataset. |

### Step 5. ✅ Correct pipeline

```
[preprocessed_raw]
  → [eog_detector]
  → [emg_bandpower_detector]
  → [ecg_detector]
  → [bad_channel_finder]
  → [epoch_rejection_rules]
  → [annotation_writer]
  → [artifact_table.csv]
```

Config:

```json
{
  "eog_detector":  { "method": "corr_with_eog_channel", "threshold": 0.7, "window_s": 1.0 },
  "emg_detector":  { "method": "bandpower_ratio", "high_band": [30, 80], "low_band": [8, 13], "kappa": 3.0 },
  "ecg_detector":  { "method": "qrs_template_corr", "channel": "T8", "threshold": 0.6 },
  "bad_channels":  { "variance_ratio_max": 5.0, "flatness_floor": 0.1, "neighbour_corr_min": 0.4 },
  "epoch_reject":  { "ptp_uv": 150.0, "muscle_index_max": 5.0 },
  "annotations":   { "write_to": "raw.annotations", "json_out": "artifact_table.csv" }
}
```

### Step 6. Direct comparison — ❌ vs ✅

| Aspect | ❌ Naive | ✅ Correct |
|---|---|---|
| Logic | "Loud = bad" | "Loud = another physiological system" |
| EOG channels | Ignored | Used as detection triggers |
| Per-class table | None | `artifact_table.csv` |
| Risk register | Unchanged | Updated per artefact class |
| Downstream impact | Random epoch loss | Targeted handling per source |

### Step 7. Journal line

> *"Every rejected epoch must carry a physiological source label; otherwise the engineer is silently choosing what counts as 'brain' and what counts as 'not brain' on amplitude alone."*

---

# Assignment 1.4 — Baseline & Nonstationarity (epochs + session metadata)

## Scenario

The recording protocol used four blocks of motor-imagery trials over ~30 minutes. The subject reports being *"more tired"* in block 4. A junior colleague has already epoched the data with `tmin = -0.2 s, tmax = 0.8 s, baseline = (None, None)`, applied z-scoring across the *entire session*, and is now confused why the test accuracy looks "suspiciously high" yet the per-block accuracy declines. You must demonstrate that **nonstationarity is biological**, fix the baseline policy, and protect against information leakage.

## What to submit

- A Studio sub-graph implementing baseline correction + session metadata (PNG + JSON).
- Updated epochs with `baseline = (-0.2, 0.0)` and an explicit `session_metadata` block.
- A `norm_policy.json` describing where normalisation parameters are estimated (train-only) and how they are reused.
- A `leakage_demo.ipynb` showing the accuracy gap between leaky and correct normalisation.
- A **journal line** distinguishing between-session and between-subject normalisation.

## 📖 Neurophysiology required for this task

### The brain is not stationary

The brain's electrical state changes with:

- **Neuromodulators.** **Acetylcholine** *desynchronises* cortex (think: attention, novelty). **Noradrenaline** increases β and arousal. **Dopamine** modulates reward-related signals.
- **Habituation.** A repeated stimulus elicits progressively *smaller* responses — the neuron is adapting, the data are still correct.
- **Circadian phase.** Morning and evening recordings show measurable spectral differences.
- **Fatigue.** Block N is electrically different from block 1 even with identical instructions.
- **Inter-subject variability.** Two healthy subjects share the same physics but not the same parameter values.

→ **Implication.** A "session" is a **window of approximate stationarity**, not a uniform sample. Anything that aggregates statistics *across* a session (e.g., a single z-score) implicitly **mixes brain states**.

### Why baseline correction is mandatory

The pre-stimulus interval is **the only honest "zero"** we have for that particular trial: it is the cortical state immediately before the event of interest, under the same neuromodulatory and circadian conditions. Subtracting this baseline isolates the **event-related deviation** from the **ongoing state**.

If the baseline window overlaps the stimulus or includes a previous response, the correction *destroys* the very effect we are trying to measure.

### Train-only normalisation

A z-score computed across all data leaks future statistics into the past. From the model's perspective this is *cheating*: the model "knows" something about the test trials before it sees them. The accuracy goes up; the biological interpretation goes nowhere.

## 🧮 Formulas needed for this task

### Per-epoch baseline correction

$$ x^{\text{corr}}_{\text{epoch}}(t) = x_{\text{epoch}}(t) - \overline{x_{\text{epoch}}(t')}_{\,t' \in [t_b^-, t_b^+]} $$

where $[t_b^-, t_b^+]$ is the baseline window (here $[-0.2, 0]$ s relative to the cue).

### Train-only z-score

$$ \mu_{\text{train}} = \text{mean}(x_{\text{train}}), \quad \sigma_{\text{train}} = \text{std}(x_{\text{train}}) $$

$$ z(x) = \frac{x - \mu_{\text{train}}}{\sigma_{\text{train}}} $$

Apply **the same** $\mu_{\text{train}}, \sigma_{\text{train}}$ to validation, test, and live streaming.

### Robust alternative (heavy-tailed features)

$$ \text{MAD}(x) = \text{median}(|x - \text{median}(x)|) $$

$$ z_{\text{robust}}(x) = \frac{x - \text{median}_{\text{train}}}{1.4826 \cdot \text{MAD}_{\text{train}}} $$

### Block-level fatigue indicator (simple proxy)

$$ R_{\text{block}} = \frac{\text{n\_rejected\_epochs}}{\text{n\_total\_epochs}} \cdot 100\,\% $$

A monotonic rise in $R_{\text{block}}$ across blocks is a fatigue signature, **not** a pipeline failure.

## Solution walkthrough

### Step 1. Logical hypothesis

The "high test accuracy + falling per-block accuracy" pattern is the signature of **leakage + fatigue mixed in**. Fixing both requires two independent corrections:
1. Baseline correction per epoch with the correct window.
2. Normalisation parameters estimated only on train, time-split (not random-split).

### Step 2. Where calculation is required

- Mean of baseline window per epoch (vectorised).
- $\mu, \sigma$ (or median/MAD) per channel on the **train fold only**.
- Block-level rejection rate $R_{\text{block}}$ to document fatigue.

### Step 3. Calculation (illustrative numbers)

- Pipeline A (leaky z-score, random split): test accuracy = **0.92**.
- Pipeline B (train-only z-score, time split): test accuracy = **0.78**.
- The 0.14 gap is the size of the lie.

Block rejection rates: 6 % → 9 % → 14 % → 22 %. Monotonic → fatigue documented in `session_metadata`.

### Step 4. ❌ Naive pipeline

```
[filtered_raw]
  → [epoch_creator: tmin=-0.2, tmax=0.8, baseline=None]
  → [z_score_full_session]
  → [random_train_test_split]
  → [features]
```

| Error | Physical / statistical consequence |
|---|---|
| `baseline=None` | Pre-stimulus drift contaminates every event-related effect. |
| `z_score_full_session` | Future statistics leak into past trials. |
| `random_train_test_split` | Two consecutive epochs (≈ same brain state) end up in train *and* test — trivial accuracy. |
| No `session_metadata` | Fatigue / block / impedance are invisible to downstream tooling. |

### Step 5. ✅ Correct pipeline

```
[artifact_annotated_raw]
  → [epoch_creator: tmin=-0.2, tmax=0.8, baseline=(-0.2, 0.0)]
  → [baseline_corrector]
  → [session_metadata_emitter]
  → [time_aware_train_val_test_split]
  → [norm_policy_emitter (train-only μ/σ or median/MAD)]
  → [normalised_features]
```

Config:

```json
{
  "epoch_creator": { "tmin": -0.2, "tmax": 0.8, "baseline": [-0.2, 0.0] },
  "session_metadata": {
    "blocks": 4,
    "block_duration_s": 360,
    "fatigue_proxy": "rejection_rate_per_block",
    "impedance_log": "artifacts/impedance.csv"
  },
  "split": { "method": "time_aware", "train": 0.60, "val": 0.20, "test": 0.20 },
  "normalisation": {
    "scheme": "zscore",
    "fit_on": "train",
    "params_path": "artifacts/norm_params.json",
    "robust_alternative": "median_mad"
  }
}
```

### Step 6. Direct comparison — ❌ vs ✅

| Aspect | ❌ Naive | ✅ Correct |
|---|---|---|
| Baseline | None / whole epoch | `(-0.2, 0.0)` — pre-stimulus only |
| Z-score | Full session | Train-only, saved as artefact |
| Split | Random | Time-aware |
| Fatigue | Invisible | Block-level rejection rate logged |
| ERP shape (P300) | Smeared by drift | Pinned to baseline |

### Step 7. Journal line

> *"Baseline correction is not cosmetic; it acknowledges that the brain has a state at $t_0$. Cross-session normalisation accepts inter-session drift; cross-subject normalisation accepts biological variability — they are not the same operation."*

---

# Assignment 1.5 — ICA Cleaning (independent components)

## Scenario

Your dataset, after baseline correction, still shows a clear frontal blink artefact and a faint ECG-like 1.2 Hz pulsation on temporal channels. A teammate writes a one-liner that runs ICA on the raw data, drops components 3 and 7 *"because they look weird"*, and ships. You must demonstrate why this is dangerous, build a correct ICA sub-graph, and *prove* that no cortical α-component was destroyed.

## What to submit

- A Studio sub-graph implementing ICA fit / inspect / label / apply (PNG + JSON).
- An **ICA report** (topomap + time course + PSD per component, before/after sensor-space PSD).
- The saved **unmixing matrix** $W$ and the list of excluded components with labels.
- A **journal line** distinguishing a body artefact from a cortical network that must be preserved.

## 📖 Neurophysiology required for this task

### Functional segregation justifies ICA

Different cortical areas perform partially independent computations. At any moment, scalp EEG is a **linear mixture** of these sources plus body signals (EOG, EMG, ECG). ICA assumes the sources are **statistically independent** (stronger than uncorrelated). For *most* tasks this is approximately true; for tightly coupled processes (attention + working memory) the assumption is **violated** — ICA is not magic.

### What a component "looks like" physiologically

| Component signature | Topomap | Time course | PSD | Label |
|---|---|---|---|---|
| **Eye blink** | Strong frontal dipole, anti-symmetric | Sharp downward pulses | Low-frequency dominant | `eog` |
| **Saccade** | Left/right frontal asymmetry | Step-like | Low | `eog` |
| **ECG** | Subtle, often temporal | Sharp QRS-like spikes at 1–2 Hz | 1–2 Hz peak | `ecg` |
| **EMG** | Focal, lateral or jaw region | Continuous broadband | 30–80 Hz dominant | `emg` |
| **Cortical α** | Symmetric posterior dipole | Smooth oscillation at ~10 Hz | Sharp 8–13 Hz peak | **`brain` (keep!)** |
| **DMN-like** | Midline parietal | Slow modulation | Broad 1–10 Hz | **`brain` (keep!)** |

### Why a 1 Hz high-pass *before* ICA is non-negotiable

ICA convergence assumes stationary statistics. Slow drifts (< 1 Hz: GSR, electrode drift, breathing) violate this assumption and produce *meaningless* components. The standard practice is a temporary 1 Hz high-pass **for ICA fitting only**; the unmixing matrix is then applied to the original (lower-passed) data.

### Rank check is biology, not math trivia

If you have re-referenced to average, the data **rank drops by 1**. If you have interpolated 2 bad channels, it drops by 2 more. Fitting ICA with `n_components = n_channels` on rank-deficient data yields **spurious** components that look real but are linear combinations of noise.

## 🧮 Formulas needed for this task

### Mixing / unmixing

$$ X = A \cdot S \quad \Longleftrightarrow \quad S = W \cdot X, \quad W \approx A^{-1} $$

with $X \in \mathbb{R}^{n_{\text{ch}} \times n_t}$ (sensors), $S$ (sources), $A$ mixing matrix, $W$ unmixing matrix.

### Data rank

$$ \text{rank}(X) \le \min(n_{\text{ch}}, n_t) $$

After average reference: $\text{rank}(X) \le n_{\text{ch}} - 1$. After interpolating $k$ bad channels: $\text{rank}(X) \le n_{\text{ch}} - 1 - k$.

### α-retention acceptance criterion

$$ \Delta_\alpha = \frac{P_\text{after}(f_\alpha) - P_\text{before}(f_\alpha)}{P_\text{before}(f_\alpha)} $$

Acceptance: **$\Delta_\alpha > -0.30$**. If applying the unmixing matrix removed more than 30 % of α-power at posterior electrodes, the engineer almost certainly removed a cortical component by mistake — **revert**.

### Component score for EOG correlation (auto-labelling)

$$ s_k^{\text{eog}} = |\rho(s_k(t), x_{\text{EOG}}(t))| $$

with $s_k$ the $k$-th IC time course. Components with $s_k^{\text{eog}} > 0.5$ are flagged as `eog` candidates and confirmed by topomap inspection.

## Solution walkthrough

### Step 1. Logical hypothesis

If ICA is fitted on raw data without a 1 Hz high-pass and the engineer prunes components without inspection, **at least one cortical component is statistically likely to be deleted**. The α-retention test is the cheapest insurance against this failure mode.

### Step 2. Where calculation is required

- Estimate data rank after average reference and interpolation.
- Compute EOG correlation score per component.
- Compute $\Delta_\alpha$ before vs after applying the unmixing.

### Step 3. Calculation

- 22 EEG channels, average reference, 0 interpolated → expected ICA rank = 21.
- Posterior α-power on `O1` before: $P_\text{before}(10.2) = 14.7$ µV²/Hz.
- After removing 2 components labelled `eog`/`ecg`: $P_\text{after}(10.2) = 13.6$ µV²/Hz.
- $\Delta_\alpha = (13.6 - 14.7)/14.7 = -0.075 > -0.30 \checkmark$ → safe to commit.

### Step 4. ❌ Naive pipeline

```
[raw] → [ICA n_components=22] → [drop IC 3, 7] → [downstream]
```

| Error | Consequence |
|---|---|
| No 1 Hz high-pass | ICA fails to separate; components mix slow drift with cortical activity. |
| `n_components = n_channels` | Rank-deficient; spurious components appear. |
| Drop by index, no inspection | A cortical α-component may be silently destroyed. |
| No `unmixing_matrix` saved | The transformation is irreproducible in Level 2 streaming. |
| No `α-retention` check | The engineer never learns of the mistake. |

### Step 5. ✅ Correct pipeline

```
[reference_filtered_raw]
  → [highpass 1 Hz for ICA fit only]
  → [rank_estimator]
  → [ICA_fit: picard, n_components = rank]
  → [IC_inspector: topomap + time + PSD]
  → [auto_labeller: eog/ecg/emg via correlations]
  → [manual_confirm]
  → [apply_exclude_to_original_raw]
  → [psd_alpha_validator]
  → [save_unmixing_matrix W + label_map]
```

Config:

```json
{
  "ica": {
    "method": "picard",
    "n_components": "rank_aware",
    "highpass_for_fit_hz": 1.0,
    "random_state": 42
  },
  "labelling": {
    "eog_threshold": 0.5,
    "ecg_threshold": 0.5,
    "manual_confirm": true
  },
  "validation": {
    "alpha_retention_min": -0.30,
    "posterior_channels": ["O1", "O2", "Pz"]
  },
  "outputs": {
    "unmixing_matrix": "artifacts/W.npy",
    "label_map": "artifacts/ica_labels.json",
    "report": "artifacts/ica_report.html"
  }
}
```

### Step 6. Direct comparison — ❌ vs ✅

| Aspect | ❌ Naive | ✅ Correct |
|---|---|---|
| Pre-processing | None | 1 Hz HP for fit |
| `n_components` | = n_channels | = rank |
| Selection | By index | Inspect + label + confirm |
| Safety net | None | α-retention check |
| Reproducibility | None | `W.npy` + `label_map.json` saved |

### Step 7. Journal line

> *"ICA separates statistically independent sources; whether a source is a body artefact or a cortical network is a physiological judgement, not a numerical one. The α-retention check enforces that judgement quantitatively."*

---

# Assignment 1.6 — Quality Dashboard (SNR, α-peak, rejection rate)

## Scenario

A reviewer asks for a *"quality report"* to decide whether the recording is good enough to enter the L2 decoder. You realise that *"accuracy"* is a downstream metric and answers the wrong question — we need to know whether the *signal itself* is interpretable, **before** any decoder is trained. You must build a dashboard whose verdicts have a physiological reading.

## What to submit

- A Studio sub-graph implementing the quality dashboard (PNG + JSON).
- An HTML report `quality_dashboard.html` containing per-channel SNR, PSD, α-peak frequency, channel variance, finite-value rate, % rejected epochs, and a `physiological caveats` section.
- A `quality_gates.json` file: thresholds and the **PASS / WARN / FAIL** verdict per gate.
- A **journal line** translating the dashboard verdict into a statement about subject state and protocol.

## 📖 Neurophysiology required for this task

### A "good recording" is a chain of biological conditions

- **Electrode impedance** of 5–20 kΩ → ionic contact across skin / gel / metal. Above 50 kΩ → noise dominates.
- **Skin** behaves as a frequency-dependent filter (stratum corneum); hydration matters.
- **Subject anxiety** → tonic EMG → broadband high-frequency pollution.
- **Fatigue** → blink rate ↑, α-power ↑, ERD attenuation.
- **Temperature / humidity** → change gel conductivity over time.

→ **Implication.** SNR and α-peak shifts are *not* "hardware metrics" — they are the chain *(skin → impedance → amplifier → arousal → cortex)* expressed in numbers.

### The α-peak as a sanity oracle

A healthy adult with eyes closed shows an α-peak in **7.5–13 Hz**, narrowest and tallest at **O1, O2, Pz**. A missing α-peak (after correct preprocessing) suggests either a wrong reference, a destroyed cortical component (see Assignment 1.5), or an extremely aroused subject. A drifted α-peak hints at fatigue or medication effects.

### Block-level decline is biology, not failure

Increasing rejection rate or decreasing SNR across recording blocks signals **habituation + fatigue + blink frequency rise** — *the recording is honest about the brain getting tired*. The dashboard must surface this so the engineer doesn't blame the model.

## 🧮 Formulas needed for this task

### SNR (signal-to-noise ratio, per channel)

$$ \text{SNR}_c = 10 \log_{10}\left( \frac{P_{\text{signal,c}}}{P_{\text{noise,c}}} \right) \quad [\text{dB}] $$

where $P_{\text{signal}}$ is power in the paradigm-relevant band (e.g., 0.5–45 Hz for broad descriptive use) and $P_{\text{noise}}$ is power in a *guard* band where no cortical signal is expected (e.g., 0.1–0.4 Hz, after notch).

### α-peak frequency estimator

$$ f_\alpha = \arg\max_{f \in [7,14]} \overline{\text{PSD}_O}(f) $$

with $\overline{\text{PSD}_O}$ the mean PSD over occipital channels.

### Rejection rate

$$ R = \frac{n_{\text{rejected}}}{n_{\text{total}}} \times 100\,\% $$

### Finite-value rate

$$ \text{finite\_rate} = \frac{|\{x : \text{isfinite}(x)\}|}{|x|} $$

Acceptance: **exactly 1.0**. Anything below 1.0 indicates NaN/Inf in the data — fatal.

### Quality gates

| Gate | Acceptance | Verdict if violated |
|---|---|---|
| `snr_min_db` | $\text{SNR}_c \ge 3$ on all EEG channels | **FAIL** if more than 2 channels below; else WARN |
| `alpha_peak_in_band` | $f_\alpha \in [7, 14]$ Hz | **WARN** |
| `rejection_rate_max` | $R \le 40\,\%$ | **FAIL** |
| `finite_rate` | $= 1.0$ | **FAIL** |
| `channel_variance_ratio` | $\le 5\times$ median | **WARN** |

## Solution walkthrough

### Step 1. Logical hypothesis

A quality verdict must be *separable* from the decoder. We measure properties of the signal itself, against thresholds that translate back to physiology. The dashboard's failure mode is silent: if the engineer sees only "accuracy 0.86", they cannot tell whether they have a bad recording or a bad model.

### Step 2. Where calculation is required

- SNR per channel.
- α-peak frequency on occipital group.
- Rejection rate per block and overall.
- Finite-value rate.
- Channel variance ratio against median.

### Step 3. Calculation (illustrative)

- SNR median across EEG channels: 6.2 dB. Two channels below 3 dB → WARN.
- $f_\alpha = 10.3$ Hz → PASS.
- Overall rejection rate $R = 18\,\%$ → PASS. Block-wise: 6, 9, 14, 22 % → fatigue caveat added.
- Finite rate = 1.0 → PASS.
- Channel variance ratio max: 3.6× → PASS.

Overall verdict: **PASS with WARN** (two low-SNR channels, fatigue trend).

### Step 4. ❌ Naive pipeline

```
[clean_data] → [train_decoder] → [accuracy] → "OK / not OK"
```

| Error | Consequence |
|---|---|
| Single number for "quality" | Confuses signal quality and decoder quality. |
| No per-channel SNR | Cannot pinpoint bad electrodes. |
| No α-peak check | Cannot detect destroyed cortical components. |
| No finite check | NaN/Inf can pass silently. |
| No physiological caveats | Reviewer cannot interpret the verdict. |

### Step 5. ✅ Correct pipeline

```
[clean_epochs]
  → [per_channel_snr]
  → [psd_estimator]
  → [alpha_peak_finder: O1, O2, Pz]
  → [rejection_rate_per_block]
  → [region_grouper: frontal/central/parietal/occipital]
  → [finite_value_check]
  → [paradigm_aware_gate]
  → [verdict_writer]
  → [jinja2: quality_dashboard.html]
```

Config:

```json
{
  "gates": {
    "snr_min_db": 3.0,
    "alpha_peak_band_hz": [7.0, 14.0],
    "rejection_rate_max": 0.40,
    "finite_rate": 1.0,
    "channel_variance_ratio_max": 5.0
  },
  "groups": {
    "frontal":  ["Fp1","Fp2","F3","F4","Fz"],
    "central":  ["C3","C4","Cz"],
    "parietal": ["P3","P4","Pz"],
    "occipital":["O1","O2"]
  },
  "report": {
    "template": "templates/dashboard.html",
    "out": "artifacts/quality_dashboard.html",
    "include_caveats": true
  }
}
```

### Step 6. Direct comparison — ❌ vs ✅

| Aspect | ❌ Naive | ✅ Correct |
|---|---|---|
| What is measured | Accuracy | Signal quality, separately |
| Resolution | Single number | Per channel + per block + per group |
| α-peak | Not checked | Required, in band |
| Caveats | None | Free-text physiological caveats section |
| Verdict | Binary | PASS / WARN / FAIL per gate, with overall verdict |

### Step 7. Journal line

> *"The dashboard verdict is a sentence about the subject and the protocol — 'two electrodes near the temples were low-impedance unfriendly, the subject's α drifted slightly between block 1 and block 4' — not a sentence about the decoder."*

---

# Assignment 1.7 — Public Datasets + Nimbus Feature Contract (replication)

## Scenario

You have a working Level 1 pipeline on the local recording. The team lead asks: *"Does it also work on a public dataset, with no code changes other than the data source?"* This is the replication test. To pass it, the pipeline must carry a **feature contract**, a **metadata schema**, and **train-only normalisation parameters** that survive a change of dataset.

## What to submit

- A Studio sub-graph wrapping the entire L1 pipeline + replication runner (PNG + JSON).
- A `feature_metadata.json` describing every feature (name, units, shape, paradigm, train-only stats).
- A `replication_script.py` runnable with **one command** to reproduce the local result on MOABB.
- A `cross_dataset_comparison.md` reporting subject-level and session-level variance, plus a KL-divergence comparison of feature distributions.
- A **journal line** stating what transfers between datasets and what stays local.

## 📖 Neurophysiology required for this task

### Why two healthy datasets disagree

- **Age, sex, education, meditation history** all shift the spectrum measurably.
- The **α-peak frequency** is a *distribution* between 8 and 13 Hz, not a constant 10 Hz.
- **Heritability** of individual EEG rhythms is high (twin studies report up to ~80 % for some bands).
- **BCI-naive vs trained** users differ at the level of motor imagery strategy and ERD topography.
- **Cultural / cognitive strategies** for tasks like Stroop or N-back differ across labs.

→ **Implication.** A transfer gap is **not a model failure** — it is the sum of biological variability and protocol variability. A pipeline that pretends otherwise will overfit to one cohort.

### Feature contract is physiology-aware

| Paradigm | Feature family | Why it matches biology |
|---|---|---|
| **P300** | ERP amplitudes in 250–500 ms windows | The component lives in those windows by anatomy. |
| **SSVEP** | Bandpower at stimulation frequency and harmonics | V1 phase-locks to the stimulus. |
| **Motor imagery** | Log-variance of CSP components in 8–30 Hz | ERD/ERS lives in mu/beta. |
| **Resting / connectivity** | Spectral or coherence features per band | Each band addresses one generator. |

A model in Level 2 should never receive *raw EEG*; it should receive **features whose definition is paradigm-justified**.

## 🧮 Formulas needed for this task

### KL divergence between feature distributions

$$ D_{\text{KL}}(P \| Q) = \sum_x P(x) \log\frac{P(x)}{Q(x)} $$

Used to quantify the distance between the *same feature* on local and public data. Low $D_{\text{KL}}$ ⇒ features transfer; high $D_{\text{KL}}$ ⇒ document a transfer caveat.

### Subject-level vs session-level variance

$$ \sigma^2_{\text{subject}} = \frac{1}{N_s - 1} \sum_{i=1}^{N_s}(\bar{x}_i - \bar{\bar{x}})^2 $$

$$ \sigma^2_{\text{session}} = \frac{1}{N_e}\sum_{i,j}(x_{ij} - \bar{x}_i)^2 $$

A pipeline that confounds these two variances at L2 will *think* it generalises but only ever learnt within-subject patterns.

### Robust feature stats (train-only)

$$ \mu_{\text{train}}, \sigma_{\text{train}} \quad \text{or} \quad \text{median}_{\text{train}}, \text{MAD}_{\text{train}} $$

Persisted in `feature_metadata.json`; loaded as-is at inference time on a new dataset.

## Solution walkthrough

### Step 1. Logical hypothesis

A pipeline that works *only because it was fitted on the same data it tests on* is indistinguishable from a pipeline that just memorised the dataset. The replication runner forces the pipeline to expose its assumptions as a *contract* — and forces the engineer to confront biological variability honestly.

### Step 2. Where calculation is required

- Feature distribution per dataset (histogram or KDE).
- KL divergence per feature between local and public data.
- Variance partition into subject-level vs session-level.

### Step 3. Calculation (illustrative)

- Local: 1 subject, 4 sessions → $\sigma^2_{\text{session}} = 0.13$.
- Public: 9 subjects, 2 sessions each → $\sigma^2_{\text{subject}} = 0.42$, $\sigma^2_{\text{session}} = 0.11$.
- Feature *"C3 mu power"* KL divergence local↔public = **0.18** (acceptable, documented).
- Feature *"Fp1 broadband variance"* KL divergence = **0.92** (high — likely driven by impedance/blink differences; flag as **local-only**).

### Step 4. ❌ Naive pipeline

```
[moabb_download] → [CSP fit on all data] → [z-score across all] → [export features]
```

| Error | Consequence |
|---|---|
| CSP fit on all data | Spatial filter sees test labels via shared statistics. |
| Z-score across all | Same leak as Assignment 1.4. |
| No `feature_metadata.json` | The downstream model has no contract to validate against. |
| No `cross_dataset_comparison.md` | Subject vs session variance never reported. |
| No `README` / single-command runner | Replication impossible. |

### Step 5. ✅ Correct pipeline

```
[full_L1_chain (1.1–1.6)]
  → [train_val_test_time_split]
  → [feature_extractor: paradigm_specific]
  → [norm_fit_train_only]
  → [feature_distribution_diagnostic]
  → [cross_dataset_comparator]
  → [feature_metadata.json + features.npz]
  → [replication_script.py + README]
```

Config:

```json
{
  "datasets": [
    { "name": "local",  "source": "internal/raw/", "subjects": [1] },
    { "name": "moabb",  "source": "BNCI2014_001", "subjects": [1,2,3,4,5,6,7,8,9] }
  ],
  "features": {
    "paradigm": "motor_imagery",
    "family": "csp_logvar",
    "n_csp": 6,
    "band_hz": [8.0, 30.0]
  },
  "split": { "method": "time_aware", "train": 0.6, "val": 0.2, "test": 0.2 },
  "normalisation": { "scheme": "median_mad", "fit_on": "train" },
  "comparison": {
    "metrics": ["kl_divergence", "subject_var", "session_var"],
    "report_out": "artifacts/cross_dataset_comparison.md"
  },
  "replication": {
    "entry_point": "python -m nimbus.l1.replication --config artifacts/l1_config.json",
    "readme_out": "artifacts/README.md"
  }
}
```

### Step 6. Direct comparison — ❌ vs ✅

| Aspect | ❌ Naive | ✅ Correct |
|---|---|---|
| CSP fit | All data | Train fold only |
| Normalisation | Across all | Train-only, persisted |
| Feature contract | None | `feature_metadata.json` |
| Cross-dataset report | None | `cross_dataset_comparison.md` with KL + variance |
| Reproducibility | Notebook in head | One-command `replication_script.py` |

### Step 7. Journal line

> *"What transfers across datasets are paradigm-grounded features and their physiologically justified bands; what stays local are absolute amplitudes, impedance signatures and subject-specific feature offsets. The feature contract is the explicit boundary between these two."*

---

# Assignment 1.CAP — Capstone: Full Analyst Pipeline (integration of 1.1–1.7)

## Scenario

You must deliver a single Studio graph that runs end-to-end *with no manual steps* and produces:
1. A Nimbus-ready **feature dataset** (`features.npz`).
2. A **preprocessing notebook** documenting every choice.
3. An **HTML / PDF quality report**.
4. A **Studio graph export** (`studio_graph.json`).

At the defence, you will be asked: *"Which preprocessing step would most change the physiological interpretation of the data if it were removed?"*

## What to submit

- A capstone Studio graph (PNG + JSON) composed of the seven sub-graphs from Assignments 1.1–1.7, plus a final `health_check_combined` node.
- The four artefacts listed above.
- A short **defence memo** (½ page) answering the defence question, ranked by impact.
- A **journal line** binding the answer to a biological mechanism.

## 📖 Neurophysiology required for this task

This capstone reuses every neurophysiological fact established in 1.1–1.7. No new facts are introduced; the assignment is a test of *integration* — does the engineer see the chain *(measurement schema → reference → bands → body artefacts → state → independent sources → quality → replication)* as **one biological argument**, or as seven disconnected scripts?

## 🧮 Formulas needed for this task

The capstone reuses the formulas from 1.1–1.7. The only *new* quantity is the **deployment readiness score**:

$$ \text{DRS} = \prod_{g \in \text{gates}} \mathbb{1}[\,g\text{ passes}\,] $$

DRS = 1 iff **every** quality gate passes. The combined health check is binary by design — partial passes are not acceptable for L2 entry.

## Solution walkthrough

### Step 1. Logical hypothesis

The pipeline is a single object whose **failure modes are physiological**, not architectural. Removing any one sub-graph must change something measurable about the signal's interpretation; the defence answer ranks them by how much.

### Step 2. Where calculation is required

A small ablation table. For each sub-graph $g \in \{$intake, reference, filter, artifacts, baseline, ICA, dashboard, replication$\}$, run the capstone *without* $g$ and record:
- α-peak shift (Hz).
- α-power retention $\Delta_\alpha$.
- Rejection rate $R$.
- DRS = 1/0.

### Step 3. Calculation (illustrative ranking)

| Removed sub-graph | $\Delta f_\alpha$ (Hz) | $\Delta_\alpha$ | $R$ | DRS | Interpretation impact |
|---|---:|---:|---:|---:|---|
| **Intake** (1.1) | n/a | n/a | n/a | 0 | Whole physical schema lost — *catastrophic*. |
| **ICA** (1.5) | +0.4 | −0.05 | +6 % | 0 | Blink dominates frontal; fronto-central interpretation invalid. |
| **Reference + filter** (1.2) | +1.2 | −0.18 | +3 % | 0 | Bands no longer match generators. |
| **Artifacts** (1.3) | +0.1 | −0.02 | +12 % | 0 | EMG bleeds into γ; bad channels poison spatial methods. |
| **Baseline** (1.4) | 0 | 0 | +1 % | 0 | ERP smeared by drift; leakage inflates accuracy. |
| **Dashboard** (1.6) | 0 | 0 | 0 % | 1 (?) | DRS passes but engineer cannot diagnose subject state. |
| **Replication** (1.7) | 0 | 0 | 0 % | 1 (?) | Pipeline works locally but cannot be defended on new data. |

→ Top of the ranking: **Intake** and **ICA labelling** — they change *what the signal is*. The dashboard and replication change *what we can say about it*, but not the signal itself.

### Step 4. ❌ Naive capstone

```
[load] → [bandpass] → [ICA] → [features] → [train] → [export]
```

Monolithic, no sub-graphs, no quality gates, no metadata. Works on the lab machine, breaks on a new subject.

### Step 5. ✅ Correct capstone

```
[intake_subgraph (1.1)]
  → [reference_filter_subgraph (1.2)]
  → [artifact_subgraph (1.3)]
  → [baseline_epoch_subgraph (1.4)]
  → [ica_subgraph (1.5)]
  → [feature_subgraph (1.7, paradigm-specific)]
  → [quality_dashboard_subgraph (1.6)]
  → [health_check_combined]
  → [export: features.npz + studio_graph.json + quality_dashboard.html + README.md]
```

Each sub-graph is a *reused* artefact from its assignment, not re-coded. The `health_check_combined` node aggregates all gates from 1.6 and emits the DRS.

### Step 6. Direct comparison — ❌ vs ✅ (capstone-level)

| Aspect | ❌ Naive capstone | ✅ Correct capstone |
|---|---|---|
| Structure | Monolithic script | Composed sub-graphs |
| Reuse | Copy-paste | Each sub-graph reused verbatim from its assignment |
| Quality gating | None | DRS = 1 required for L2 entry |
| Defence | "It worked on my data" | Ablation ranking + biological explanation |
| Generalisation | Local | Replication runner + cross-dataset report |

### Step 7. Journal line (capstone-level)

> *"The preprocessing steps that change **what the signal is** (intake and ICA labelling) dominate the steps that change **what we can say about the signal** (dashboard and replication). The order of preprocessing is therefore physiology first, then statistics, then reporting."*

---

# Editing notes for this document

- All headings use `#`/`##`/`###` so any TOC generator will rebuild the structure automatically.
- All formulas are LaTeX-in-Markdown (`$$ … $$`). GitHub and most renderers handle them natively. If the target editor does not, paste the LaTeX directly into the section you are editing — no other text changes required.
- All Studio graphs are plain bracketed pseudo-code blocks (` ``` `). Adding or renaming a node is a single-line edit.
- All configs are valid JSON inside fenced blocks. Add, remove, or change keys freely.
- All tables use standard Markdown pipe syntax. New rows are one line.
- The structure *"Scenario / What to submit / Neurophysiology / Formulas / Solution walkthrough (7 steps)"* is the canonical template. Use it for any new assignment added later.

*End of Level 1 Integrated Assignments — English edition.*
