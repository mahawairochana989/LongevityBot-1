# Nimbus Academy · Level 2 — Сценарии видео для Colossyan

**Уровень:** BCI Engineer · «Почему парадигма работает»  
**Формат:** текст для ИИ-аватара (голос + on-screen + визуалы)  
**Видео в пакете:** 10 (2.0, 2.1–2.9, 2.CAP)  
**Язык:** русский  
**Инструмент пайплайнов на экране:** Nimbus Studio + NimbusSDK

---

## Общие настройки (для всех 10 роликов)

| Параметр | Значение |
|---|---|
| Персона | Инженер BCI, лекторский тон, спокойный темп |
| Фон | Тёмно-синий, слева — схема нейронной сети/парадигмы, справа — Studio граф |
| Темп | ~130 слов/мин · субтитры RU burned-in |
| Брендинг | «Nimbus Academy» нижний правый угол |
| Структура каждого ролика | (A) нейрофизиология парадигмы → (B) ❌ наивный пайплайн → (C) ✅ правильный → (D) таблица сравнения → (E) строка журнала |
| Кодирование графов | ❌ — красная рамка узлов; ✅ — зелёная |

Условные обозначения: `[ГОЛОС]`, `[ЭКРАН]`, `[ВИЗУАЛ]`, `[ПАУЗА]`.

---

# ВИДЕО 2.0 · Обзор Level 2

**ID:** `L2-V00-overview` · ~5:30

### Сцена 1 · Хук (0:00–0:50)
**[ГОЛОС]** На Level 1 вы получили feature-датасет. Level 2 учит превращать его в *декодер с уверенностью*: P300, SSVEP, MI — каждая парадигма имеет свой нейронный механизм, и под него выбирается *модель*, а не наоборот.  
**[ЭКРАН]** `features → Nimbus model → posterior → policy → command`

### Сцена 2 · Карта уровня (0:50–2:30)
**[ВИЗУАЛ]** Дорожная карта L2-P1…P8 + ethics.  
**[ГОЛОС]** Три парадигмы (P300, SSVEP, MI) → нормализация без утечки → байесовская неопределённость → дрейф → online loop → метрики → этика.

### Сцена 3 · ❌ vs ✅ на уровне (2:30–4:30)
**[ГОЛОС]** Наивный инженер берёт LDA на все парадигмы, z-score по всему датасету, accuracy на test → деплой. Правильный — подбирает модель под ковариационную структуру парадигмы, fit нормализации только на train, calibration curve, abstention policy и latency budget.

| ❌ Level 2 | ✅ Level 2 |
|---|---|
| Один LDA на всё | QDA для P300, LDA+CSP для MI, LDA/QDA для SSVEP |
| z-score по всему | mean/std на train fold |
| Только accuracy | accuracy + ITR + ECE + rejection |
| Static модель | NimbusSTS под дрейф |
| Нет ethics | model card + ethics statement |

### Сцена 4 · Закрытие (4:30–5:30)
**[ГОЛОС]** Журнал уровня: для каждого нейронного механизма парадигмы — какое допущение модели его уважает?  
**[ЭКРАН]** Следующее: **L2-V01 · P300**

---

# ВИДЕО 2.1 · P300 · NimbusQDA

**ID:** `L2-V01-p300` · ~10:30

### Сцена 1 · Нейрофизиология P300 (0:00–2:15)
**[ГОЛОС]** Locus coeruleus выбрасывает норадреналин на редкий значимый стимул. P3a — фронтальный «новизновый», P3b — париетальный «context updating». Латентность 300–500 мс зависит от сложности задачи и возраста. Это автоматический ответ — поэтому P300-BCI работает у пациентов ALS без тренировки.  
**[ЭКРАН]** Generators: parietal (P3b) + frontal (P3a) · Latency 300–500 ms  
**[ВИЗУАЛ]** ERP-кривая target vs non-target

### Сцена 2 · Гипотеза для модели (2:15–3:30)
**[ГОЛОС]** Распределения target и non-target имеют *разные ковариации*: target несёт коррелированную активность теменной коры, non-target — почти белый шум. LDA предполагает равные ковариации — гипотеза нарушена. QDA моделирует две матрицы и выигрывает биологически, не «случайно».  
**[ЭКРАН]** LDA: Σ₀ = Σ₁ · QDA: Σ₀ ≠ Σ₁  
`δ_QDA(x) = −½ log|Σ_k| − ½ (x−µ_k)ᵀ Σ_k⁻¹ (x−µ_k) + log π_k`

