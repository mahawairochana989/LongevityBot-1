# Nimbus Academy · Level 3 — Сценарии видео для Colossyan

**Уровень:** Researcher · Research Pipeline  
**Видео в пакете:** 12 (3.0, 3.1–3.10, 3.CAP)  
**Язык:** русский · ИИ-аватар + on-screen Nimbus Studio граф  
**Структура каждого ролика:** нейрофизиология → ❌ наивный пайплайн → ✅ правильный → таблица сравнения → строка журнала

---

## Общие настройки

| Параметр | Значение |
|---|---|
| Персона | Исследователь-нейроинженер, академический тон |
| Фон | Тёмно-синий; слева — анатомическая схема; справа — Nimbus Studio граф |
| Темп | ~125 слов/мин · субтитры RU |
| Кодирование графов | ❌ красная рамка / ✅ зелёная рамка |

---

# ВИДЕО 3.0 · Обзор Level 3

**ID:** `L3-V00-overview` · ~5:30

### Сцена 1 · Хук (0:00–0:50)
**[ГОЛОС]** На Level 1 у вас данные, на Level 2 — декодер. Level 3 учит превращать пайплайн в *исследовательский протокол*: от предрегистрации до mini-paper. Каждое решение должно быть обосновано механизмом, не accuracy.

### Сцена 2 · Карта уровня (0:50–2:30)
**[ВИЗУАЛ]** Дорога: design → ERP → TF → connectivity → source → MVPA → stats → reproducibility → paper → neurofeedback.

### Сцена 3 · ❌ vs ✅ (2:30–4:30)
| ❌ Level 3 | ✅ Level 3 |
|---|---|
| «Возьмём что есть» | Preregistration до сбора |
| Параметры из туториала | Параметры из анатомии генератора |
| p < 0.05 везде | Cluster-based + effect size |
| Notebook на 1 машине | BIDS + Conda + Docker |
| «Мы использовали MNE» | Methods через data contract |

### Сцена 4 · Закрытие (4:30–5:30)
**[ГОЛОС]** Журнал уровня: какое предметное знание превращает мою accuracy в *утверждение о мозге*?

---

# ВИДЕО 3.1 · Дизайн эксперимента + Preregistration

**ID:** `L3-V01-design` · ~9:30

### Сцена 1 · Нейрофизиология парадигм (0:00–2:00)
**[ГОЛОС]** Oddball/MMN — автодетектор девиантов; Flanker/Stroop/Go-NoGo — ACC и DLPFC; N-back — рабочая память (поддержание vs манипуляция). Between-subjects требует больших N из-за биологической вариабельности. Скучная задача → плохая наука: arousal критичен.  
**[ЭКРАН]** Paradigm = address of cortical mechanism

### Сцена 2 · ❌ Наивный пайплайн (2:00–4:00)
**[ВИЗУАЛ]**
```
[сбор данных] → [много анализов] → [пишем то, что вышло]
```
Ошибки: HARKing (hypothesis after results); p-hacking; нет stopping rule; нет планируемого feature contract.

### Сцена 3 · ✅ Правильный пайплайн (4:00–7:00)
**[ВИЗУАЛ]**
```
[hypothesis spec] → [paradigm + power calc] → [feature_contract draft]
  → [planned analysis + Nimbus model choice] → [stopping rule]
  → [OSF preregistration draft 1-2 pages] → [data collection]
```
**[ГОЛОС]** Feature contract решается *до* данных. Модель выбирается из карты курса (P300→QDA, MI→LDA+CSP). Stopping rule защищает от sequential analysis bias.

### Сцена 4 · Сравнение + журнал (7:00–9:30)
**[ГОЛОС]** Журнал: «Дизайн без знания нейронного субстрата измеряет что-то другое, чем заявлено».

---

# ВИДЕО 3.2 · ERP-углублённо · ERP → Nimbus

**ID:** `L3-V02-erp` · ~10:00

### Сцена 1 · Архитектура ERP (0:00–2:30)
**[ГОЛОС]** N100 — первичная слуховая кора; P200 — сенсорное стробирование; N200 — ACC конфликт; P300 — LC-NE/париетальная; N400 — левая височная семантика; P600 — синтаксис; CNV — SMA+PFC готовность.  
**[ЭКРАН]** Component window ≡ anatomical address

