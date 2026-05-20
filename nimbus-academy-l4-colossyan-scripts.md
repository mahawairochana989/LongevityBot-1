# Nimbus Academy · Level 4 — Сценарии видео для Colossyan

**Уровень:** Specialist · 4 трека (Clinical / Cognitive / Product / Computational)  
**Видео в пакете:** 36 (4 трека × 8 уроков + 4 capstones)  
**Язык:** русский · ИИ-аватар + on-screen Nimbus Studio граф

> **Логика трека:** каждый из 8 уроков добавляет один шаг к capstone-пайплайну специализации. Все ролики держат единый шаблон: нейрофизиология → ❌ наивный пайплайн → ✅ правильный → таблица сравнения → строка журнала.

---

## Общие настройки для всех 36 роликов

| Параметр | Значение |
|---|---|
| Длительность | 7–9 мин на урок · 11–12 мин на capstone |
| Персона | Эксперт-специалист (clinical / cognitive / product / computational) — стиль меняется по треку |
| Темп | ~130 слов/мин |
| Субтитры | RU burned-in |
| ❌/✅ | Красная / зелёная рамка узлов |
| Брендинг | Nimbus Academy + код трека (4A / 4B / 4C / 4D) |

---

# ТРЕК A · CLINICAL

**Стиль аватара:** клиницист-нейрофизиолог, белый халат поверх рубашки. Фон: томограф/ЭЭГ-кабинет.

## L4A.1 · Патологические осцилляции · QC pipeline
**ID:** `L4A-V01` · ~8:00

**🧠 Нейрофизиология (0:00–2:00).** Эпилептический разряд — GABAergic failure. Иктальный vs интериктальный паттерн; spike-wave templates; антиэпилептики и их ЭЭГ-маркеры.

**❌ Наивный (2:00–3:30).** `[raw clinical] → [уровень 100 µV reject] → [Nimbus model]`. Ошибка: spike — *сигнал*, не артефакт; реджектится патология, остаётся фон.

**✅ Правильный (3:30–6:30).** 
```
[raw] → [clinical_QC_gate] → [spike-wave_template_match] → [pattern_keep_filter]
  → [risk_gating to model] → [report]
```

**📊 Сравнение + журнал (6:30–8:00).** Журнал: «Патологический паттерн нельзя отфильтровать как артефакт — это и есть сигнал интереса».

---

## L4A.2 · Seizure onset detection
**ID:** `L4A-V02` · ~8:30

**🧠 Нейрофизиология.** Spreading depolarization; onset zones; focal vs generalized; sentinel HFO-маркеры (80–250 Гц).

**❌ Наивный.** `[bandpass 1-40] → [global threshold] → [alarm]`. Ошибка: HFO теряются при cutoff 40 Гц; глобальный порог даёт высокий false positive rate.

**✅ Правильный.**
```
[wideband 0.5-300] → [sliding window 1s, hop 250ms]
  → [HFO band 80-250 + spike detector]
  → [confidence_policy very-low-FP] → [latency_budget online alert]
```

**Журнал:** «В клинике false positives дорогие — confidence threshold выводится из последствий ошибки».

---

## L4A.3 · Coma scoring · Complexity
**ID:** `L4A-V03` · ~8:00

**🧠 Нейрофизиология.** Global Neuronal Workspace; thalamocortical disconnection; Minimally Conscious State; Perturbational Complexity Index (PCI).

**❌ Наивный.** `[bandpower α/β only] → [single LDA]`. Игнор complexity; нет TMS-PCI; нет stage hierarchy.

**✅ Правильный.**
```
[clean] → [spectral_features per stage]
  → [LZ_complexity + PCI_proxy] → [NimbusQDA per coma stage]
  → [confidence calibration for clinical decision]
```

**Журнал:** «Сложность ЭЭГ — мера работы таламо-кортикальной сети».

---

## L4A.4 · Stroke recovery markers
**ID:** `L4A-V04` · ~8:00