### Сцена 3 · ❌ Наивный пайплайн (3:30–5:30)
**[ВИЗУАЛ]**
```
[raw] → [bandpass 1-40] → [epochs -0.1..0.6] → [LDA] → [accuracy]
```
Ошибки: полоса 1–40 Гц «съедает» медленный P300; baseline до −0.1 c — слишком короткий; LDA = неверная ковариация; нет ITR, нет CV по subject; xDAWN не использован.

### Сцена 4 · ✅ Правильный пайплайн (5:30–8:00)
**[ВИЗУАЛ]**
```
[clean_raw] → [bandpass 0.5-10] → [downsample 64-128]
  → [epochs -0.2..0.8 + baseline (-0.2,0)] → [xDAWN spatial]
  → [feature_extractor: amp windows 250-500ms] → [NimbusQDA fit]
  → [posterior + ITR + confusion + reliability]
```
**[ГОЛОС]** Полоса 0.5–10 Гц — потому что P300 — медленный корковый процесс. xDAWN усиливает target signature. Окна признаков 250–500 мс — анатомический адрес P3b.  
**[ЭКРАН]** `ITR = log₂(N) + p log p + (1-p) log[(1-p)/(N-1)]` (Wolpaw)

### Сцена 5 · Расчёт (8:00–9:00)
**[ГОЛОС]** Пример: 6 классов (matrix speller), accuracy 0.85, trial 3 c. ITR ≈ 30.3 бит/мин — рабочая система.

### Сцена 6 · Сравнение + журнал (9:00–10:30)
| | ❌ | ✅ |
|---|---|---|
| Полоса | 1–40 (артефактно широкая) | 0.5–10 (физиологична) |
| Модель | LDA | QDA |
| Метрика | accuracy | accuracy + ITR + ECE |
**[ГОЛОС]** Журнал: «QDA выбран потому, что *ковариации target и non-target физически разные*».

---

# ВИДЕО 2.2 · SSVEP · CCA / NimbusLDA-QDA

**ID:** `L2-V02-ssvep` · ~9:45

### Сцена 1 · Нейрофизиология SSVEP (0:00–2:00)
**[ГОЛОС]** V1-нейроны входят в фазовую блокировку с частотой мерцания. Топография: Oz, O1, O2, PO7, PO8 — это адрес первичной зрительной коры. Гармоники 2f и 3f несут реальную информацию. Полоса 6–30 Гц: ниже — утомление, выше — потеря отклика.  
**[ЭКРАН]** Latency 100–200 ms · Phase-locking V1  
**[ВИЗУАЛ]** Анимация мерцающего стимула → пик в спектре Oz

### Сцена 2 · Гипотеза для CCA (2:00–3:00)
**[ГОЛОС]** CCA ищет линейную комбинацию каналов, максимально коррелирующую с синусами на f, 2f, 3f. Физически — потому что мозг действительно фазово синхронизирован с мерцанием.  
**[ЭКРАН]** `ρ = max corr(X·W_x, Y·W_y)` · Y = sin/cos(2π·k·f·t)

### Сцена 3 · ❌ Наивный пайплайн (3:00–4:30)
**[ВИЗУАЛ]**
```
[raw all channels] → [bandpower @ f only] → [argmax target] → done
```
Ошибки: брать все каналы (теряем SNR); только основная частота (игнор гармоник); окно 0.5 с (мало для разрешения); нет CCA; нет confidence.

### Сцена 4 · ✅ Правильный пайплайн (4:30–7:00)
**[ВИЗУАЛ]**
```
[occipital channels: Oz/O1/O2/PO7/PO8] → [bandpass: f±2 Hz with harmonics]
  → [epochs 1-4 s adaptive] → [CCA features] → [NimbusLDA or QDA]
  → [latency-vs-accuracy curve]
```
**[ГОЛОС]** Длина окна — компромисс latency/accuracy: 2 с — типовая точка. Гармоники 2f, 3f включены в reference matrix CCA.  
**[ЭКРАН]** Δf разрешение = 1/T_window