### Сцена 2 · ❌ Наивный пайплайн (2:30–4:30)
**[ВИЗУАЛ]**
```
[epochs] → [grand average] → [pick peak amplitude] → [t-test]
```
Ошибки: окно «по удобству», не по анатомии; нет CIs/bootstrap; нет subject-level; нет alternative metric (mean vs peak).

### Сцена 3 · ✅ Правильный пайплайн (4:30–8:00)
**[ВИЗУАЛ]**
```
[clean_epochs] → [component_windows_from_anatomy] → [mean amplitude + peak]
  → [bootstrap CIs] → [subject + group level] → [features → NimbusQDA]
  → [Methods paragraph via data_contract]
```
**[ГОЛОС]** Сравните два аналитических пайплайна (mean vs peak) на тех же эпохах — выбор обосновывается анатомией, а не разницей p-values.

### Сцена 4 · Сравнение + журнал (8:00–10:00)
**[ГОЛОС]** Журнал: «Временное окно компонента — адрес генератора, а не настройка».

---

# ВИДЕО 3.3 · Time-frequency · TF feature pipeline

**ID:** `L3-V03-tf` · ~10:00

### Сцена 1 · Осцилляторная динамика (0:00–2:15)
**[ГОЛОС]** PING-модель γ (pyramidal-interneuron); θ-γ coupling упаковки воспоминаний; α pulsed inhibition; β статус-кво; CFC — иерархическая коммуникация; phase precession — нейронные часы.  
**[ЭКРАН]** Trade-off: Δt · Δf ≥ 1/(4π) (uncertainty)

### Сцена 2 · ❌ Наивный пайплайн (2:15–4:15)
**[ВИЗУАЛ]**
```
[STFT с одним окном] → [log-сетка частот] → [TF map] → "красиво"
```
Ошибки: одно окно для всех полос (плохо для γ); логарифмическая сетка без биологической мотивации; ERD/ERS не нормированы к baseline.

### Сцена 3 · ✅ Правильный пайплайн (4:15–7:30)
**[ВИЗУАЛ]**
```
[clean_epochs] → [Morlet wavelets (или STFT с band-specific windows)]
  → [ERD/ERS = (P − P_baseline) / P_baseline] → [biologically motivated bands]
  → [features: band × window × channel] → [NimbusLDA/QDA/Softmax compare]
  → [TF feature contract]
```
**[ГОЛОС]** Wavelets дают переменную time-frequency resolution — биологически уместно. ERD/ERS — относительная мера, не абсолютная амплитуда.

### Сцена 4 · Сравнение + журнал (7:30–10:00)
**[ГОЛОС]** Журнал: «TF-анализ — вокруг биологических полос, не вокруг логарифмической сетки».

---

# ВИДЕО 3.4 · Connectivity · Coherence / PLV / wPLI

**ID:** `L3-V04-conn` · ~10:00

### Сцена 1 · Как области разговаривают (0:00–2:15)
**[ГОЛОС]** DMN (MPFC+PCC), Salience (insula+ACC), ECN (DLPFC+parietal). Аксональные задержки — физическая основа фазового лага. Dynamic FC меняется каждые секунды. Volume conduction даёт ложную связность — wPLI её устраняет.  
**[ЭКРАН]** Coherence (mag) · PLV (phase) · wPLI (volume-conduction safe)

### Сцена 2 · ❌ Наивный пайплайн (2:15–4:30)
**[ВИЗУАЛ]**
```
[sensor-level coherence] → [пары всех каналов] → [graph metrics]
```
Ошибки: volume conduction даёт «связь» между соседями; нет source-space; нет permutation; никакого anatomical caveat.

### Сцена 3 · ✅ Правильный пайплайн (4:30–7:30)
**[ВИЗУАЛ]**
```
[clean] → [source_projection (опционально)] → [wPLI per band]
  → [graph: degree, clustering, path_length] → [permutation tests]
  → [Nimbus features] → [connectivity report с anatomical caveats]
```

### Сцена 4 · Сравнение + журнал (7:30–10:00)
**[ГОЛОС]** Журнал: «Connectivity без знания путей — числа без смысла».

