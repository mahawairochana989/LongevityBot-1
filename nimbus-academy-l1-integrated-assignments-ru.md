# Nimbus Academy · Level 1 — Интегрированные задания

> **Редактируемый рабочий документ.** Формат Markdown — открывается в любом редакторе (VS Code, Obsidian, Typora, веб-интерфейс GitHub). Заголовки, таблицы, блоки кода и формулы сохраняются при правках.
>
> **Источник:** канонический набор интегрированных заданий Level 1 · EEG Analyst Pipeline (TOC v1.0, порядок BBS-first).
>
> **Правила оформления (единые для всех заданий):**
> - Вся нейрофизиология и все формулы, нужные для решения, **встроены в условие** — внешние ссылки не требуются.
> - Каждое задание на пайплайн: **❌ наивный** → разбор ошибок → **✅ правильный** → таблица сравнения → **строка журнала** (*биологический факт → инженерное решение*).
> - Графы Nimbus Studio: цепочки узлов `[узел_a] → [узел_b] → …`.
> - Датасет по умолчанию: **MOABB BNCI 2014-001 (S01, `0train`)** — 22 EEG + 3 EOG, `sfreq = 250 Гц`, 288 эпох motor imagery.

---

## Содержание

1. [Задание 1.1 — Studio graph intake (intake-узел)](#задание-11--studio-graph-intake-intake-узел)
2. [Задание 1.2 — Referencing + filtering](#задание-12--referencing--filtering)
3. [Задание 1.3 — Artifact annotation (EOG / EMG / ECG / bad channels)](#задание-13--artifact-annotation-eog--emg--ecg--bad-channels)
4. [Задание 1.4 — Baseline и нестационарность (эпохи + session metadata)](#задание-14--baseline-и-нестационарность-эпохи--session-metadata)
5. [Задание 1.5 — ICA cleaning (независимые компоненты)](#задание-15--ica-cleaning-независимые-компоненты)
6. [Задание 1.6 — Quality dashboard (SNR, α-пик, rejection rate)](#задание-16--quality-dashboard-snr-α-пик-rejection-rate)
7. [Задание 1.7 — Публичные датасеты + Nimbus feature contract (репликация)](#задание-17--публичные-датасеты--nimbus-feature-contract-репликация)
8. [Задание 1.CAP — Capstone: полный Analyst Pipeline (интеграция 1.1–1.7)](#задание-1cap--capstone-полный-analyst-pipeline-интеграция-1117)

---

# Интегрированные задания Level 1

# Задание 1.1 — Studio graph intake (intake-узел)

**Коды:** BBs-1.1 + L1-P1

## Сценарий

Файл **BNCI 2014-001 (S01, `0train`)** загрузился в MNE без ошибок: **22 EEG-канала + 3 EOG**, `sfreq = 250 Гц`, **288 эпох motor imagery**. Технический коллега говорит: *«Файл валидный, грузи в L2, не теряй время»*. Ваша работа — проверить, действительно ли «грузить можно», и собрать **intake-узел в Nimbus Studio**, который зафиксирует **физическую схему измерения** до того, как данные попадут в любые фильтры.

## Что сдать

- **Intake-subgraph** в Nimbus Studio (PNG + JSON-конфиги узлов).
- Единый выходной объект **`RawIntake`** (проверенные данные + metadata).
- Файл **`risk_log.md`** — минимум **3 записи** в формате *наблюдение → severity → план*.
- **Одна строка** в нейронаучный журнал: цепочка *«биологический факт → инженерное решение»*.

## 📖 Нейрофизиология, нужная именно для этой задачи

### Откуда берётся сигнал на скальпе

Видимый на электроде потенциал создают **только пирамидные нейроны слоёв III и V** коры. Их **апикальный дендрит** длиной 1–2 мм выстроен перпендикулярно поверхности коры — при активации синапсов на дистальной части возникает **электрический диполь**.

- Один нейрон: дипольный момент ≈ **10⁻¹² A·м** — на скальпе невидим.
- Видимым становится ансамбль **~10⁸ синхронных нейронов на ~1 см²** коры → **10–100 µV** на электроде.

→ **Вывод.** Амплитуда EEG — мера **согласованности популяции**, а не «силы мысли».

### EEG — разность потенциалов, не абсолютная активность

Любая запись с электрода — **разность потенциалов** между ним и референсом. Без выбора референса понятие «активность канала Cz» **физически не определено**.

→ **Вывод.** Reference и montage — не «настройка софта», а **часть физической схемы измерения**.

### Open vs closed field

В **неокортексе** (параллельные пирамиды) диполи **суммируются** → open field, видим на скальпе.  
В **гиппокампе** и глубоких ядрах геометрия **гасит** поле → closed field, почти невидим.

→ **Вывод.** Topomap «из глубины» на сыром EEG — почти всегда **проекция коркового или экстракраниального источника**.

### Типы каналов — это биология, не метки

| Тип | Что измеряет |
|---|---|
| **EEG** | Локальная популяция коры (после вычитания референса) |
| **EOG** | **Корneo-retinal dipole** глаза — на порядки выше коры, доминирует на фронте |
| **EMG** | **Моторные единицы** мышц — широкополосный сигнал, доминирует > 30 Гц |
| **ECG** | **Сердечный диполь**, проводимость через голову |

→ **Вывод.** EOG, помеченный как EEG, заставляет пайплайн трактовать **сигнал глаза как кору** — все последующие стадии теряют физический смысл.

## 🧮 Формулы для этой задачи

### Критерий Найквиста

$$ f_N = \frac{f_s}{2} $$

Рабочая полоса Level 1: **0.5–45 Гц** → минимум $f_s > 90$ Гц.  
При $f_s = 250$ Гц: $f_N = 125$ Гц > 45 Гц ✓.

### Разность потенциалов

$$ V_{\text{scalp}} = \varphi_A - \varphi_B $$

Смена референса меняет **все** каналы — это не «постобработка».

### Шкала severity в `risk_log.md`

| Severity | Смысл |
|---|---|
| **L** | Задокументированная особенность, не ломает контракт |
| **M** | Собьёт одну downstream-стадию, если проигнорировать |
| **H** | Ломает физическую интерпретируемость сигнала |

## Развёртка решения

### Шаг 1. Логическая гипотеза

«Файл валиден, потому что загрузился» — **недостаточно**. Нужно зафиксировать:
1. EOG не смешаны с EEG.
2. Montage установлен → topomap геометрически определён.
3. Nyquist задокументирован для целевой полосы.
4. События приведены к типизированной схеме `event_id`.

Intake **не улучшает SNR** — он **сохраняет измеряемую величину**.

### Шаг 2. Точка, где нужен расчёт

Единственная количественная проверка на intake — **Nyquist для целевой полосы**. Остальное — структурные проверки (типы, montage, события, metadata).

### Шаг 3. Расчёт

Целевая полоса: **0.5–45 Гц**.  
`sfreq = 250 Гц`:

$$ f_N = 250 / 2 = 125 \text{ Гц} $$

$$ \text{margin} = f_N / f_{\text{high}} = 125 / 45 \approx 2{,}78 $$

→ Записать: `nyquist_ok = true`, `nyquist_margin = 2.78`.

### Шаг 4. ❌ Наивный пайплайн с ошибками

```
[load_edf] → [bandpass 1-40] → [ICA] → [features]
```

| Узел / шаг | Ошибка | Физический смысл потери |
|---|---|---|
| `load_edf` | Только путь к файлу | Невоспроизводимый эксперимент |
| *(пропущен)* `channel_inventory` | EOG = EEG | Смешение поля глаза и коры |
| *(пропущен)* `montage_setter` | Координаты NULL | Topomap бессмысленен |
| *(пропущен)* `sfreq_validator` | Nyquist не проверен | Репликация на другом sfreq «тихо» сломается |
| *(пропущен)* `events_loader` | Нет схемы `event_id` | Эпохирование может перепутать классы |
| *(пропущен)* `intake_report` | Нет контракта | Нечего сравнивать в L2+ |
| `bandpass` до intake | Фильтр до проверки схемы | Ошибка схемы неотличима от «биологии» |
| `ICA` на смешанных типах | — | Компоненты физиологически неинтерпретируемы |

### Шаг 5. ✅ Правильный пайплайн (Studio graph + JSON config)

```
[data_source]
  → [channel_inventory]
  → [montage_setter]
  → [sfreq_validator]
  → [events_loader]
  → [intake_report]
```

**Контракты портов:**

```
data_source         → RawArray(n_channels, n_samples)
channel_inventory   → Dict["eeg", "eog", "emg", "ecg", "misc", "stim": List[str]]
montage_setter      → DigMontage (aligned to inventory.eeg)
sfreq_validator     → Dict { sfreq, nyquist, target_band, ok, margin }
events_loader       → ndarray(n_events, 3), event_id: Dict[str, int]
intake_report       → IntakeReport { html, json, risks }
```

**JSON-конфиг (фрагмент):**

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
    "on_missing": "raise"
  },
  "sfreq_validator": {
    "expected_sfreq": 250.0,
    "target_band": [0.5, 45.0],
    "min_margin": 2.0
  },
  "events_loader": {
    "event_id": { "left_hand": 1, "right_hand": 2, "feet": 3, "tongue": 4 }
  }
}
```

**Минимум 3 записи в `risk_log.md`:**

| Наблюдение | Severity | План |
|---|---|---|
| 3 EOG-канала не типизированы в исходном файле | **H** | `channel_inventory.overrides`; assert `len(eog)=3` |
| Montage не сохранён в источнике | **M** | Принудительно `standard_1020`; при несовпадении имён — raise |
| `sfreq` прочитан, но не assert'нут | **M** | `expected_sfreq == 250.0`; при дрейфе — fail loudly |

### Шаг 6. Прямое сравнение

| Аспект | ❌ Наивный | ✅ Правильный |
|---|---|---|
| Типизация каналов | EOG = EEG | 22 EEG / 3 EOG |
| Montage | Нет | `standard_1020` |
| Nyquist | Не проверен | margin ≈ 2.78 задокументирован |
| События | Annotations | Типизированный `event_id` |
| Воспроизводимость | Путь к файлу | dataset + subject + session в JSON |
| Выход | `Raw` | `RawIntake` + IntakeReport + risk_log |

### Шаг 7. Строка в журнал

> *«Референс и тип канала — часть физической схемы измерения; intake обязан сериализовать inventory, montage, margin Nyquist и события **до** любого фильтра.»*

---

# Задание 1.2 — Referencing + filtering

**Коды:** BBs-1.2 + L1-P2

## Сценарий

На входе — объект `RawIntake` из задания 1.1. Коллега просит *«один bandpass 1–40 Гц — универсальный, и P300, и MI»*. Вы должны показать в Nimbus Studio, что **выбор референса и полосы — адрес биологического генератора**, а не дефолт из туториала.

## Что сдать

- Sub-graph reference + filter (PNG + JSON).
- Артефакт **`preprocessing_config.json`**.
- **PSD report** (до/после) для окципитальной и центральной групп.
- **Строка журнала:** что сохранено биологически, что отсечено «железом».

## 📖 Нейрофизиология для этой задачи

| Полоса | Диапазон | Генератор |
|---|---|---|
| **δ** | 0.5–4 Гц | Медленные деполяризации; сон, нарушения сознания |
| **θ** | 4–8 Гц | Гиппокампо-фронтальная петля; память, нагрузка |
| **α** | 8–13 Гц | **Таламо-кортикальная петля** (Lopes da Silva); GABA-торможение; pulsed inhibition (Klimesch) |
| **β** | 13–30 Гц | Моторная кора; **ERD** при движении, **ERS** после |
| **γ** | 30–80 Гц | Локальное связывание; сеть PING (pyramidal–interneuron) |

**Референс — гипотеза о «нуле» поля:**
- **Average** — среднее скальпа как ноль (плотное покрытие).
- **Mastoid** — якорь на кости (ERP, P300).
- **Notch 50/60 Гц** — **не биология**, а сетевая помеха.

**Парадигма → полоса:**
- **P300:** 0.5–10 Гц (медленные корковые компоненты).
- **Motor imagery:** 8–30 Гц (mu/beta ERD/ERS).
- **Общий анализ:** 0.5–45 Гц.

## 🧮 Формулы для этой задачи

**Average reference:**

$$ x_i^{\text{ref}}(t) = x_i^{\text{raw}}(t) - \frac{1}{N}\sum_{j=1}^{N} x_j^{\text{raw}}(t) $$

**Изменение α-пика (критерий приёмки):**

$$ \Delta P_\alpha = \frac{P_{\text{after}}(f_\alpha) - P_{\text{before}}(f_\alpha)}{P_{\text{before}}(f_\alpha)} $$

Приёмка: $|\Delta P_\alpha| < 0{,}10$; $|\Delta f_\alpha| < 1$ Гц.

## Развёртка решения

### Шаг 1. Логическая гипотеза

«Универсальный 1–40 Гц» даёт число для любой парадигмы, но **режет P300** и **не добавляет пользы** для MI. Разные парадигмы → разные ветки, общий только intake.

### Шаг 2. Точка расчёта

Проверка $\Delta P_\alpha$ после фильтра; проверка `line_freq` (50 vs 60 Гц).

### Шаг 3. Расчёт

MI, bandpass 8–30 Гц: $f_\alpha = 10{,}2$ Гц, $P_{\text{before}} = 12{,}4$ µV²/Hz, $P_{\text{after}} = 11{,}6$ µV²/Hz.

$$ \Delta P_\alpha = (11{,}6 - 12{,}4) / 12{,}4 = -0{,}065 \quad \checkmark $$

### Шаг 4. ❌ Наивный пайплайн

```
[RawIntake] → [notch 50] → [bandpass 1-40] → [downstream]
```

| Ошибка | Почему |
|---|---|
| notch 50 без проверки страны | В 60 Гц-сети notch 50 режет сигнал, оставляет помеху |
| 1–40 для P300 и MI | Съедает медленный P300; для MI избыточен |
| Нет `psd_comparator` | Не видно, «съел» ли фильтр α-пик |
| Нет `reference_setter` | Неявный референс = неявная гипотеза |

### Шаг 5. ✅ Правильный пайплайн

```
[RawIntake]
  → [reference_setter: average | mastoid]
  → [notch: line_freq]
  → [bandpass: paradigm_specific]
  → [psd_comparator]
  → [preprocessing_config.json]
```

```json
{
  "reference": { "scheme": "average", "rationale": "22 канала, плотное покрытие" },
  "notch": { "line_freq": 50, "rationale": "EU" },
  "bandpass_variants": {
    "p300": { "l_freq": 0.5, "h_freq": 10.0 },
    "motor_imagery": { "l_freq": 8.0, "h_freq": 30.0 },
    "broad": { "l_freq": 0.5, "h_freq": 45.0 }
  },
  "psd_acceptance": { "alpha_power_change_max": 0.10, "alpha_peak_drift_hz_max": 1.0 }
}
```

### Шаг 6. Прямое сравнение

| Аспект | ❌ | ✅ |
|---|---|---|
| Референс | Неявный | Явный + rationale |
| Notch | Hard-coded 50 | Из metadata `line_freq` |
| Полоса | 1–40 «для всего» | Варианты под парадигму |
| Контроль | Нет | PSD comparator |

### Шаг 7. Строка в журнал

> *«Полоса — адрес генератора: 8–30 Гц для MI — это таламо-кортикальный осциллятор ERD/ERS, а не «магическое число».»*

---

# Задание 1.3 — Artifact annotation (EOG / EMG / ECG / bad channels)

**Коды:** BBs-1.3 + L1-P3

## Сценарий

Ревьюер: *«Слишком шумно — почисти перед features»*. Наивная интерпретация — **удалить громкие эпохи**. Но громкость — это **другая физиологическая система** (глаза, мышцы, сердце). Задача — **разметить источники**, а не слепо reject.

## Что сдать

- Sub-graph artifact annotation (PNG + JSON).
- **`artifact_table.csv`**: `t_start`, `t_end`, `source` ∈ {eog, emg, ecg, bad_channel, other}, `method`, `score`.
- Обновлённый **`risk_log.md`**.
- **Строка журнала** — физиологический источник каждого отклонённого epoch.

## 📖 Нейрофизиология для этой задачи

- **ЭМГ:** моторная единица >> коркового PSP; лицо/шея ближе к Fp, чем моторная кора к C3.
- **ЭОГ:** роговица — диполь «батарейки»; моргания на Fp — **сигнал глазодвигательной системы**.
- **ЭКГ:** QRS виден на темени (T7/T8), особенно при mastoid ref.
- **КГР:** медленный дрейф < 0.5 Гц от потовых желез.
- **Bad channel:** высокий импеданс → variance ↑; обрыв → flatness; мост → ρ с соседом → 1.

## 🧮 Формулы для этой задачи

**EOG (корреляция):**

$$ \rho(x_{\text{Fp}}, x_{\text{EOG}}) = \text{corr}(x_{\text{Fp}}, x_{\text{EOG}}) $$

Порог: $|\rho| > 0{,}7$ → событие EOG.

**EMG index:**

$$ \text{EMG\_idx} = \frac{P_{30-80}}{P_{8-13}} $$

Порог: $\text{EMG\_idx} > \kappa$ (типично 3–5).

**Bad channel:**

$$ \text{var}(x_c) > 5 \cdot \text{median}_n[\text{var}(x_n)] $$

**Peak-to-peak (reject epoch):**

$$ \text{PtP}(x) = \max(x) - \min(x) $$

## Развёртка решения

### Шаг 1. Логическая гипотеза

«Чистка» = **разделение систем**, не удаление «шума». Фиксированная таксономия: EOG, EMG, ECG, bad_channel, other.

### Шаг 2. Точка расчёта

ρ(Fp, EOG); EMG_idx по каналам; variance ratio; PtP по эпохам.

### Шаг 3. Расчёт (пример)

Epoch t = 12.4 s, Fp1: ρ(Fp1, EOG1) = 0.84 → **eog**; EMG_idx = 1.7 (< 3) → не EMG.

### Шаг 4. ❌ Наивный пайплайн

```
[bandpassed] → [reject PtP > 100 µV] → [ICA] → [features]
```

| Ошибка | Следствие |
|---|---|
| Один порог на все каналы | Fp и O1 трактуются одинаково |
| Reject без `source` | Потеря информации «почему» |
| EOG-каналы не используются | Богатейший триггер игнорируется |
| Bad channels не помечены | Отравляют CSP, ICA, average ref |

### Шаг 5. ✅ Правильный пайплайн

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

```json
{
  "eog_detector": { "threshold": 0.7, "window_s": 1.0 },
  "emg_detector": { "kappa": 3.0, "high_band": [30, 80], "low_band": [8, 13] },
  "ecg_detector": { "channel": "T8", "threshold": 0.6 },
  "bad_channels": { "variance_ratio_max": 5.0 },
  "epoch_reject": { "ptp_uv": 150.0 }
}
```

### Шаг 6. Прямое сравнение

| | ❌ | ✅ |
|---|---|---|
| Логика | «Громкое = плохое» | «Громкое = другой орган» |
| EOG | Игнор | Канал-триггер |
| Таблица | Нет | artifact_table.csv |

### Шаг 7. Строка в журнал

> *«Каждый отклонённый epoch несёт метку физиологического источника — иначе инженер молча решает, что считать «мозгом».»*

---

# Задание 1.4 — Baseline и нестационарность (эпохи + session metadata)

**Коды:** BBs-1.4 + L1-P2* (baseline extension)

## Сценарий

4 блока MI за ~30 мин; в блоке 4 субъект устал. Коллега: эпохи без baseline, **z-score по всей сессии**, random split → test accuracy «подозрительно высокая», per-block accuracy падает. Покажите, что **нестационарность — биология**, исправьте baseline и защититесь от leakage.

## Что сдать

- Sub-graph baseline + session metadata (PNG + JSON).
- Эпохи с **`baseline = (-0.2, 0.0)`**.
- **`norm_policy.json`** (fit только на train).
- **`leakage_demo.ipynb`** — разница accuracy при leaky vs correct norm.
- **Строка журнала:** межсессионная vs межсубъектная нормализация.

## 📖 Нейрофизиология для этой задачи

- **Нейромодуляторы:** ACh десинхронизирует; NA поднимает β; DA — reward.
- **Habituation:** повтор → меньший ответ (адаптация нейрона, не «плохие данные»).
- **Циркада, усталость:** блок N ≠ блок 1 электрически.
- **Baseline (−0.2, 0)** — единственный честный «ноль» **состояния коры до события** для данного trial.
- **Z-score по всей сессии** = смешение состояний мозга + **утечка** будущего в прошлое.

## 🧮 Формулы для этой задачи

**Baseline correction:**

$$ x^{\text{corr}}(t) = x(t) - \overline{x}_{t \in [-0{,}2,\,0]} $$

**Train-only z-score:**

$$ z(x) = \frac{x - \mu_{\text{train}}}{\sigma_{\text{train}}} $$

**Robust (MAD):**

$$ z_{\text{robust}} = \frac{x - \text{median}_{\text{train}}}{1{,}4826 \cdot \text{MAD}_{\text{train}}} $$

**Fatigue proxy (по блокам):**

$$ R_{\text{block}} = \frac{n_{\text{rejected}}}{n_{\text{total}}} \times 100\,\% $$

## Развёртка решения

### Шаг 1. Логическая гипотеза

Высокий test acc + падение по блокам = **leakage + fatigue**. Два независимых исправления: baseline per epoch; norm только на train, split по времени.

### Шаг 2–3. Расчёт

- Leaky z-score + random split: acc = **0.92**.
- Train-only + time split: acc = **0.78**.
- Gap **0.14** — размер «обмана».
- Rejection по блокам: 6 % → 9 % → 14 % → 22 % (монотонный рост → fatigue в metadata).

### Шаг 4. ❌ Наивный пайплайн

```
[filter] → [epochs baseline=None] → [z_score_full_session] → [random_split] → [features]
```

### Шаг 5. ✅ Правильный пайплайн

```
[artifact_clean]
  → [epoch_creator: baseline=(-0.2,0)]
  → [baseline_corrector]
  → [session_metadata_emitter]
  → [time_aware_split]
  → [norm_policy_emitter train-only]
  → [normalised_features]
```

### Шаг 6. Прямое сравнение

| | ❌ | ✅ |
|---|---|---|
| Baseline | None | (−0.2, 0) pre-stimulus |
| Norm | Вся сессия | Только train, артефакт |
| Split | Random | Time-aware |
| Усталость | Невидима | R_block в metadata |

### Шаг 7. Строка в журнал

> *«Baseline — учёт состояния нервной системы в t₀; межсессионная нормализация принимает drift между сессиями, межсубъектная — биологическую вариабельность; это разные операции.»*

---

# Задание 1.5 — ICA cleaning (независимые компоненты)

**Коды:** BBs-1.5 + L1-P4

## Сценарий

После baseline на фронте — blinks, на темпоральных — пульсация ~1.2 Гц. Коллега: ICA на raw, удалить IC#3 и IC#7 «потому что странные». Докажите опасность, соберите корректный ICA-subgraph, **докажите сохранение α-компоненты**.

## Что сдать

- Sub-graph ICA fit / inspect / label / apply (PNG + JSON).
- **ICA report:** topomap + time course + PSD до/после.
- Сохранённая **unmixing matrix** $W$ + список excluded с labels.
- **Строка журнала:** тело vs корковая сеть.

## 📖 Нейрофизиология для этой задачи

ICA опирается на **статистическую независимость** смешанных источников (кора + тело). Нарушается при тесно связанных процессах (внимание + память).

| Подпись | Topomap | PSD | Метка |
|---|---|---|---|
| Blink | Фронтальный диполь | Низкие частоты | `eog` |
| ECG | Тemporal | 1–2 Гц | `ecg` |
| EMG | Фокальный | 30–80 Гц | `emg` |
| **Кortical α** | Затылок симметрично | 8–13 Гц пик | **`brain` — оставить!** |
| DMN-like | Средняя линия | 1–10 Гц | **`brain` — оставить!** |

**Обязательно:** HP 1 Гц **только для fit ICA**; **rank check** после average ref.

## 🧮 Формулы для этой задачи

$$ X = A \cdot S, \quad S = W \cdot X $$

$$ \text{rank}(X) \le n_{\text{ch}} - 1 \quad \text{(после average ref)} $$

**α-retention:**

$$ \Delta_\alpha = \frac{P_{\text{after}}(f_\alpha) - P_{\text{before}}(f_\alpha)}{P_{\text{before}}(f_\alpha)} $$

Приёмка: $\Delta_\alpha > -0{,}30$ — иначе **откатить** удаление.

**EOG score компоненты k:**

$$ s_k^{\text{eog}} = |\rho(s_k(t), x_{\text{EOG}}(t))| $$

## Развёртка решения

### Шаг 3. Расчёт

Rank = 21 (22 ch, average ref). O1: $P_{\text{before}}(10.2) = 14.7$, $P_{\text{after}} = 13.6$ → $\Delta_\alpha = -0.075$ ✓.

### Шаг 4. ❌ Наивный

```
[raw] → [ICA n=22] → [drop IC 3,7] → [downstream]
```

### Шаг 5. ✅ Правильный

```
[filtered] → [HP 1 Hz for fit] → [rank_estimator]
  → [ICA picard n=rank] → [IC_inspector] → [label_eog_ecg]
  → [apply_exclude] → [psd_alpha_validator] → [save W + labels]
```

### Шаг 6. Сравнение + Шаг 7. Журнал

> *«ICA отделяет статистически независимые источники; метка «артефакт / мозг» — физиологическое решение; α-retention — его количественная страховка.»*

---

# Задание 1.6 — Quality dashboard (SNR, α-пик, rejection rate)

**Коды:** BBs-1.6 + L1-P6

## Сценарий

Ревьюер: *«Quality report — годится ли запись для L2?»* Accuracy — downstream-метрика; нужно знать, **интерпретируем ли сам сигнал**, до обучения декодера.

## Что сдать

- Sub-graph quality dashboard (PNG + JSON).
- **`quality_dashboard.html`**: SNR, PSD, α-пик, variance, finite rate, % rejected, секция **physiological caveats**.
- **`quality_gates.json`**: пороги PASS / WARN / FAIL.
- **Строка журнала:** как состояние субъекта читается в метриках.

## 📖 Нейрофизиология для этой задачи

- Импеданс **5–20 kΩ** — норма; **> 50 kΩ** — SNR падает.
- Кожа — фильтр в цепи измерения.
- Тревога → EMG; усталость → blinks ↑, α drift.
- **α-пик 7.5–13 Гц** на O1/O2/Pz — sanity oracle после корректного preprocessing.
- Падение SNR к блоку 4 — **биология**, не «сломанный CSP».

## 🧮 Формулы для этой задачи

$$ \text{SNR}_c = 10 \log_{10}\left(\frac{P_{\text{signal,c}}}{P_{\text{noise,c}}}\right) \text{ [dB]} $$

$$ f_\alpha = \arg\max_{f \in [7,14]} \overline{\text{PSD}_O}(f) $$

$$ R = \frac{n_{\text{rejected}}}{n_{\text{total}}} \times 100\,\% $$

**Gates:** SNR ≥ 3 dB; $f_\alpha \in [7,14]$; $R \le 40\%$; finite_rate = 1.0.

## Развёртка решения

### Шаг 3. Расчёт (пример)

SNR median 6.2 dB; 2 ch < 3 → WARN. $f_\alpha = 10.3$ → PASS. R = 18 % → PASS; по блокам 6→22 % → caveat fatigue. Verdict: **PASS with WARN**.

### Шаг 4. ❌ Наивный

```
[clean] → [train] → [accuracy] → OK
```

### Шаг 5. ✅ Правильный

```
[clean_epochs] → [per_channel_snr] → [psd] → [alpha_peak_finder]
  → [rejection_per_block] → [region_grouper] → [finite_check]
  → [verdict_writer] → [quality_dashboard.html]
```

### Шаг 7. Журнал

> *«Dashboard — предложение о субъекте и протоколе, а не о декодере: «два канала у висков с низким SNR, α дрейфует к блоку 4».»*

---

# Задание 1.7 — Публичные датасеты + Nimbus feature contract (репликация)

**Коды:** BBs-1.7 + L1-P5 + L1-P7

## Сценарий

Локальный pipeline работает. Лид: *«Тот же код на MOABB — без правок, кроме data source?»* Нужны **feature contract**, **metadata**, **train-only norm**, **cross-dataset comparison**.

## Что сдать

- Sub-graph полного L1 + replication runner (PNG + JSON).
- **`feature_metadata.json`** + **`features.npz`**.
- **`replication_script.py`** — одна команда запуска + README.
- **`cross_dataset_comparison.md`**: subject/session variance, KL-divergence.
- **Строка журнала:** что переносится, что локально.

## 📖 Нейрофизиология для этой задачи

- α-пик — **распределение**, не константа 10 Гц.
- Наследуемость ритмов до ~80 % (twin studies).
- BCI-naive vs trained — разные стратегии MI / ERD.
- Transfer gap = **биология + протокол**, не «плохой ML».

**Feature contract по парадигме:**

| Парадигма | Признаки | Механизм |
|---|---|---|
| P300 | ERP 250–500 ms | P3b / LC-NE |
| SSVEP | Bandpower f, 2f, 3f | Phase-lock V1 |
| MI | CSP log-var 8–30 Hz | mu/beta ERD/ERS |

## 🧮 Формулы для этой задачи

$$ D_{\text{KL}}(P \| Q) = \sum_x P(x) \log\frac{P(x)}{Q(x)} $$

$$ \sigma^2_{\text{subject}}, \quad \sigma^2_{\text{session}} $$

Norm: $\mu_{\text{train}}, \sigma_{\text{train}}$ (или median/MAD) → в metadata, reuse at inference.

## Развёртка решения

### Шаг 3. Расчёт (пример)

Local 1 subj / 4 sess: $\sigma^2_{\text{session}} = 0.13$. MOABB 9 subj: $\sigma^2_{\text{subject}} = 0.42$. KL(C3 mu power) = 0.18 ✓; KL(Fp1 variance) = 0.92 → **local-only**, flag.

### Шаг 4. ❌ Наивный

```
[moabb] → [CSP on all] → [z-score all] → [export]
```

### Шаг 5. ✅ Правильный

```
[full_L1_chain] → [time_split] → [feature_extractor paradigm]
  → [norm_fit_train] → [distribution_diagnostic]
  → [cross_dataset_comparator] → [features.npz + metadata + README]
```

### Шаг 7. Журнал

> *«Переносятся paradigm-grounded features и полосы; локальны абсолютные амплитуды и impedance/blink-профиль — contract явно проводит эту границу.»*

---

# Задание 1.CAP — Capstone: полный Analyst Pipeline (интеграция 1.1–1.7)

**Код:** 1.CAP

## Сценарий

Единый Studio graph **без ручных шагов** → на выходе:
1. Nimbus-ready **`features.npz`**
2. Preprocessing **notebook**
3. **HTML/PDF quality report**
4. **`studio_graph.json`**

**Защита:** *«Какой шаг preprocessing сильнее всего изменит физиологическую интерпретацию, если его убрать?»*

## Что сдать

- Capstone graph (PNG + JSON) = 7 sub-graphs + **`health_check_combined`**
- 4 артефакта выше + **defence memo** (½ стр.) с ранжированием
- **Строка журнала**

## 📖 Нейрофизиология

Capstone **не вводит новых фактов** — проверяет, видите ли вы цепочку  
*схема измерения → ref/bands → артефакты → состояние → ICA → quality → replication*  
как **один биологический аргумент**.

## 🧮 Формула DRS (deployment readiness score)

$$ \text{DRS} = \prod_{g \in \text{gates}} \mathbb{1}[\,g \text{ passes}\,] $$

DRS = 1 только если **все** quality gates пройдены — иначе запись не идёт в L2.

## Развёртка решения

### Шаг 3. Ablation-таблица (ранжирование)

| Убран sub-graph | $\Delta f_\alpha$ | $\Delta_\alpha$ | $R$ | DRS | Влияние |
|---|---:|---:|---:|---:|---|
| **Intake (1.1)** | n/a | n/a | n/a | 0 | **Катастрофа** — потеря схемы измерения |
| **ICA (1.5)** | +0.4 | −0.05 | +6 % | 0 | Blink доминирует фронт |
| **Ref+filter (1.2)** | +1.2 | −0.18 | +3 % | 0 | Полосы ≠ генераторы |
| **Artifacts (1.3)** | +0.1 | −0.02 | +12 % | 0 | EMG в γ, bad ch poison |
| **Baseline (1.4)** | 0 | 0 | +1 % | 0 | ERP smear + leakage |
| Dashboard (1.6) | 0 | 0 | 0 | 1? | Сигнал тот же, диагностика нет |
| Replication (1.7) | 0 | 0 | 0 | 1? | Локально OK, защита слабая |

→ **Топ:** Intake и ICA labelling меняют **что такое сигнал**; filter/artifacts — **как его читать**; dashboard/replication — **что мы можем сказать**.

### Шаг 4. ❌ Наивный capstone

```
[load] → [bandpass] → [ICA] → [features] → [export]
```

Монолит, нет gates, нет metadata — работает на демо, рушится на новом субъекте.

### Шаг 5. ✅ Правильный capstone

```
[intake_subgraph_1.1]
  → [ref_filter_subgraph_1.2]
  → [artifact_subgraph_1.3]
  → [baseline_subgraph_1.4]
  → [ica_subgraph_1.5]
  → [feature_subgraph_1.7]
  → [quality_subgraph_1.6]
  → [health_check_combined]
  → [export: features.npz + studio_graph.json + quality_dashboard.html + README]
```

Каждый sub-graph — **переиспользованный артефакт** своего урока, не переписанный код.

### Шаг 6. Сравнение capstone-level

| | ❌ | ✅ |
|---|---|---|
| Структура | Монолит | Composed sub-graphs |
| Quality | Нет | DRS = 1 для L2 |
| Защита | «У меня работало» | Ablation + механизм |
| Обобщение | Локально | Replication + KL report |

### Шаг 7. Строка в журнал

> *«Шаги, меняющие **что такое сигнал** (intake, ICA), доминируют над шагами, меняющими **что мы о нём говорим** (dashboard, replication). Порядок preprocessing — сначала физиология, потом статистика, потом отчёт.»*

---

# Примечания для редактирования

- **Заголовки** `#` / `##` / `###` — автоматическое оглавление в большинстве редакторов.
- **Формулы** — LaTeX в `$$ … $$`; при отсутствии рендера формулы остаются читаемым текстом.
- **Графы Studio** — однострочное редактирование узлов в блоках ` ``` `.
- **JSON-конфиги** — валидный JSON; добавляйте ключи без смены структуры.
- **Шаблон нового задания:** Сценарий → Что сдать → 📖 Нейрофизиология → 🧮 Формулы → Развёртка (шаги 1–7).

*Конец документа · Nimbus Academy · Level 1 · Integrated Assignments · RU edition.*