### Сцена 5 · Расчёт (7:00–8:00)
**[ГОЛОС]** Пример: 4 цели на 8, 10, 12, 15 Гц, окно 2 с — Δf = 0.5 Гц, цели разделимы. ITR ≈ 60 бит/мин при accuracy 0.9.

### Сцена 6 · Сравнение + журнал (8:00–9:45)
| | ❌ | ✅ |
|---|---|---|
| Каналы | все | окципитальные V1 |
| Признаки | bandpower @ f | CCA с гармониками |
| Окно | фиксировано | latency/accuracy curve |
**[ГОЛОС]** Журнал: «CCA работает потому, что фазовая блокировка V1 — реальная физика, а не статистическая корреляция».

---

# ВИДЕО 2.3 · Motor Imagery · CSP + NimbusLDA

**ID:** `L2-V03-mi` · ~10:30

### Сцена 1 · Нейрофизиология MI (0:00–2:15)
**[ГОЛОС]** Зеркальные нейроны премоторной коры включаются и при движении, и при его воображении. ERD в mu/beta — дезингибиция таламо-кортикальной петли. После — ERS (rebound). Топография: C3/C4/Cz контралатерально воображаемой конечности. 10–30% людей — BCI non-responders: анатомическая особенность, не «плохой студент».  
**[ЭКРАН]** mu 8–13 Hz · beta 13–30 Hz · ERD/ERS

### Сцена 2 · Зачем CSP (2:15–3:30)
**[ГОЛОС]** CSP ищет пространственные фильтры, максимизирующие variance одного класса при минимизации другого — это инженерная реализация поиска источников ERD. log-variance первых k компонент = вход для LDA. Shared covariance (LDA) уместен в CSP-пространстве.  
**[ЭКРАН]** `max wᵀΣ₁w / wᵀΣ₂w` · log-var(w·X)

### Сцена 3 · ❌ Наивный пайплайн (3:30–5:30)
**[ВИЗУАЛ]**
```
[raw] → [bandpass 1-40] → [features = raw amplitudes]
  → [QDA on raw channels] → [test accuracy]
```
Ошибки: широкая полоса (нет ERD-фокуса); нет CSP; QDA на raw → переобучение; нет cue baseline; нет FBCSP.

### Сцена 4 · ✅ Правильный пайплайн (5:30–8:00)
**[ВИЗУАЛ]**
```
[clean_raw] → [bandpass 8-30 (или FBCSP 4 subbands)]
  → [epochs 0.5-2.5 s + baseline pre-cue] → [CSP fit on train only]
  → [log-var top-k] → [NimbusLDA] → [posterior + topomap check]
```
**[ГОЛОС]** Полоса 8–30 — адрес моторного осциллятора. CSP fit *только* на train. Топография CSP-паттернов должна быть над C3/C4 — иначе это артефакт.

### Сцена 5 · Расчёт + проверка (8:00–9:15)
**[ГОЛОС]** k=6 фильтров, окно 2 с, FBCSP 4-полосный → accuracy ~0.78–0.85 на BNCI2014-001. Если топография CSP над Fp — модель учит EOG, не MI.  
**[ЭКРАН]** Sanity: argmax(|CSP pattern|) ∈ sensorimotor strip

### Сцена 6 · Сравнение + журнал (9:15–10:30)
| | ❌ | ✅ |
|---|---|---|
| Spatial filter | нет | CSP/FBCSP |
| Полоса | 1–40 | 8–30 (paradigm-specific) |
| Проверка | accuracy | topomap-sanity |
**[ГОЛОС]** Журнал: «CSP-топография — физиологический санчек; если она не сенсомоторная, мы декодируем не MI».

---

# ВИДЕО 2.4 · Feature normalization · Полосы как состояния мозга

**ID:** `L2-V04-norm` · ~9:00

### Сцена 1 · Нейрофизиология полос (0:00–1:45)
**[ГОЛОС]** Альфа — pulsed inhibition по Klimesch; тета — гиппокампо-фронтальная связь; бета-rebound — пост-моторная синхрония; high-gamma — прокси спайков (требует sfreq ≥ 500 Гц). Нормализация хранит *биологический baseline сессии*.  
**[ЭКРАН]** α inhibits · θ binds · β stabilizes · γ ≈ spikes