**🧠 Нейрофизиология.** Periinfarct plasticity; диасхиз; cortical remapping; inter-hemispheric inhibition.

**❌ Наивный.** Сравнить одну запись пациента с нормой → «улучшение/ухудшение». Нет longitudinal; нет inter-hemispheric coherence.

**✅ Правильный.**
```
[longitudinal sessions] → [inter_hemispheric_coherence per band]
  → [NimbusSTS adaptive trajectory] → [recovery_marker_report]
```

**Журнал:** «Восстановление — это конкретный анатомический процесс ремаппинга, не метрика».

---

## L4A.5 · Sleep staging · AASM
**ID:** `L4A-V05` · ~8:30

**🧠 Нейрофизиология.** NREM/REM генераторы; sleep spindles (TRN + thalamic relay); slow oscillations и консолидация; K-complexes как cortical down-states.

**❌ Наивный.** `[any-window features] → [random forest 5-class]`. Без AASM-окон 30 с; без spindle/K detector.

**✅ Правильный.**
```
[30s_epochs AASM] → [spectral δ/θ/σ/β + spindle_detector + K_detector]
  → [NimbusSoftmax 5-class] → [transition_constraints HMM]
  → [agreement-with-scorer report]
```

**Журнал:** «AASM-стадии — договор о физиологии, не классы данных».

---

## L4A.6 · Pediatric pipeline · Возрастная нормализация
**ID:** `L4A-V06` · ~8:00

**🧠 Нейрофизиология.** Миелинизация и её ЭЭГ-маркеры; созревание α 4→8→10 Гц; sensitive periods.

**❌ Наивный.** Адультные нормы → ребёнок «всегда аномален».

**✅ Правильный.**
```
[features] → [age_adjusted_norm: percentile curves per age]
  → [deviation_score] → [Nimbus output as z-against-age]
```

**Журнал:** «"Нормальная" ЭЭГ зависит от возраста; модель учитывает это в самом контракте».

---

## L4A.7 · Biomarker validation · FDA-style
**ID:** `L4A-V07` · ~8:00

**🧠 Нейрофизиология.** Biomarker qualification; construct/criterion/predictive validity; surrogate vs true endpoint.

**❌ Наивный.** Высокая accuracy → «биомаркер». Без construct validity, без regulatory rationale.

**✅ Правильный.**
```
[biomarker_candidate] → [validity_battery: construct/criterion/predictive]
  → [clinical_grade_thresholds] → [regulatory_rationale in model_card]
  → [validation_pack: report + data + code + audit]
```

**Журнал:** «Биомаркер обязан иметь биологическое обоснование, иначе не пройдёт регуляторно».

---

## L4A.8 · Clinical capstone defense
**ID:** `L4A-V08` · ~9:00

**🧠 Дифференциальный диагноз через ЭЭГ-механизм; failure modes в патофизиологических терминах.**

**❌ vs ✅.** Изолированные ноутбуки vs единый pipeline: QC gate → pattern → markers → adaptive recovery → AASM → biomarker validation → deployment plan + регуляторный rationale.

**Журнал:** «Защита клиника — это связное patho-обоснование на одной странице».

---

## L4A-VCAP · Clinical capstone integration
**ID:** `L4A-VCAP` · ~12:00

Интеграция шагов A.1–A.7 в один Studio граф + risk log + FDA rationale + clinical reviewer defense.

---

# ТРЕК B · COGNITIVE

**Стиль аватара:** когнитивный нейрофизиолог, в свитере, фон лаборатории. Темп чуть быстрее.

## L4B.1 · Attention · Alpha lateralization
**ID:** `L4B-V01` · ~7:30

**🧠 Нейрофизиология.** Dorsal vs ventral attention network; top-down vs bottom-up; TMS causality; alpha lateralization как маркер.

**❌ Наивный.** `[parietal alpha mean] → [LDA]`. Без cued paradigm; без latералize index.

**✅ Правильный.**
```
[cued_attention paradigm] → [TF map per hemisphere]
  → [LI = (R-L)/(R+L) alpha] → [NimbusLDA on TF features]
```