---

# ВИДЕО 3.5 · Source localization · Анатомия генераторов

**ID:** `L3-V05-source` · ~9:45

### Сцена 1 · Где сидят источники (0:00–2:15)
**[ГОЛОС]** Цитоархитектоника Бродмана: BA7 ≠ BA40. Гиры и борозды определяют направление диполя. Глубокие источники (амигдала, гиппокамп) почти неразрешимы. Атласы: Desikan-Killiany, Schaefer, AAL.  
**[ЭКРАН]** Источник = гипотеза, не «координата»

### Сцена 2 · ❌ Наивный пайплайн (2:15–4:15)
**[ВИЗУАЛ]**
```
[sensors] → [одноразовый dSPM] → [«нашли источник»]
```
Ошибки: нет forward model; одна inverse без сравнения; нет caveats spatial smearing; глубокий источник интерпретирован как кортикальный.

### Сцена 3 · ✅ Правильный пайплайн (4:15–7:30)
**[ВИЗУАЛ]**
```
[clean] → [forward: BEM или fsaverage] → [inverse: dSPM/sLORETA/MNE compare]
  → [dipole fit для конкретных ERP] → [sensor vs source features → Nimbus]
  → [limits: smearing, non-identifiability]
```

### Сцена 4 · Сравнение + журнал (7:30–9:45)
**[ГОЛОС]** Журнал: «Source localization — гипотеза о физиологии, зависящая от модели головы и атласа».

---

# ВИДЕО 3.6 · MVPA · Temporal generalization + RSA

**ID:** `L3-V06-mvpa` · ~10:15

### Сцена 1 · Что декодирует MVPA (0:00–2:00)
**[ГОЛОС]** Population codes — распределённые vs локальные представления. Manifold hypothesis — низкоразмерное многообразие. Temporal dynamics: *когда* категория появляется в коде. RSA сравнивает нейронный код с когнитивной моделью.  
**[ЭКРАН]** Decoder = «есть ли информация»; RSA = «какая структура»