### Сцена 2 · Что такое утечка (1:45–3:00)
**[ГОЛОС]** Если mean/std оценены на всех данных, модель «подсмотрела» будущее → ложно высокая accuracy. Calibration set ≠ test set; разделение по времени, не по случайному split.  
**[ЭКРАН]** `z = (x − µ_train) / σ_train` · сохранять mean/std/median/MAD в `norm_params.json`

### Сцена 3 · ❌ Наивный пайплайн (3:00–4:30)
**[ВИЗУАЛ]**
```
[features all] → [z-score all] → [random split] → [model] → 0.95 acc
```
Ошибки: leakage; random split смешивает соседние эпохи; нет сохранения параметров для streaming.

### Сцена 4 · ✅ Правильный пайплайн (4:30–7:00)
**[ВИЗУАЛ]**
```
[features] → [time-split: train/cal/test] → [fit norm on train]
  → [save norm_params.json] → [apply on cal/test/stream]
  → [leakage demo notebook]
```
**[ГОЛОС]** Robust-нормализация: median + MAD вместо mean + std при тяжёлых хвостах. Параметры — часть model card.  
**[ЭКРАН]** `MAD = median(|x − median(x)|)` · `z_robust = (x − median) / (1.4826·MAD)`

### Сцена 5 · Демо разницы (7:00–8:00)
**[ГОЛОС]** Та же модель: leakage → 0.92, правильная нормализация → 0.78. Разница — это размер обмана при «лабораторной» accuracy.

### Сцена 6 · Сравнение + журнал (8:00–9:00)
**[ГОЛОС]** Журнал: «Нормализация — это договор о baseline сессии; утечка = смешение состояний мозга, которые модель не должна была видеть».

---

# ВИДЕО 2.5 · Bayesian uncertainty · Predictive coding

**ID:** `L2-V05-uncertainty` · ~10:45

### Сцена 1 · Нейрофизиология uncertainty (0:00–2:15)
**[ГОЛОС]** Predictive coding по Фристону: кора непрерывно предсказывает и обновляется по prediction error. Precision = вес источника (буквальный аналог posterior). Anterior cingulate кодирует конфликт; pupil dilation — наблюдаемый маркер uncertainty через LC-NE. Мозг хранит распределение, не точку.  
**[ЭКРАН]** Brain ≈ Bayesian inference engine

### Сцена 2 · От posterior к политике (2:15–3:30)
**[ГОЛОС]** Из Nimbus-модели берём posterior `p(y|x)`. Predictive entropy `H = −Σ pᵢ log pᵢ`. ECE — насколько confidence соответствует accuracy в bins.  
**[ЭКРАН]** Threshold policy: execute / confirm / reject

### Сцена 3 · ❌ Наивный пайплайн (3:30–5:30)
**[ВИЗУАЛ]**
```
[model] → [argmax posterior] → [command always]
```
Ошибки: нет порога; нет calibration; «уверенный, но неправ» проходит молча; ECE 0.18 — модель самоуверенна; нет abstention.

### Сцена 4 · ✅ Правильный пайплайн (5:30–8:15)
**[ВИЗУАЛ]**
```
[model.posterior] → [entropy + max_posterior] → [calibrator: isotonic/Platt]
  → [reliability_diagram] → [policy: execute if max>τ₁ & H<τ₂ ; confirm if intermediate ; reject otherwise]
  → [abstention_metrics.json] → [safety_gate]
```
**[ГОЛОС]** Calibration сначала, политика — после. Trade-off: rejection rate ↑ → ошибки ↓, ITR ↓.  
**[ЭКРАН]** ECE до 0.18, после калибровки 0.04

### Сцена 5 · Расчёт (8:15–9:30)
**[ГОЛОС]** Пример: P300 speller, τ₁=0.65, τ₂=0.8. Rejection rate 0.22, accuracy на принятых 0.96, expected harm ≈ 0 для symbol typing.

### Сцена 6 · Сравнение + журнал (9:30–10:45)
**[ГОЛОС]** Журнал: «Uncertainty — это не слабость модели, а имитация того, как мозг сам декодирует мир».

---

# ВИДЕО 2.6 · Neural drift · NimbusSTS

**ID:** `L2-V06-drift` · ~10:00