**Журнал:** «Alpha lateralization — анатомически осмысленный маркер, не частотный bin».

---

## L4B.2 · Working memory · Frontal theta
**ID:** `L4B-V02` · ~8:00

**🧠 Нейрофизиология.** Persistent firing PFC; gamma-burst модель; capacity via interference; frontal theta при load.

**❌ Наивный.** `[parietal alpha only] → [бинарный load/no-load]`. Игнорирует frontal theta и градацию.

**✅ Правильный.**
```
[n-back paradigm] → [frontal_theta + parietal_alpha features]
  → [NimbusSoftmax 4-class load levels] → [reliability per subject]
```

**Журнал:** «Frontal theta — прямой коррелят PFC persistent firing».

---

## L4B.3 · Decision · FRN / reward
**ID:** `L4B-V03` · ~7:45

**🧠 Нейрофизиология.** DLPFC weighing reward; insula risk; dopamine prediction error; FRN ERP.

**❌ Наивный.** Mean amplitude window-by-convenience.

**✅ Правильный.**
```
[gambling_paradigm] → [FRN window 200-350ms]
  → [reward-coded epochs] → [NimbusQDA prediction_error]
  → [trial_wise_posterior]
```

**Журнал:** «FRN — конкретный коррелят dopaminergic prediction error».

---

## L4B.4 · Language · N400 / P600
**ID:** `L4B-V04` · ~8:00

**🧠 Нейрофизиология.** Dual-stream dorsal/ventral; Broca переосмыслен; N400 семантика; P600 синтаксис.

**❌ Наивный.** Одна ERP window на оба эффекта.

**✅ Правильный.**
```
[semantic + syntactic violation paradigms] → [N400 + P600 windows]
  → [feature compare] → [NimbusQDA per task]
```

**Журнал:** «Разные окна — разные сети».

---

## L4B.5 · Emotion · Honest model card
**ID:** `L4B-V05` · ~7:30

**🧠 Нейрофизиология.** Frontal asymmetry valence; amygdala-ACC arousal; embodied emotion; ЭЭГ-пределы для дискретных эмоций.

**❌ Наивный.** Заявить «детектор happiness/sadness» на 4 классах с overfit.

**✅ Правильный.**
```
[FAA: frontal_alpha_asymmetry] + [HEP optional]
  → [arousal/valence proxy] → [honest_model_card with limits]
```

**Журнал:** «ЭЭГ детектирует arousal лучше дискретных эмоций — это честное ограничение».

---

## L4B.6 · MMN · Predictive coding
**ID:** `L4B-V06` · ~8:00

**🧠 Нейрофизиология.** Hierarchical predictive coding (Friston); precision = attention; MMN как prediction error.

**❌ Наивный.** Усреднить odd-standard и взять разницу.

**✅ Правильный.**
```
[oddball paradigm] → [trial_wise_PE_estimate]
  → [bayesian_Nimbus_model: posterior + confidence]
  → [test prediction-coding hierarchy]
```

**Журнал:** «MMN — прямой коррелят prediction error в иерархии».

---

## L4B.7 · Consciousness · NCC
**ID:** `L4B-V07` · ~8:00

**🧠 Нейрофизиология.** IIT, Global Workspace, P3b и access; perturbational complexity.

**❌ Наивный.** «ЭЭГ показывает сознание» без operationalization.

**✅ Правильный.**
```
[paradigm: aware vs unaware trials] → [P3b feature + LZ/PCI complexity]
  → [Nimbus classifier conscious_access] → [confound_log]
```

**Журнал:** «Сознание в ЭЭГ — операционализированные маркеры, не философия».

---

## L4B.8 · Cognitive capstone defense
**ID:** `L4B-V08` · ~9:00  
Связное обоснование маркера на 1 стр.; confound log; interpretability section в model card.

## L4B-VCAP · Cognitive integration
**ID:** `L4B-VCAP` · ~11:30  
Task → feature family → Nimbus → posterior → confound log → interpretability.

