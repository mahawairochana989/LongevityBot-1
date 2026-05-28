"""Nimbus BCI Problems — data for build_bci_problems_html.py."""

LEVEL_NAMES = {
    1: "Основы нейросигналов",
    2: "Обработка ЭЭГ",
    3: "Ритмы и паттерны",
    4: "Машинное обучение",
    5: "Байесовский вывод",
    6: "Пайплайны Nimbus",
    7: "Нелинейные методы",
    8: "Нейронные сети",
    9: "Real-Time системы",
}

TAG_COLORS = {
    "Нейрофизиология": "#00e5ff",
    "Обработка сигналов": "#7c4dff",
    "Ритмы и паттерны": "#00e676",
    "Машинное обучение": "#ffd740",
    "Байесовский вывод": "#69f0ae",
    "Пайплайны Nimbus": "#448aff",
    "Нелинейные методы": "#ff4081",
    "Нейронные сети": "#e040fb",
    "Real-Time системы": "#ff6e40",
}

PROBLEMS = [
    {
        "id": "EEG",
        "title": "Частота спайков и f-I кривая",
        "level": 1,
        "tag": "Нейрофизиология",
        "color": "#00e5ff",
        "emoji": "⚡",
        "difficulty": "★☆☆ Базовый",
        "description": """## Условие

Нейрон LIF (leaky integrate-and-fire) получает **постоянный ток** $I$. При $I < I_{\\min}$ частота спайков $f = 0$ Гц; при больших $I$ частота растёт. Зависимость $f(I)$ называется **f-I кривой**.

**Дано:**
- Период рефрактерности: $\\tau_{\\text{ref}} = 3$ мс
- Порог $I_{\\min} = 0{,}5$ нА — ниже этого тока спайков нет
- Линейный участок: $f = k \\cdot (I - I_{\\min})$, $k = 80$ Гц/нА

**Задачи:**
1. Какова **максимальная** частота спайков этого нейрона?
2. Вычислите $f$ при $I = 2{,}5$ нА.
3. Почему на скальпе мы видим **синхронность популяции**, а не отдельные спайки?

### Контекст BCI

EEG — это сумма полей **~10⁸ синхронных нейронов**. Частота ритма (например, α ≈ 10 Гц) — это не firing rate одного нейрона, а **осцилляция согласованности** популяции.""",
        "solution": """## Шаг 1. Максимальная частота

Рефрактерность ограничивает минимальный интервал между спайками:

$$f_{\\max} = \\frac{1}{\\tau_{\\text{ref}}} = \\frac{1}{0{,}003} \\approx 333 \\text{ Гц}$$

На практике реальные нейроны редко превышают 200–300 Гц из-за адаптации.

## Шаг 2. Расчёт f(I)

$$f = k \\cdot (I - I_{\\min}) = 80 \\cdot (2{,}5 - 0{,}5) = 160 \\text{ Гц}$$

160 Гц < 333 Гц → ограничение рефрактерности **не активно**.

## Шаг 3. Связь с EEG

| Масштаб | Что измеряем | Частота |
| --- | --- | --- |
| Один нейрон | Спайки | 0–300 Гц |
| Популяция (~1 см²) | Поле диполей | 0.5–100 Гц (EEG) |
| Скальп | Разность потенциалов | µV-диапазон |

```python
import numpy as np

def f_I_curve(I_nA, I_min=0.5, k=80.0, tau_ref_ms=3.0):
    f = np.maximum(0.0, k * (I_nA - I_min))
    f_max = 1000.0 / tau_ref_ms
    return np.minimum(f, f_max)

I = 2.5
print(f"f({I} nA) = {f_I_curve(I):.0f} Hz")
print(f"f_max = {1000/tau_ref_ms:.0f} Hz")
```

**Вывод:** f-I кривая описывает **одиночный нейрон**; EEG отражает **согласованность ансамбля**, а не сумму индивидуальных firing rates.""",
    },
    {
        "id": "MV",
        "title": "Уравнение Goldman и мембранный потенциал",
        "level": 1,
        "tag": "Нейрофизиология",
        "color": "#00e5ff",
        "emoji": "🔋",
        "difficulty": "★☆☆ Базовый",
        "description": """## Условие

Вы записываете **resting potential** нейрона и хотите понять, как ионы определяют $V_m$.

**Уравнение Goldman–Hodgkin–Katz (GHK):**

$$V_m = \\frac{RT}{F} \\ln \\frac{P_K [K^+]_{out} + P_{Na} [Na^+]_{out} + P_{Cl} [Cl^-]_{in}}{P_K [K^+]_{in} + P_{Na} [Na^+]_{in} + P_{Cl} [Cl^-]_{out}}$$

**Дано (мМ):**
| Ион | $[in]$ | $[out]$ | $P$ (относ.) |
| --- | --- | --- | --- |
| K⁺ | 140 | 5 | 1.0 |
| Na⁺ | 15 | 145 | 0.04 |
| Cl⁻ | 10 | 110 | 0.45 |

$RT/F ≈ 25{,}7$ мВ при 37°C.

**Задачи:**
1. Вычислите $V_m$ (мВ).
2. Что произойдёт с $V_m$, если **удвоить** $P_{Na}$ (открытие Na-каналов)?
3. Почему **depolarization** на EEG ≠ «больше спайков»?""",
        "solution": """## Шаг 1. Подстановка в GHK

Числитель:
$$N = 1.0 \\cdot 5 + 0.04 \\cdot 145 + 0.45 \\cdot 10 = 5 + 5.8 + 4.5 = 15.3$$

Знаменатель:
$$D = 1.0 \\cdot 140 + 0.04 \\cdot 15 + 0.45 \\cdot 110 = 140 + 0.6 + 49.5 = 190.1$$

$$V_m = 25.7 \\cdot \\ln(15.3 / 190.1) = 25.7 \\cdot (-2.51) \\approx \\mathbf{-64.5 \\text{ мВ}}$$

Типичный resting potential ✓

## Шаг 2. Удвоение P_Na

При $P_{Na} = 0.08$:
$$N' = 5 + 11.6 + 4.5 = 21.1 \\quad \\Rightarrow \\quad V_m' \\approx -58 \\text{ мВ}$$

→ **Depolarization** на ~6 мВ — приближение к порогу спайка.

## Шаг 3. Связь с EEG

Depolarization **локальной популяции** создаёт **отрицательный** потенциал на активном электроде (если диполи направлены к pia). Но EEG — **разность** $V_A - V_B$, и знак зависит от **референса** и **геометрии**.

```python
import numpy as np

RT_F = 25.7  # mV at 37°C

def goldman(P, conc_in, conc_out):
    num = P["K"]*conc_out["K"] + P["Na"]*conc_out["Na"] + P["Cl"]*conc_in["Cl"]
    den = P["K"]*conc_in["K"] + P["Na"]*conc_in["Na"] + P["Cl"]*conc_out["Cl"]
    return RT_F * np.log(num / den)

P = {"K": 1.0, "Na": 0.04, "Cl": 0.45}
cin = {"K": 140, "Na": 15, "Cl": 10}
cout = {"K": 5, "Na": 145, "Cl": 110}
print(f"Vm = {goldman(P, cin, cout):.1f} mV")
```

**Вывод:** Goldman задаёт **равновесный потенциал**; firing rate зависит от **динамики** каналов, а не только от $V_m$.""",
    },
    {
        "id": "PWR",
        "title": "Band power через FFT",
        "level": 2,
        "tag": "Обработка сигналов",
        "color": "#7c4dff",
        "emoji": "📊",
        "difficulty": "★★☆ Средний",
        "description": """## Условие

Дан 10-секундный фрагмент EEG канала **O1** (`sfreq = 250` Гц). Нужно оценить **band power** в полосах:
- **θ:** 4–8 Гц
- **α:** 8–13 Гц
- **β:** 13–30 Гц

**Задачи:**
1. Реализуйте Welch PSD и интегрируйте мощность по полосам.
2. Вычислите **относительную** α-мощность: $P_\\alpha / P_{total}$.
3. Субъект закрыл глаза → α(O1) выросла с 15% до 40%. Как это интерпретировать биологически?

### Ограничения

- Используйте **односторонний** спектр (удвоение, кроме DC и Nyquist).
- Полоса анализа: 1–40 Гц.""",
        "solution": """## Шаг 1. Welch PSD

```python
import numpy as np
from scipy.signal import welch

def bandpower(data, sfreq, fmin, fmax):
    freqs, psd = welch(data, fs=sfreq, nperseg=int(2 * sfreq))
    idx = (freqs >= fmin) & (freqs <= fmax)
    # односторонний спектр: df * sum(PSD)
    return np.trapz(psd[idx], freqs[idx])

sfreq = 250
# data: np.ndarray shape (2500,) — 10 s @ 250 Hz
# data = ...

theta = bandpower(data, sfreq, 4, 8)
alpha = bandpower(data, sfreq, 8, 13)
beta  = bandpower(data, sfreq, 13, 30)
total = bandpower(data, sfreq, 1, 40)

print(f"θ={theta:.2e}, α={alpha:.2e}, β={beta:.2e} µV²/Hz integrated")
print(f"Relative α = {alpha/total:.1%}")
```

## Шаг 2. Интерпретация α-blocking

| Состояние | α(O1/O2) | Механизм |
| --- | --- | --- |
| Глаза закрыты | ↑ (15→40%) | Таламо-кортикальные осцилляторы **синхронизированы** |
| Глаза открыты, внимание | ↓ (α-blocking) | Дезсинхронизация затылочной коры |

## Шаг 3. Связь с BCI

Band power — **стандартная фича** для SSVEP и neurofeedback. Nimbus ожидает **предобработанные** признаки, не raw EEG.

**Вывод:** FFT/Welch переводит временной ряд в **энергию по полосам** — первый шаг feature extraction.""",
    },
    {
        "id": "ART",
        "title": "Детектор артефактов",
        "level": 2,
        "tag": "Обработка сигналов",
        "color": "#7c4dff",
        "emoji": "👁",
        "difficulty": "★★☆ Средний",
        "description": """## Условие

Сырой EEG содержит **EOG** (моргания), **EMG** (жевание) и **bad channels** (отвалившийся электрод). Нужен **автоматический детектор** для epoch rejection.

**Правила:**
| Артефакт | Критерий | Полоса |
| --- | --- | --- |
| EOG | Peak-to-peak на Fp1/Fp2 > 150 µV | — |
| EMG | Bandpower > 30 Гц, z-score > 3 | 30–80 Гц |
| Bad channel | Variance < 0.01 µV² или flat line | — |

**Задачи:**
1. Реализуйте `detect_artifacts(epoch, sfreq) -> dict`.
2. Почему **ICA до** маркировки bad channels опасна?
3. Сколько эпох отбросится, если 3 из 22 каналов — bad?""",
        "solution": """## Шаг 1. Детектор

```python
import numpy as np

def detect_artifacts(epoch, sfreq, eog_ch=("Fp1", "Fp2"), ch_names=None):
    # epoch: (n_channels, n_samples)
    flags = {"eog": False, "emg": False, "bad_ch": []}
    # EOG: peak-to-peak on frontal channels
    if ch_names:
        for ch in eog_ch:
            if ch in ch_names:
                idx = ch_names.index(ch)
                ptp = epoch[idx].ptp()
                if ptp > 150e-6:  # 150 µV
                    flags["eog"] = True

    # EMG: high-gamma bandpower z-score (simplified)
    from scipy.signal import welch
    freqs, psd = welch(epoch.mean(axis=0), fs=sfreq, nperseg=256)
    emg_power = psd[(freqs >= 30) & (freqs <= 80)].sum()
    if emg_power > 3.0:  # threshold after z-scoring on train
        flags["emg"] = True

    # Bad channels
    for i in range(epoch.shape[0]):
        if epoch[i].var() < 0.01e-12:
            flags["bad_ch"].append(i)

    flags["reject"] = flags["eog"] or flags["emg"] or len(flags["bad_ch"]) > 0
    return flags
```

## Шаг 2. ICA и bad channels

Bad channel с **нулевой** дисперсией создаёт **singular covariance** → ICA ломается или «размазывает» артефакт на все компоненты. **Порядок:** mark bad → interpolate/exclude → ICA.

## Шаг 3. Rejection rate

Bad channels **не всегда** = reject epoch. Если bad channel **исключён** из average reference, эпоха может быть валидной. Но если bad channel участвует в spatial filter (CSP) — **вся эпоха отравлена**.

**Вывод:** Artifact gate — **физический фильтр** до ML; без него декодер учится на шуме.""",
    },
    {
        "id": "ERD",
        "title": "ERD/ERS при motor imagery",
        "level": 3,
        "tag": "Ритмы и паттерны",
        "color": "#00e676",
        "emoji": "🌀",
        "difficulty": "★★☆ Средний",
        "description": """## Условие

Субъект **воображает сжатие правой кисти** (MI). Запись: C3, C4, `sfreq=250` Гц, эпоха 0–4 с после cue.

**Определения:**
- **ERD** (desynchronization): **снижение** mu/beta (8–30 Гц) над **контралатеральной** моторной корой (C4 для правой руки)
- **ERS** (synchronization): **рост** mu/beta над **ипсилатеральной** корой (C3)

**Задачи:**
1. Вычислите ERD% = $(P_{baseline} - P_{task}) / P_{baseline} \\times 100$ в 8–30 Гц.
2. Постройте time-frequency (или bandpower по окнам).
3. Почему **реальное** сокращение мышцы даёт **другой** спектр, чем чистый MI?""",
        "solution": """## Шаг 1. ERD%

```python
import numpy as np
from scipy.signal import welch

def erd_percent(data, sfreq, t_base=(-0.5, 0), t_task=(1.0, 3.0)):
    def power_window(t0, t1):
        i0, i1 = int(t0*sfreq), int(t1*sfreq)
        seg = data[i0:i1]
        f, psd = welch(seg, fs=sfreq, nperseg=256)
        band = (f >= 8) & (f <= 30)
        return psd[band].sum()
    p_base = power_window(*t_base)
    p_task = power_window(*t_task)
    return 100 * (p_base - p_task) / p_base

# C4 for right-hand MI — expect ERD > 10%
# erd_c4 = erd_percent(epoch_c4, 250)
```

## Шаг 2. Биологическая интерпретация

```
Планирование движения (MI)
  → снижение синхронности mu/beta над contralateral M1
  → ERD на C4 (правая рука)

Реальное EMG-сокращение
  → широкополосный EMG > 30 Гц
  → co-contraction → «размазанный» mu, не чистый ERD
```

## Шаг 3. BCI-применение

MI-BCI (BNCI 2014-001) использует **8–30 Гц + CSP + log-variance**. ERD — **биологический маркер**, который CSP усиливает пространственно.

| Канал | Правая рука MI | Ожидание |
| --- | --- | --- |
| C4 | Contralateral | ERD ↓ power |
| C3 | Ipsilateral | ERS ↑ power (часто слабее) |

**Вывод:** ERD — **снижение синхронности**, не «больше электричества». Чистый MI без EMG критичен для декодера.""",
    },
    {
        "id": "P300",
        "title": "Детекция P300 (ERP)",
        "level": 3,
        "tag": "Ритмы и паттерны",
        "color": "#00e676",
        "emoji": "🎯",
        "difficulty": "★★☆ Средний",
        "description": """## Условие

**Oddball paradigm:** редкий target (15%) vs frequent standard (85%). Нужно извлечь **P300** — положительный пик **300–500 мс** после стимула на **Pz/Cz**.

**Параметры:**
- Фильтр: 0.5–10 Гц (Butterworth)
- Эпоха: -0.2 … +0.8 с
- Baseline: -0.2 … 0 с

**Задачи:**
1. Усредните ERP по target vs standard trials.
2. Найдите latency и amplitude P300 (максимум в окне 300–500 мс).
3. Почему для P300 нужен **mastoid reference**, а не average ref?""",
        "solution": """## Шаг 1. ERP extraction

```python
import numpy as np
import mne

# epochs: mne.Epochs, event_id={"target": 1, "standard": 2}
epochs.filter(0.5, 10., fir_design="firwin")
evoked_target = epochs["target"].average()
evoked_std = epochs["standard"].average()
diff = mne.combine_evoked([evoked_target, evoked_std], weights=[1, -1])

# P300 window
times = diff.times
data_pz = diff.copy().pick("Pz").data[0]
win = (times >= 0.3) & (times <= 0.5)
p300_amp = data_pz[win].max()
p300_lat = times[win][np.argmax(data_pz[win])]
print(f"P300: {p300_amp*1e6:.1f} µV @ {p300_lat*1000:.0f} ms")
```

## Шаг 2. Reference

| Reference | P300 | Почему |
| --- | --- | --- |
| Mastoid (M1/M2) | Стабильный baseline | Якорь на кости, мало корковой активности |
| Average ref | Смещает все каналы | P300 «размазывается» по montage |

## Шаг 3. Nimbus pipeline

P300 speller → **NimbusQDA** на ERP-амplitude 300–500 мс, 0.5–10 Гц, class-specific covariance.

**Вывод:** P300 — **когнитивный ERP**, не ритм. Полоса 0.5–10 Гц сохраняет медленную волну.""",
    },
    {
        "id": "CSP",
        "title": "Common Spatial Patterns (CSP)",
        "level": 4,
        "tag": "Машинное обучение",
        "color": "#ffd740",
        "emoji": "🧩",
        "difficulty": "★★★ Продвинутый",
        "description": """## Условие

Датасет **BNCI 2014-001**, 2 класса MI (левая/правая рука). Нужно извлечь **CSP** признаки в полосе 8–30 Гц.

**Задачи:**
1. Fit CSP **только на train fold** (6 компонент → 12 log-variance features).
2. Объясните: $\\mathbf{w}^T \\Sigma_1 \\mathbf{w}$ vs $\\mathbf{w}^T \\Sigma_2 \\mathbf{w}$.
3. Почему CSP fit на **всех данных** — data leakage?

### Формула

CSP находит фильтры $\\mathbf{W}$, максимизирующие дисперсию для одного класса и минимизирующие для другого.""",
        "solution": """## Шаг 1. Pipeline (MNE + scikit-learn)

```python
import numpy as np
from mne.decoding import CSP
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

n_components = 6
csp = CSP(n_components=n_components, reg=None, log=True, norm_trace=False)
clf = LinearDiscriminantAnalysis()
pipe = Pipeline([("csp", csp), ("lda", clf)])

# X: (n_trials, n_channels, n_times), y: labels
# Fit ONLY on X_train, y_train
pipe.fit(X_train, y_train)
score = pipe.score(X_test, y_test)
print(f"Accuracy: {score:.1%}")

# Spatial patterns
patterns = csp.patterns_  # (n_components, n_channels)
```

## Шаг 2. Математика

Обобщённая задача собственных значений:
$$\\Sigma_1 \\mathbf{w} = \\lambda \\Sigma_2 \\mathbf{w}$$

Фильтры с $\\lambda$ близким к 0 → **высокая** дисперсия class 1, **низкая** class 2.

## Шаг 3. Data leakage

```
❌ [CSP fit ALL] → [CV split] → accuracy завышена
✅ [CV split] → [CSP fit train fold only] → [test fold]
```

CSP «видит» test trials → spatial filter **подгоняется** под тест.

**Вывод:** CSP — **supervised spatial filter** для MI; log-variance — стандартная фича для NimbusLDA.""",
    },
    {
        "id": "XDAWN",
        "title": "xDAWN spatial filtering",
        "level": 4,
        "tag": "Машинное обучение",
        "color": "#ffd740",
        "emoji": "✨",
        "difficulty": "★★★ Продвинутый",
        "description": """## Условие

Для **P300 speller** (ERP) CSP не оптимален — нужен **xDAWN**: фильтр, максимизирующий **SNR ERP** относительно фона.

**Задачи:**
1. Примените `Xdawn` (MNE) с `n_filters=4` на train data.
2. Сравните topomap xDAWN vs raw ERP.
3. Когда xDAWN лучше CSP? Когда хуже?

### Контекст

xDAWN — **supervised** метод для **evoked responses** (P300, N170), CSP — для **oscillations** (MI, ERD).""",
        "solution": """## Шаг 1. xDAWN в MNE

```python
from mne.preprocessing import Xdawn
from mne import Epochs

# epochs: target vs non-target, already filtered 0.5-10 Hz
xdawn = Xdawn(n_filters=4, signal_cov=None, correct_overlap="auto")
xdawn.fit(epochs)

# Transform
epochs_xd = xdawn.apply(epochs)
evoked = epochs_xd["target"].average()

# Filters enhance target ERP at ~300 ms
filters = xdawn.filters_  # (n_filters, n_channels)
```

## Шаг 2. xDAWN vs CSP

| Метод | Парадигма | Оптимизирует |
| --- | --- | --- |
| xDAWN | ERP (P300) | SNR evoked response |
| CSP | MI (ERD) | Ratio of band variances |

## Шаг 3. Pipeline

```
[filter 0.5-10 Hz] → [xDAWN fit train] → [epochs transform]
  → [mean amplitude 300-500 ms] → [NimbusQDA]
```

xDAWN **хуже** для MI, потому что ERD — **oscillatory desync**, не time-locked peak.

**Вывод:** xDAWN — spatial filter **для ERP**; обязателен fit только на train.""",
    },
    {
        "id": "BAYES",
        "title": "Байесовский BCI (NimbusLDA/QDA)",
        "level": 5,
        "tag": "Байесовский вывод",
        "color": "#69f0ae",
        "emoji": "📐",
        "difficulty": "★★★ Продвинутый",
        "description": """## Условие

После CSP+log-variance (12 features) нужен **классификатор с posterior** для MI-BCI.

**Модели Nimbus:**
| Модель | Ковариация | Когда |
| --- | --- | --- |
| NimbusLDA | Shared | MI, well-separated |
| NimbusQDA | Class-specific | P300, overlapping |

**Задачи:**
1. Обучите NimbusLDA, получите `predict_proba`.
2. Реализуйте **abstention**: если max posterior < 0.6 → «не уверен».
3. Почему posterior лучше argmax для **real-time feedback**?""",
        "solution": """## Шаг 1. Nimbus inference

```python
from nimbus_bci import NimbusLDA
import numpy as np

# X_train: (n_trials, n_features), y_train: labels
model = NimbusLDA()
model.fit(X_train, y_train)

proba = model.predict_proba(X_test)  # (n_trials, n_classes)
pred = proba.argmax(axis=1)
confidence = proba.max(axis=1)

# Abstention
threshold = 0.6
uncertain = confidence < threshold
print(f"Abstained: {uncertain.mean():.1%} trials")
```

## Шаг 2. Posterior vs argmax

| Подход | Feedback | Риск |
| --- | --- | --- |
| argmax | Всегда команда | Ложные срабатывания при 51% |
| posterior + threshold | Команда только при уверенности | Меньше ошибок, больше «no decision» |

## Шаг 3. Model selection

- **MI (4-class, CSP):** NimbusLDA — быстрее, меньше параметров
- **P300 (overlapping ERP):** NimbusQDA — class-specific covariance
- **Long session drift:** NimbusSTS — adaptive state-space

**Вывод:** Bayesian BCI = **posterior + uncertainty**; abstention — production guardrail.""",
    },
    {
        "id": "PIPE1",
        "title": "P300 speller pipeline",
        "level": 6,
        "tag": "Пайплайны Nimbus",
        "color": "#448aff",
        "emoji": "⌨",
        "difficulty": "★★★ Продвинутый",
        "description": """## Условие

Соберите **полный pipeline** P300 row-column speller (6×6, 36 символов).

**Цепочка Nimbus Studio:**
```
[load] → [filter 0.5-10] → [epochs -0.2..0.8]
  → [xDAWN] → [ERP 300-500ms] → [NimbusQDA] → [spell]
```

**Задачи:**
1. Опишите **flash sequence** и как накапливаются scores по rows/columns.
2. Рассчитайте **ITR** (bits/min) при accuracy 90%, 2.5 s/trial.
3. Какие 3 узла **нельзя** менять местами?""",
        "solution": """## Шаг 1. Speller logic

```python
import numpy as np

def update_scores(scores, flash_idx, is_row, posterior_target):
    # scores: 6 rows + 6 cols = 12 scores
    if is_row:
        scores[flash_idx] += posterior_target
    else:
        scores[6 + flash_idx] += posterior_target
    return scores

def decode_char(row_scores, col_scores):
    r = np.argmax(row_scores)
    c = np.argmax(col_scores)
    return r, c  # index into 6x6 grid
```

## Шаг 2. ITR

$$ITR = \\left[ \\log_2 N + P \\log_2 P + (1-P) \\log_2 \\frac{1-P}{N-1} \\right] \\cdot \\frac{60}{T}$$

При $N=36$, $P=0.9$, $T=2.5$ s:
$$ITR \\approx 40.5 \\text{ bits/min}$$

## Шаг 3. Порядок узлов

| ❌ Нельзя | Почему |
| --- | --- |
| xDAWN до filter | ERP smeared by broadband noise |
| QDA до feature extraction | Raw EEG не в feature space |
| Normalization fit on test | Scale leakage |

**Правильный порядок:**
```
filter → epoch → xDAWN (train) → ERP feature → z-score (train params) → QDA
```

**Вывод:** P300 speller = **ERP pipeline + Bayesian decoder + row/col accumulation**.""",
    },
    {
        "id": "PIPE2",
        "title": "Adaptive MI pipeline",
        "level": 6,
        "tag": "Пайплайны Nimbus",
        "color": "#448aff",
        "emoji": "🔄",
        "difficulty": "★★★ Продвинутый",
        "description": """## Условие

MI-BCI сессия **45 минут**. Accuracy падает с 78% до 62% — **neural drift**.

**Pipeline:**
```
[CSP train calib] → [NimbusLDA] → [online feedback]
  → [drift monitor] → [partial_fit / NimbusSTS]
```

**Задачи:**
1. Когда переключаться на **NimbusSTS**?
2. Реализуйте **rolling calibration**: partial_fit каждые 20 trials.
3. Почему **пересчёт CSP online** опасен?""",
        "solution": """## Шаг 1. Drift detection

```python
from collections import deque
import numpy as np

window = deque(maxlen=20)
baseline_acc = 0.78

def check_drift(recent_correct):
    window.append(recent_correct)
    if len(window) == 20:
        acc = np.mean(window)
        if acc < baseline_acc - 0.10:
            return "DRIFT_DETECTED"
    return "OK"
```

## Шаг 2. Adaptive strategies

| Стратегия | Что адаптируется | Риск |
| --- | --- | --- |
| `partial_fit` (LDA) | Decision boundary | Med |
| NimbusSTS | Latent state + decoder | Low (designed for drift) |
| Re-fit CSP online | Spatial filters | **High** — unstable, non-causal |

## Шаг 3. NimbusSTS switch

Переключайтесь когда:
- Session > 30 min
- Confidence trend ↓ over 10+ trials
- Accuracy drop > 10% from calibration

```python
from nimbus_bci import NimbusSTS

sts = NimbusSTS()
sts.fit(X_calib, y_calib)

for chunk in stream:
    pred, proba, state = sts.predict_with_state(chunk)
    if proba.max() < 0.5:
        trigger_recalibration()
```

**Вывод:** Адаптируйте **decision boundary** (LDA/STS), не **spatial filter** (CSP) mid-session.""",
    },
    {
        "id": "SSVEP",
        "title": "SSVEP + Canonical Correlation Analysis",
        "level": 7,
        "tag": "Нелинейные методы",
        "color": "#ff4081",
        "emoji": "👀",
        "difficulty": "★★★★ Эксперт",
        "description": """## Условие

SSVEP: 3 мигания **15, 17, 19 Гц**. Субъект смотрит на 17 Гц.

**Задачи:**
1. Реализуйте **CCA** между EEG и reference signals $[\\sin(2\\pi f t), \\cos(2\\pi f t)]$.
2. Добавьте **2-ю гармонику** (2f) — почему она важна?
3. Сравните CCA vs bandpower @ target frequency.

### Биология

SSVEP — **резонанс** зрительной коры (V1/V2) на частоту мерцания, не просто «пик в FFT».""",
        "solution": """## Шаг 1. CCA (scikit-learn)

```python
import numpy as np
from sklearn.cross_decomposition import CCA

freqs = [15, 17, 19]
sfreq = 250
duration = 2.0
t = np.arange(0, duration, 1/sfreq)

def ref_signals(f, t):
    refs = []
    for h in [1, 2]:  # fundamental + 2nd harmonic
        refs.append(np.sin(2 * np.pi * h * f * t))
        refs.append(np.cos(2 * np.pi * h * f * t))
    return np.column_stack(refs)

# X: (n_samples, n_channels) — one SSVEP epoch
scores = {}
for f in freqs:
    Y = ref_signals(f, t)
    cca = CCA(n_components=1)
    cca.fit(X, Y)
    X_c, Y_c = cca.transform(X, Y)
    scores[f] = np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1]

pred_freq = max(scores, key=scores.get)
print(f"Detected: {pred_freq} Hz (scores: {scores})")
```

## Шаг 2. Гармоники

V1 генерирует **nonlinear response** → энергия на 2f, 3f. CCA с 2f ↑ SNR для низких частот (< 20 Гц).

## Шаг 3. CCA vs bandpower

| Метод | Плюс | Мinus |
| --- | --- | --- |
| Bandpower @ f | Простой | Чувствителен к шуму, нет phase |
| CCA | Phase-aware, multichannel | Медленнее, нужен чистый ref |

Nimbus: **NimbusLDA/QDA** на CCA features или bandpower (f, 2f, 3f).

**Вывод:** SSVEP = **phase-locked resonance**; CCA — стандартный нелинейный детектор.""",
    },
    {
        "id": "EEGNET",
        "title": "EEGNet (PyTorch)",
        "level": 8,
        "tag": "Нейронные сети",
        "color": "#e040fb",
        "emoji": "🧠",
        "difficulty": "★★★★ Эксперт",
        "description": """## Условие

Обучите **EEGNet** для 4-class MI (BNCI 2014-001).

**Архитектура (упрощённо):**
- Temporal conv → Depthwise spatial conv → Separable conv → Dense

**Задачи:**
1. Подготовьте данные: `(n_trials, 1, n_channels, n_times)`, bandpass 4–38 Гц.
2. Train/val/test split **по sessions**, не по trials.
3. Почему split by trials — **leakage**? Как EEGNet сравнить честно с CSP+LDA?""",
        "solution": """## Шаг 1. Data prep

```python
import torch
import torch.nn as nn
from braindecode.models import EEGNetv4

# X: (n_trials, n_channels, n_times) after bandpass 4-38 Hz
X = X[:, np.newaxis, :, :]  # add channel dim for EEGNet
X_tensor = torch.FloatTensor(X)
y_tensor = torch.LongTensor(y)

model = EEGNetv4(n_chans=22, n_outputs=4, n_times=1000, final_conv_length="auto")
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()
```

## Шаг 2. Training loop (sketch)

```python
for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    out = model(X_train)
    loss = criterion(out, y_train)
    loss.backward()
    optimizer.step()

model.eval()
with torch.no_grad():
    acc = (model(X_test).argmax(1) == y_test).float().mean()
```

## Шаг 3. Fair comparison

| Split | Leakage? |
| --- | --- |
| Random trials | ✓ same session → correlated |
| By session/subject | ✗ честная generalization |

Сравнение с CSP+LDA:
- **Same splits**, same bandpass
- Report **mean ± std** over subjects (LOSO)
- EEGNet может ↑ accuracy, но ↓ interpretability

**Вывод:** EEGNet — end-to-end; честная оценка требует **session-level CV**.""",
    },
    {
        "id": "RT",
        "title": "Real-time OpenBCI streaming",
        "level": 9,
        "tag": "Real-Time системы",
        "color": "#ff6e40",
        "emoji": "📡",
        "difficulty": "★★★★ Эксперт",
        "description": """## Условие

Разверните **online MI-BCI** с OpenBCI Cyton (8 каналов, 250 Hz).

**Требования:**
- Latency end-to-end < 100 ms
- Causal filter (filtfilt **запрещён**)
- Chunk-based inference (250 samples = 1 s)

**Задачи:**
1. Подключите LSL stream → ring buffer → causal bandpass.
2. Примените **pre-trained** CSP+LDA/NimbusLDA на каждый chunk.
3. Что делать при `confidence < 0.5` три chunks подряд?

### Hardware

OpenBCI → USB/serial → Python (`brainflow` или `pylsl`).""",
        "solution": """## Шаг 1. Causal streaming

```python
import numpy as np
from scipy.signal import lfilter, butter
from collections import deque

sfreq = 250
chunk_size = 250  # 1 second
buffer = deque(maxlen=4 * sfreq)  # 4 s history for CSP epoch

b, a = butter(4, [8, 30], btype="bandpass", fs=sfreq)

# Pre-trained from offline calibration
# csp_filters, lda_model loaded from disk

zi = np.zeros(max(len(a), len(b)) - 1)

def process_chunk(raw_chunk):
    global zi
    filtered, zi = lfilter(b, a, raw_chunk, zi=zi)
    buffer.extend(filtered)
    if len(buffer) >= 2 * sfreq:
        epoch = np.array(buffer)[-2*sfreq:]  # last 2 s
        features = extract_csp_logvar(epoch, csp_filters)
        proba = lda_model.predict_proba(features.reshape(1, -1))[0]
        return proba.argmax(), proba.max()
    return None, 0.0
```

## Шаг 2. Latency budget

| Stage | ms |
| --- | --- |
| Acquisition buffer | 1000 (1 s epoch) |
| Filter + CSP | 5–15 |
| NimbusLDA | 10–25 |
| **Total** | ~1020–1040 ms |

→ Для < 100 ms нужен **shorter epoch** или **overlap-add** с trade-off SNR.

## Шаг 3. Fallback policy

```python
low_conf_streak = 0

def on_prediction(pred, conf):
    global low_conf_streak
    if conf < 0.5:
        low_conf_streak += 1
        if low_conf_streak >= 3:
            send_feedback("RECALIBRATE")
            pause_feedback()
    else:
        low_conf_streak = 0
        send_feedback(pred)
```

**Вывод:** Real-time = **causal processing + pre-trained model + confidence gating + drift monitoring**.""",
    },
]