### Сцена 1 · Нейрофизиология дрейфа (0:00–2:00)
**[ГОЛОС]** LTP/LTD меняют синапсы в реальном времени; гомеостатическая пластичность нормализует gain; дофамин и ацетилхолин модулируют состояние; сон консолидирует — между-сессионный дрейф особенно велик. BCI-обучение реально меняет мозг.  
**[ЭКРАН]** Brain(t) ≠ Brain(t+T)

### Сцена 2 · Static vs adaptive (2:00–3:15)
**[ГОЛОС]** NimbusSTS — модель со скрытым состоянием, обновляющая параметры по новым данным. Подходит, когда дрейф медленный и направленный (week-to-week обучение).  
**[ЭКРАН]** STS update rule: state_t = f(state_{t−1}, x_t)

### Сцена 3 · ❌ Наивный пайплайн (3:15–5:15)
**[ВИЗУАЛ]**
```
[train static LDA on session 1] → [deploy] → [accuracy down 30% by session 5]
```
Ошибки: random CV маскирует дрейф; нет session split; нет переобучения; нет rejection rate во времени.

### Сцена 4 · ✅ Правильный пайплайн (5:15–7:45)
**[ВИЗУАЛ]**
```
[session-wise CV] → [train static baseline LDA/QDA]
  → [train NimbusSTS with adaptive update] → [evaluate per session]
  → [drift_curve: accuracy(t), ECE(t), rejection(t)]
  → [model_card: drift coverage]
```
**[ГОЛОС]** Сравните static vs STS на N сессиях — это график честности модели против биологии.

### Сцена 5 · Расчёт (7:45–8:45)
**[ГОЛОС]** Static: session 1 → 0.82, session 5 → 0.61. STS: 0.82 → 0.78. Разница 0.17 — стоимость игнорирования пластичности.

### Сцена 6 · Сравнение + журнал (8:45–10:00)
**[ГОЛОС]** Журнал: «Static model биологически нечестна — мозг адаптируется, и модель обязана отвечать тем же».

---

# ВИДЕО 2.7 · Online loop · LSL + StreamingSession

**ID:** `L2-V07-online` · ~10:30

### Сцена 1 · Нейрофизиология latency (0:00–2:00)
**[ГОЛОС]** Цепь PSP → суммация → череп (spatial low-pass) → скальп → электрод. Скорость проводимости 50–100 мс, время реакции 150–200 мс. Temporal binding window ~150 мс: если задержка BCI больше — пользователь перестаёт чувствовать систему как продолжение себя. Efference copy: мозг знает о движении до сенсорной обратной связи.  
**[ЭКРАН]** Budget end-to-end ≤ 150 ms

### Сцена 2 · LSL / BrainFlow роль (2:00–3:00)
**[ГОЛОС]** LSL — сетевой транспорт меток времени; BrainFlow — унифицированный доступ к hardware. StreamingSession — Nimbus-обёртка, держащая контракт preprocessing + features + model + policy.

### Сцена 3 · ❌ Наивный пайплайн (3:00–5:00)
**[ВИЗУАЛ]**
```
[device] → [single big window 5s] → [reload model each chunk]
  → [no latency log] → [no sliding posterior]
```
Ошибки: окно 5 с (выше binding window); перезагрузка модели на каждом chunk; нет sliding vote; нет budget per node.

### Сцена 4 · ✅ Правильный пайплайн (5:00–8:00)
**[ВИЗУАЛ]**
```
[LSL/BrainFlow] → [ring_buffer] → [chunker: window 1-2s, hop 250ms]
  → [preproc_apply] → [features] → [NimbusSDK.StreamingSession]
  → [sliding_posterior + weighted_vote] → [safety_gate] → [command]
  → [latency_budget.json]
```
**[ГОЛОС]** Каждый узел получает свой budget в мс. Sliding vote снимает шум одиночного chunk.

### Сцена 5 · Расчёт budget (8:00–9:15)
**[ГОЛОС]** acquisition 20 ms · filter 15 ms · features 10 ms · inference 8 ms · policy 5 ms → 58 ms < 150 ms ✓.

### Сцена 6 · Сравнение + журнал (9:15–10:30)
**[ГОЛОС]** Журнал: «Latency budget — биологическая константа, а не инженерное удобство».

---

# ВИДЕО 2.8 · Metrics dashboard · Шеннон и нейрон

**ID:** `L2-V08-metrics` · ~9:00