---

# ТРЕК C · PRODUCT

**Стиль аватара:** BCI-PM, hoodie + Notion на втором мониторе. Фон: open-space + prototype.

## L4C.1 · Workload monitor · θ/α ratio
**ID:** `L4C-V01` · ~7:30

**🧠 Нейрофизиология.** Mental workload; frontal theta + parietal alpha как ratio; subjective vs objective; limits сухих электродов.

**❌ Наивный.** Только bandpower α → бинарный «устал/нет».

**✅ Правильный.**
```
[dry_electrode_intake] → [frontal_theta + parietal_alpha]
  → [ratio_feature] → [NimbusLDA continuous score]
  → [UX-friendly latency budget < 250ms]
```

**Журнал:** «θ/α ratio — биологический proxy, не случайный признак».

---

## L4C.2 · Latency budget · JND + binding window
**ID:** `L4C-V02` · ~7:00

**🧠 Нейрофизиология.** JND visual / haptic / audio; temporal binding ~150 ms; embodiment.

**❌ Наивный.** «оптимизировать как сможем».

**✅ Правильный.**
```
[budget_spec.json: per_node_ms = 150 total]
  → [profiler_per_stage] → [compensation_strategies (prediction)]
  → [measurement_protocol] → [report]
```

**Журнал:** «JND — физиологическая константа, ограничивающая дизайн».

---

## L4C.3 · Sustained attention · Fatigue monitor
**ID:** `L4C-V03` · ~7:30

**🧠 Нейрофизиология.** Vigilance decrement; mind wandering markers; BCI fatigue causes.

**❌ Наивный.** Один threshold drowsiness.

**✅ Правильный.**
```
[long_session_intake] → [vigilance_features: α/θ/blink_rate]
  → [escalation_policy: warn / pause / abort]
  → [UI cues + fallback behavior]
```

**Журнал:** «Усталость — нейрофизиологическое ограничение продукта».

---

## L4C.4 · Real-world / motion robust
**ID:** `L4C-V04` · ~8:00

**🧠 Нейрофизиология.** Мозг в лаборатории vs в жизни; motion artifacts; dual-task; ambient noise.

**❌ Наивный.** Лабораторная модель → деплой на улице → крах.

**✅ Правильный.**
```
[lab + real-world dataset] → [motion-robust filter]
  → [domain_shift_diagnostic] → [degradation_curve]
  → [Nimbus retraining policy]
```

**Журнал:** «Ecological validity — разница, которая всегда стоит реальных денег».

---

## L4C.5 · Trust UX · Confidence visualization
**ID:** `L4C-V05` · ~7:00

**🧠 Нейрофизиология.** Anterior insula interoception; uncertainty → беспокойство; communication of confidence.

**❌ Наивный.** «100% уверенность» во всех ответах.

**✅ Правильный.**
```
[confidence_policy from L2.5] → [UX_mapping: badges / haptics / colors]
  → [user_testing_protocol] → [trust_metric NPS-like]
```

**Журнал:** «Доверие — продуктовое следствие правильно показанной uncertainty».

---

## L4C.6 · ErrP self-correction
**ID:** `L4C-V06` · ~8:00

**🧠 Нейрофизиология.** ACC performance monitoring; ErrP компонент; frustration → muscle tension; feedback timing.

**❌ Наивный.** Игнор ошибок → пользователь перестаёт пользоваться.

**✅ Правильный.**
```
[command issued] → [ErrP_window 200-500ms]
  → [NimbusLDA on ErrP] → [auto_correct or confirm prompt]
  → [closed_loop demo]
```

**Журнал:** «ErrP — встроенная коррекция от ACC; учитывая её, продукт самовосстанавливается».

---

## L4C.7 · Long-term plasticity-aware product
**ID:** `L4C-V07` · ~7:30

**🧠 Нейрофизиология.** Long-term BCI plasticity studies; skill transfer; adverse plasticity risk.