### Сцена 2 · ❌ Наивный пайплайн (2:00–4:00)
**[ВИЗУАЛ]**
```
[features] → [random CV] → [decode every t] → [красная zone]
```
Ошибки: random split утечка по subject/session; нет permutation для significance; нет temporal generalization (train @ t, test @ t').

### Сцена 3 · ✅ Правильный пайплайн (4:00–7:30)
**[ВИЗУАЛ]**
```
[features] → [subject/session split] → [decoder per time]
  → [temporal_generalization matrix] → [permutation null]
  → [RSA: empirical RDM vs model RDMs]
  → [posterior_confidence(t)]
```

### Сцена 4 · Сравнение + журнал (7:30–10:15)
**[ГОЛОС]** Журнал: «Что MVPA находит, определяется нейронаукой представлений, не accuracy сама по себе».

---

# ВИДЕО 3.7 · Статистика и cluster-permutation · Sweep

**ID:** `L3-V07-stats` · ~9:30

### Сцена 1 · Физиология статистики (0:00–1:45)
**[ГОЛОС]** EEG автокоррелирован во времени и пространстве — это не «нарушение», это синхронизация ансамбля. Cluster-based permutation учитывает биологически правдоподобные смежные эффекты. Effect size ≠ p-value.  
**[ЭКРАН]** Autocorrelation = biology, not bug

### Сцена 2 · ❌ Наивный пайплайн (1:45–3:45)
**[ВИЗУАЛ]**
```
[t-test per channel per time] → [Bonferroni] → [ничего не значимо]
```
Ошибки: уничтожает мощность; игнорирует пространство; нет sweep моделей.

### Сцена 3 · ✅ Правильный пайплайн (3:45–6:45)
**[ВИЗУАЛ]**
```
[features] → [config_sweep: bands × windows × norm × model]
  → [cluster_based_permutation] → [benchmark_matrix LDA/QDA/Softmax]
  → [choose Studio variant + spec.yaml] → [stat_rationale in paper]
```

### Сцена 4 · Сравнение + журнал (6:45–9:30)
**[ГОЛОС]** Журнал: «Правильный тест отражает структуру сигнала, а не дефолт туториала».

---

# ВИДЕО 3.8 · Reproducibility · BIDS + Docker

**ID:** `L3-V08-repro` · ~9:00

### Сцена 1 · Почему не воспроизводится (0:00–1:45)
**[ГОЛОС]** Биологическая вариабельность норма; state-dependency; ceiling effects у здоровых; demand characteristics; между-лаб различия hardware.  
**[ЭКРАН]** BIDS = методологический контроль вариабельности

### Сцена 2 · ❌ Наивный пайплайн (1:45–3:30)
**[ВИЗУАЛ]**
```
[notebook.ipynb] → [«у меня работает»] → [полгода спустя — ничего]
```
Ошибки: разрозненные файлы; нет seed; нет env lock; нет audit log; нет SDK version.

### Сцена 3 · ✅ Правильный пайплайн (3:30–7:00)
**[ВИЗУАЛ]**
```
[BIDS-EEG dataset] → [Studio export + Conda env + SDK version pin]
  → [seeds + run_manifest.json] → [Docker image]
  → [audit_log.csv: who/when/version]
```

### Сцена 4 · Сравнение + журнал (7:00–9:00)
**[ГОЛОС]** Журнал: «Reproducibility — это уважение к биологической вариабельности».

---

# ВИДЕО 3.9 · Mini-paper · Methods через data contract

**ID:** `L3-V09-paper` · ~10:30

### Сцена 1 · Как описать механизм (0:00–2:00)
**[ГОЛОС]** Параметры preprocessing обосновываются через генератор сигнала, полосы — через биологические осцилляторы, латентность ERP — через анатомический генератор. Discussion — интерпретация через механизм. Limitations — volume conduction, depth sensitivity, nonstationarity.

### Сцена 2 · ❌ Наивный paper (2:00–4:00)
**[ВИЗУАЛ]** «We used MNE-Python with default parameters. Bandpass 1–40 Hz. P-values < 0.05.» Без обоснования.

### Сцена 3 · ✅ Правильный paper-pipeline (4:00–8:30)
**[ВИЗУАЛ]**
```
[reproducible_figures.py] → [methods_paragraph via data_contract]
  → [results + CIs + effect_sizes] → [discussion via mechanism]
  → [Nimbus model card 1 page] → [quarto/LaTeX render]
```
**[ГОЛОС]** Каждая цифра — со ссылкой на формулу/скрипт; model card на 1 странице — must.

### Сцена 4 · Сравнение + журнал (8:30–10:30)
**[ГОЛОС]** Журнал: «Рецензент-нейрофизиолог оценит обоснование через механизм».

---

# ВИДЕО 3.10 · Neurofeedback · Пластичность

**ID:** `L3-V10-nf` · ~9:30

### Сцена 1 · Механизм пластичности (0:00–2:00)
**[ГОЛОС]** Operant conditioning через дофамин; Hebbian — «fire together, wire together»; LTP требует повторений → NF медленный. SMR и моторный контроль. Maladaptive plasticity — реальный риск.

### Сцена 2 · ❌ Наивный NF (2:00–4:00)
**[ВИЗУАЛ]**
```
[live signal] → [любая полоса] → [reward random schedule]
  → [нет safety, нет outcome]
```
Ошибки: цель без обоснования; reward не привязан к LTP-окну; нет safety thresholds; нет behavioral outcome.

### Сцена 3 · ✅ Правильный NF-протокол (4:00–7:30)
**[ВИЗУАЛ]**
```
[target_marker: SMR/alpha с обоснованием] → [online_estimator (LSL+Nimbus)]
  → [reward delivery visual/auditory + schedule]
  → [safety_thresholds + abort_policy]
  → [pre/post: behavioral + EEG Nimbus comparison report]
```

### Сцена 4 · Сравнение + журнал (7:30–9:30)
**[ГОЛОС]** Журнал: «NF-протокол должен опираться на механизм пластичности».

---

# ВИДЕО 3.CAP · Capstone L3 — Mini-paper + reproducible spec

**ID:** `L3-VCAP` · ~12:00

### Сцена 1 · Задача (0:00–1:00)
**[ГОЛОС]** Собрать research-pipeline от preregistration до mini-paper. Защита: каждый параметр — через механизм.

### Сцена 2 · ❌ «Notebook-paper» (1:00–4:00)
Ноутбук без BIDS, без model card, p < 0.05 без cluster, Methods «we used default».

### Сцена 3 · ✅ Эталонный capstone (4:00–9:00)
**[ВИЗУАЛ]**
```
[preregistration.md] → [BIDS dataset] → [Studio export + repro bundle]
  → [analysis: ERP/TF/MVPA + cluster-stats] → [Nimbus model + card]
  → [mini-paper 4-6 p] → [audit log]
```

### Сцена 4 · Сравнение + защита (9:00–12:00)
**[ГОЛОС]** Чаще всего пропускают *cluster-based permutation* и *anatomical caveats* connectivity — это превращает paper в коррелят без интерпретации.

---

# BATCH-ЗАПРОС К COLOSSYAN (Level 3)

```text
ПРОЕКТ: Nimbus Academy — Level 3 Researcher (12 видео)

РОЛЬ ИИ: создай РОВНО 12 отдельных видео по спецификации ниже.

ОБЩИЕ ТРЕБОВАНИЯ:
- Русский язык, subtitles RU burned-in.
- Аватар: исследователь-нейроинженер 35–45 лет, академический тон.
- Фон тёмно-синий; слева — анатомическая схема (мозг, BA-области, нейронные сети); справа — Nimbus Studio граф.
- Каждый ролик: (A) нейрофизиология 1.5–2.5 мин, (B) ❌ наивный пайплайн, (C) ✅ правильный с Studio + NimbusSDK, (D) таблица сравнения, (E) строка журнала.
- ❌ — красная рамка узлов, ✅ — зелёная.
- Визуал: ERP, TF map, source maps, RDM, dashboards. Без stock-видео.
- Логотип Nimbus Academy.

СПИСОК ВИДЕО:
1) L3-V00 | «Level 3 — Обзор» | 5:30 | от feature к paper; preregistration → mini-paper.
2) L3-V01 | «3.1 Design + preregistration» | 9:30 | oddball, Flanker, N-back, power; ❌ HARK/p-hack; ✅ OSF preregistration + planned analysis.
3) L3-V02 | «3.2 ERP углублённо» | 10 мин | N100/P200/N200/P300/N400/P600/CNV; ❌ peak by convenience; ✅ window-from-anatomy + bootstrap + NimbusQDA.
4) L3-V03 | «3.3 Time-frequency» | 10 мин | PING γ, θ-γ coupling, α inhibition; ❌ STFT one-window; ✅ Morlet+ERD/ERS+biological bands.
5) L3-V04 | «3.4 Connectivity» | 10 мин | DMN/Salience/ECN, axonal delays; ❌ sensor-level coherence; ✅ wPLI+graph+permutation+source.
6) L3-V05 | «3.5 Source localization» | 9:45 | Brodmann, gyri, deep sources; ❌ single dSPM; ✅ BEM/fsaverage + inverse compare + dipole fit.
7) L3-V06 | «3.6 MVPA + RSA» | 10:15 | population codes, manifold; ❌ random CV; ✅ subject-split + temporal generalization + RSA.
8) L3-V07 | «3.7 Statistics + sweep» | 9:30 | autocorrelation = biology; ❌ Bonferroni per channel; ✅ cluster-permutation + benchmark matrix.
9) L3-V08 | «3.8 Reproducibility» | 9 мин | bio-variability, state-dependency; ❌ ad-hoc notebook; ✅ BIDS+Conda+Docker+audit.
10) L3-V09 | «3.9 Mini-paper» | 10:30 | Methods как механизм; ❌ «we used defaults»; ✅ methods via data_contract + model card.
11) L3-V10 | «3.10 Neurofeedback» | 9:30 | Hebbian/LTP, dopamine; ❌ random reward; ✅ target marker + online estimator + safety + pre/post.
12) L3-VCAP | «Capstone L3 mini-paper» | 12 мин | preregistration → BIDS → analysis → Nimbus card → paper.

ФОРМАТ: для каждого ID отдельная сцена 8–14 shots, on-screen ≤12 слов, thumbnail = ID + название. Экспорт 1080p, файлы L3-V00.mp4 … L3-VCAP.mp4. Плейлист «Nimbus L3».
```