### Сцена 1 · Нейрофизиология информации (0:00–1:45)
**[ГОЛОС]** Capacity нейронного канала ограничена шумом и спайковой статистикой. Temporal vs rate coding. Bottleneck BCI лежит между электродом, фильтром, признаком и моделью — найти его и сравнить с biological capacity.  
**[ЭКРАН]** ITR = bridge Shannon ↔ BCI

### Сцена 2 · Какие метрики реально нужны (1:45–3:00)
**[ГОЛОС]** accuracy, balanced accuracy, ITR, latency, ECE, rejection rate, user reliability. 70% accuracy в P300 — уже полезная система при правильном ITR.  
**[ЭКРАН]** ITR Wolpaw · reliability diagram

### Сцена 3 · ❌ Наивный пайплайн (3:00–4:30)
**[ВИЗУАЛ]**
```
[model] → [accuracy] → "0.86, good"
```
Ошибки: одна цифра; нет balanced; нет ITR; нет per-subject; нет calibration; нет фильтров в dashboard.

### Сцена 4 · ✅ Правильный пайплайн (4:30–7:00)
**[ВИЗУАЛ]**
```
[model.eval] → [metric_set] → [reliability_diagram] → [per_subject_per_session]
  → [model_comparison: LDA/QDA/Softmax/STS] → [HTML dashboard with filters]
```

### Сцена 5 · Расчёт пример (7:00–8:00)
**[ГОЛОС]** P300: acc 0.85, 6 классов, 3 с trial → ITR ≈ 30 бит/мин. SSVEP: acc 0.95, 4 класса, 2 с → ITR ≈ 50 бит/мин.

### Сцена 6 · Сравнение + журнал (8:00–9:00)
**[ГОЛОС]** Журнал: «ITR — мера, насколько BCI приближается к собственной полосе пропускания мозга».

---

# ВИДЕО 2.9 · Этика BCI · Защита L2 портфолио

**ID:** `L2-V09-ethics` · ~8:00

### Сцена 1 · Нейроданные как особая категория (0:00–2:00)
**[ГОЛОС]** Что реально декодируется из ЭЭГ — конкретные операционализированные маркеры, а не «мысли». ЭЭГ-биометрика существует. Нейроправа: ООН, чилийская конституция, EU AI Act. Когнитивное усиление через BCI и проблема доступа.  
**[ЭКРАН]** Decodable now / soon / no

### Сцена 2 · ❌ Наивный «упаковщик» (2:00–3:30)
**[ВИЗУАЛ]**
```
[model.pkl] → [zip] → ship
```
Ошибки: нет ethics statement; нет consent metadata; нет retention; нет risk log; нет audit trail.

### Сцена 3 · ✅ Правильная упаковка (3:30–6:00)
**[ВИЗУАЛ]**
```
[model + norm_params + feature_contract + confidence_policy + streaming_demo]
  → [ethics_statement.md per paradigm]
  → [consent + retention in metadata.json]
  → [risk_log.md → safety thresholds]
  → [audit_log]
```

### Сцена 4 · Сравнение + журнал (6:00–8:00)
**[ГОЛОС]** Журнал: «Регуляторика BCI развивается быстрее остального медтеха, потому что нейроданные физически уникальны».

---

# ВИДЕО 2.CAP · Capstone Level 2 · Decoder package

**ID:** `L2-VCAP` · ~12:00

### Сцена 1 · Задача (0:00–1:00)
**[ГОЛОС]** Собрать Nimbus decoder package для одной парадигмы + streaming demo + ethics. Защита: почему именно эта модель уважает нейронный механизм парадигмы?

### Сцена 2 · ❌ Монолитный capstone (1:00–4:00)
**[ВИЗУАЛ]** Один скрипт `train_predict.py`; LDA на всё; нет calibration; нет streaming session; нет model card.

### Сцена 3 · ✅ Эталонный capstone (4:00–8:30)
**[ВИЗУАЛ]**
```
[paradigm_pipeline_subgraph]
  → [features_subgraph]
  → [Nimbus_model: QDA|LDA+CSP|LDA+CCA|STS depending on paradigm]
  → [calibrator + policy]
  → [streaming_session]
  → [metrics_dashboard]
  → [ethics_statement]
  → [export: model + norm_params + model_card + demo.mp4]
```

### Сцена 4 · Сравнение (8:30–10:00)
**[ЭКРАН]** 9 строк по урокам 2.1–2.9, что теряется при пропуске.