**❌ Наивный.** Static model годами → degradation.

**✅ Правильный.**
```
[longitudinal_NimbusSTS] → [user_progress_tracker]
  → [adaptation_policy spec] → [adverse_plasticity_safety_check]
```

**Журнал:** «Продукт учитывает, что пользователь меняется неделя за неделей».

---

## L4C.8 · Product capstone defense
**ID:** `L4C-V08` · ~9:00  
BrainFlow/LSL → real-time confidence + fallback → latency budget defended → decision memo.

## L4C-VCAP · Product integration
**ID:** `L4C-VCAP` · ~11:30  
Intake → workload → fatigue → ecological → trust UX → ErrP → longitudinal → deploy.

---

# ТРЕК D · COMPUTATIONAL

**Стиль аватара:** computational neuroscientist, на фоне whiteboard с уравнениями. Темп размеренный, академический.

## L4D.1 · Hodgkin-Huxley · Single-cell simulation
**ID:** `L4D-V01` · ~8:00

**🧠 Нейрофизиология.** Ионные каналы Na/K; потенциал действия; refractory period; cable equation.

**❌ Наивный.** Симуляция нейрона без PSP → нет моста к ЭЭГ.

**✅ Правильный.**
```
[HH_simulation: V(t), m,h,n] → [synaptic PSP integration]
  → [population sum → field potential]
  → [Nimbus feature: simulated PSD] → [compare to real]
```

**Журнал:** «Канал → спайк → PSP → field — физический мост к ЭЭГ».

---

## L4D.2 · Wilson-Cowan · Population dynamics
**ID:** `L4D-V02` · ~8:00

**🧠 Нейрофизиология.** Mean-field; E/I баланс; эмерджентные ритмы.

**❌ Наивный.** Сгенерировать sin-волну → «вот альфа».

**✅ Правильный.**
```
[WC equations: dE/dt, dI/dt] → [parameter sweep]
  → [emergent frequency response] → [match to real PSD]
  → [Nimbus feature from simulation]
```

**Журнал:** «Ритмы — эмерджентное свойство популяции, не "сгенерированный шум"».

---

## L4D.3 · Active inference · FEP toy
**ID:** `L4D-V03` · ~8:30

**🧠 Нейрофизиология.** Markov blankets; variational inference; FEP Friston.

**❌ Наивный.** Назвать любую классификацию «active inference».

**✅ Правильный.**
```
[generative_model + posterior beliefs]
  → [variational update] → [action selection minimizing F]
  → [map FEP → Nimbus Bayesian posterior]
```

**Журнал:** «Nimbus Bayesian — практическая инкарнация FEP».

---

## L4D.4 · Criticality · Avalanches
**ID:** `L4D-V04` · ~8:00

**🧠 Нейрофизиология.** Criticality; power laws; edge of chaos.

**❌ Наивный.** Любая выраженная гетерогенность → «critical».

**✅ Правильный.**
```
[neuronal_avalanche_detection] → [size/duration distributions]
  → [power_law_fit + KS_test] → [branching_parameter σ ≈ 1]
  → [healthy vs patho compare]
```

**Журнал:** «Критичность — proxy здоровья мозга, измеримый через ЭЭГ».

---

## L4D.5 · Fisher information
**ID:** `L4D-V05` · ~8:00

**🧠 Нейрофизиология.** Fisher info в нейронных кодах; efficient coding; tuning curves.

**❌ Наивный.** Считать accuracy «верхним пределом».

**✅ Правильный.**
```
[neural_features] → [estimate Fisher_info per stimulus]
  → [theoretical_decoding_bound] → [compare to MVPA accuracy]
```

**Журнал:** «Верхний предел decoding задаётся Fisher info, а не моделью».

---

## L4D.6 · Connectome · SC → FC
**ID:** `L4D-V06` · ~8:30

**🧠 Нейрофизиология.** Connectome; SC → FC mapping; hub regions; small-world.

**❌ Наивный.** Считать функциональные связи изолированно от структуры.

**✅ Правильный.**
```
[SC_matrix (DTI/template)] → [neural_mass_model на узлах]
  → [predicted_FC] → [compare to empirical EEG FC]
```

**Журнал:** «Функциональная связность ограничена структурной».

---

## L4D.7 · Theory comparison · Crucial experiments
**ID:** `L4D-V07` · ~8:30

**🧠 Нейрофизиология.** Falsifiability; конкурирующие теории; крицифические эксперименты.

**❌ Наивный.** «Наша модель fits the data» (любая).

**✅ Правильный.**
```
[2+ competing models] → [each predicts distinct features]
  → [Nimbus_inference selects which fits empirical] → [falsified vs surviving]
```

**Журнал:** «Модель решает спор только если выдаёт falsifiable predictions».

---

## L4D.8 · Computational capstone defense
**ID:** `L4D-V08` · ~9:00  
Полный chain: biophysics → population → ЭЭГ → Nimbus inference → verifiable prediction → experimental plan.

## L4D-VCAP · Computational integration
**ID:** `L4D-VCAP` · ~11:30  
Model assumption → simulated features → Nimbus inference → predictive test → experimental validation.

---

# CROSS-LEVEL CAPSTONE FINAL

**ID:** `L4-FINAL-DEFENSE` · ~10:00 (общее для всех 4 треков)

**Содержание:** студенты каждого трека защищают свой capstone перед коллегиями ревьюеров (clinical + cognitive + product + computational). Каждая защита включает: 1-страничное обоснование маркера через механизм, full Nimbus pipeline, risk/confound log, deployment plan.

---

# BATCH-ЗАПРОСЫ К COLOSSYAN (4 трека Level 4)

> Запустите 4 отдельных bulk-задания (по одному на трек). Каждое задание создаёт 9 видео = 8 уроков + capstone integration.

## BATCH 1 · Track A · Clinical (9 видео)

```text
ПРОЕКТ: Nimbus Academy — Level 4 Track A Clinical (9 видео)

РОЛЬ: создай РОВНО 9 видео.

ОБЩИЕ ТРЕБОВАНИЯ:
- Русский, субтитры RU burned-in.
- Аватар: клиницист-нейрофизиолог 40–55 лет, белый халат поверх рубашки, академический спокойный тон.
- Фон: ЭЭГ-кабинет / шапка для EEG в кадре; справа — Nimbus Studio граф с клиническим QC.
- Каждый ролик: (A) патофизиология 1.5–2 мин, (B) ❌ наивный пайплайн, (C) ✅ правильный с clinical QC + risk gating, (D) сравнение, (E) журнал.
- ❌ красная рамка узлов / ✅ зелёная.
- Визуал: spike-wave, sleep hypnogram, age curves, biomarker validation table.

СПИСОК:
1) L4A-V01 «Патологические осцилляции» 8:00 | GABAergic failure; ❌ amplitude reject 100µV; ✅ pattern-keep + clinical QC gate.
2) L4A-V02 «Seizure onset» 8:30 | HFO 80-250 Hz; ❌ bandpass 1-40 + global threshold; ✅ wideband + HFO + low-FP policy + latency budget.
3) L4A-V03 «Coma scoring» 8:00 | thalamocortical disconnection, PCI; ❌ bandpower only; ✅ LZ/PCI + NimbusQDA stages.
4) L4A-V04 «Stroke recovery» 8:00 | periinfarct plasticity; ❌ single-session; ✅ longitudinal inter-hem coherence + NimbusSTS.
5) L4A-V05 «Sleep staging AASM» 8:30 | spindles TRN, K-complex; ❌ random forest без AASM; ✅ 30s+spindle/K+Softmax+HMM.
6) L4A-V06 «Pediatric age-adjusted» 8:00 | миелинизация, α 4→10 Hz; ❌ adult norms; ✅ age percentile + deviation score.
7) L4A-V07 «Biomarker validation FDA» 8:00 | construct/criterion/predictive; ❌ accuracy alone; ✅ validity battery + regulatory rationale.
8) L4A-V08 «Clinical defense» 9:00 | дифференциальный диагноз через механизм; ❌ ноутбуки; ✅ единый pipeline + risk log.
9) L4A-VCAP «Clinical capstone integration» 12:00 | full QC→biomarker→deployment + FDA-style rationale.

ФОРМАТ: 8–14 shots/ID; on-screen ≤12 слов; 1080p; имена L4A-V01.mp4 … L4A-VCAP.mp4; плейлист «Nimbus L4-Clinical».
```