### Сцена 5 · Ответ защиты (10:00–12:00)
**[ГОЛОС]** Чаще всего пропускается *calibration* и *abstention* — они меняют биологический смысл posterior. Второй риск — leakage в нормализации.

---

# BATCH-ЗАПРОС К COLOSSYAN (создать все 10 видео Level 2)

```text
ПРОЕКТ: Nimbus Academy — Level 2 BCI Engineer (10 видео)

РОЛЬ ИИ: режиссёр и сценарист обучающих видео с ИИ-аватаром. Создай РОВНО 10 отдельных видео по спецификации. Не объединяй уроки.

ОБЩИЕ ТРЕБОВАНИЯ:
- Язык: русский, субтитры RU burned-in.
- Аватар: инженер 35–45 лет, деловой casual, в камеру ~70%.
- Фон: тёмно-синий градиент; слева — схема парадигмы/нейронной сети; справа — Nimbus Studio граф.
- Каждое видео обязано иметь: (A) нейрофизиология парадигмы/механизма 1–2 мин, (B) ❌ наивный пайплайн с озвучкой ошибок, (C) ✅ правильный пайплайн пошагово в Studio + NimbusSDK, (D) таблица сравнения, (E) строка журнала.
- ❌ граф — красная рамка, ✅ — зелёная.
- Без stock-видео людей в шапках; только схемы, ERP, PSD, topomap, dashboard mockups.
- Логотип Nimbus Academy внизу справа.

СПИСОК ВИДЕО:
1) L2-V00 | «Level 2 — Обзор: от feature к decoder с уверенностью» | 5:30 | карта L2-P1…P8 + ethics; ❌ один LDA на всё vs ✅ модель под парадигму.
2) L2-V01 | «2.1 P300 NimbusQDA» | 10:30 | LC-NE, P3a/P3b, context updating. ❌ LDA + полоса 1–40. ✅ 0.5–10 Гц + xDAWN + QDA + ITR/ECE.
3) L2-V02 | «2.2 SSVEP CCA» | 9:45 | V1 phase-locking, гармоники. ❌ все каналы + bandpower @ f. ✅ окципитальные + CCA с 2f,3f + LDA/QDA.
4) L2-V03 | «2.3 MI CSP+LDA» | 10:30 | зеркальные нейроны, ERD/ERS mu/beta. ❌ raw QDA. ✅ 8–30 Гц + CSP train-only + LDA + topomap sanity.
5) L2-V04 | «2.4 Feature normalization» | 9 мин | альфа/тета/бета/гамма как состояния. ❌ z-score all. ✅ time-split + norm_params.json + robust median/MAD.
6) L2-V05 | «2.5 Bayesian uncertainty» | 10:45 | predictive coding, precision, ACC. ❌ argmax. ✅ entropy + calibration + execute/confirm/reject + ECE.
7) L2-V06 | «2.6 Neural drift / STS» | 10 мин | LTP/LTD, дофамин, сон. ❌ static LDA. ✅ session split + NimbusSTS + drift curve.
8) L2-V07 | «2.7 Online loop» | 10:30 | latency сенсорики, temporal binding ~150ms. ❌ окно 5 с. ✅ LSL+ring buffer+StreamingSession+latency budget.
9) L2-V08 | «2.8 Metrics dashboard» | 9 мин | Shannon ↔ нейрон, capacity. ❌ только accuracy. ✅ ITR+ECE+rejection+per-subject HTML.
10) L2-V09 | «2.9 Ethics + portfolio» | 8 мин | нейроправа, биометрика. ❌ zip model. ✅ ethics_statement + retention + risk log + audit.
+) L2-VCAP | «Capstone L2 Decoder package» | 12 мин | интеграция; ❌ монолит; ✅ paradigm pipeline + Nimbus model + calibration + streaming + model card.

ИТОГО: 11 видео (10 уроков + capstone). Если bulk-генерация ограничена 10 — capstone генерируется отдельно следующим заказом с тем же стилем.

ФОРМАТ ВЫВОДА: для каждого ID отдельная сцена 8–14 shots, speaker notes, on-screen ≤12 слов, thumbnail = ID + название. Экспорт 1080p, имена L2-V00.mp4 … L2-VCAP.mp4. Плейлист «Nimbus L2».
```