---

## BATCH 2 · Track B · Cognitive (9 видео)

```text
ПРОЕКТ: Nimbus Academy — Level 4 Track B Cognitive (9 видео)

РОЛЬ: 9 отдельных видео.

ОБЩИЕ ТРЕБОВАНИЯ:
- Русский RU burned-in.
- Аватар: когнитивный нейрофизиолог 35–45 лет, casual academic (свитер).
- Фон: лаборатория с PsychoPy/PsyToolkit, eye-tracker; справа — Nimbus Studio граф когнитивной парадигмы.
- Структура: нейрофизиология → ❌ → ✅ → сравнение → журнал.
- Визуал: attention networks, n-back, FRN ERPs, RDM, NCC plots.

СПИСОК:
1) L4B-V01 «Attention α-lateralization» 7:30 | dorsal/ventral; ❌ parietal α mean; ✅ LI + TF features + NimbusLDA.
2) L4B-V02 «Working memory θ» 8:00 | PFC persistent firing; ❌ α only; ✅ frontal θ + parietal α + Softmax 4-class.
3) L4B-V03 «Decision FRN» 7:45 | dopamine PE; ❌ peak by convenience; ✅ FRN 200-350ms + QDA trial-wise.
4) L4B-V04 «Language N400/P600» 8:00 | dual-stream; ❌ single window; ✅ two windows + two NimbusQDA.
5) L4B-V05 «Emotion FAA honest» 7:30 | frontal asymmetry, HEP; ❌ дискретные эмоции overfit; ✅ arousal/valence + honest model card.
6) L4B-V06 «MMN predictive coding» 8:00 | Friston; ❌ avg odd-standard; ✅ trial-wise PE + Bayesian Nimbus.
7) L4B-V07 «NCC consciousness» 8:00 | IIT, GW, PCI; ❌ философия; ✅ aware/unaware + P3b + complexity + confound log.
8) L4B-V08 «Cognitive defense» 9:00 | marker rationale 1pp + interpretability.
9) L4B-VCAP «Cognitive integration» 11:30 | task→feature→Nimbus→posterior→confounds→interpretability.

ФОРМАТ: 8–14 shots; 1080p; L4B-V01.mp4 … L4B-VCAP.mp4; плейлист «Nimbus L4-Cognitive».
```

---

## BATCH 3 · Track C · Product (9 видео)

```text
ПРОЕКТ: Nimbus Academy — Level 4 Track C Product (9 видео)

РОЛЬ: 9 отдельных видео.

ОБЩИЕ ТРЕБОВАНИЯ:
- Русский RU burned-in.
- Аватар: BCI-PM/UX engineer 30–40 лет, hoodie/casual, продуктовый тон.
- Фон: open-space с прототипами, прибор BCI dry-electrode на столе; справа — Nimbus Studio + Figma mockup.
- Структура та же: нейро → ❌ → ✅ → сравнение → журнал.
- Визуал: latency timeline, workload chart, trust UI mockups, ErrP closed-loop.

СПИСОК:
1) L4C-V01 «Workload θ/α» 7:30 | mental workload; ❌ α only; ✅ ratio + NimbusLDA + dry electrodes + UX budget.
2) L4C-V02 «Latency budget JND» 7:00 | binding 150ms; ❌ «оптимизируем»; ✅ per-node budget + profiler + compensation.
3) L4C-V03 «Sustained attention» 7:30 | vigilance decrement; ❌ one threshold; ✅ escalation policy + fallback.
4) L4C-V04 «Real-world robust» 8:00 | motion, dual-task; ❌ lab-only; ✅ domain-shift diag + degradation curve.
5) L4C-V05 «Trust UX» 7:00 | insula, uncertainty; ❌ 100% confidence; ✅ confidence policy → UX mapping + user testing.
6) L4C-V06 «ErrP self-correction» 8:00 | ACC monitoring; ❌ игнор ошибок; ✅ ErrP 200-500ms + LDA + closed loop.
7) L4C-V07 «Plasticity-aware product» 7:30 | long-term BCI plasticity; ❌ static model; ✅ longitudinal STS + safety check.
8) L4C-V08 «Product defense» 9:00 | LSL/BrainFlow + confidence + fallback + budget defended.
9) L4C-VCAP «Product integration» 11:30 | intake→workload→fatigue→eco→trust→ErrP→longitudinal→deploy.

ФОРМАТ: 8–14 shots; 1080p; L4C-V01.mp4 … L4C-VCAP.mp4; плейлист «Nimbus L4-Product».
```

---

## BATCH 4 · Track D · Computational (9 видео)

```text
ПРОЕКТ: Nimbus Academy — Level 4 Track D Computational (9 видео)

РОЛЬ: 9 отдельных видео.

ОБЩИЕ ТРЕБОВАНИЯ:
- Русский RU burned-in.
- Аватар: computational neuroscientist 35–50 лет, рубашка, тон академический.
- Фон: whiteboard с уравнениями (HH, WC, Bayes), справа — Nimbus Studio + jupyter notebook.
- Структура: нейро+теория → ❌ → ✅ → сравнение → журнал.
- Визуал: HH membrane plot, WC bifurcation, avalanche distribution, Fisher info curves, SC-FC matrices.

СПИСОК:
1) L4D-V01 «HH single-cell» 8:00 | Na/K каналы; ❌ нейрон без PSP; ✅ HH → PSP → field → Nimbus feature.
2) L4D-V02 «Wilson-Cowan» 8:00 | mean-field, E/I; ❌ sin = α; ✅ WC + emergent freq + PSD match.
3) L4D-V03 «Active inference FEP» 8:30 | Markov blankets, variational; ❌ ярлык «inference»; ✅ generative + variational + Nimbus Bayesian.
4) L4D-V04 «Criticality» 8:00 | power laws; ❌ heterogeneity = critical; ✅ avalanche + KS-test + branching σ.
5) L4D-V05 «Fisher info» 8:00 | efficient coding; ❌ accuracy ceiling; ✅ Fisher bound + MVPA compare.
6) L4D-V06 «Connectome SC→FC» 8:30 | DTI hubs; ❌ FC изолированно; ✅ neural-mass model on SC → predicted FC.
7) L4D-V07 «Theory comparison» 8:30 | falsifiability; ❌ «model fits»; ✅ 2 competing models + Nimbus inference + falsification.
8) L4D-V08 «Computational defense» 9:00 | full chain + experimental plan.
9) L4D-VCAP «Computational integration» 11:30 | model→simulation→Nimbus→predictive test→validation.

ФОРМАТ: 8–14 shots; 1080p; L4D-V01.mp4 … L4D-VCAP.mp4; плейлист «Nimbus L4-Computational».
```

---

## Сводный чеклист публикации Level 4

- [ ] 36 файлов: 9 × 4 = `L4A-V01.mp4 … L4D-VCAP.mp4`
- [ ] 4 плейлиста по трекам
- [ ] Каждый ролик связан в LMS с соответствующим интегрированным заданием Level 4
- [ ] Сабтайтлы проверены по специальной терминологии (HFO, PCI, FRN, FEP, HH, WC, SC-FC)
- [ ] Финальный кросс-уровневый capstone defense — отдельным роликом, объединяющим 4 трека

---

*Документ сгенерирован для Colossyan · Nimbus Academy Level 4 · TOC v1.0 (BBS-first)*
