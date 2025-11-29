#!/usr/bin/env python3
"""
Модуль для оценки научных гипотез по ключевым эпистемологическим критериям.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from statistics import mean
from typing import Dict, List, Optional, Sequence


@dataclass
class PropertyScore:
    """Баллы по отдельному критерию."""

    name: str
    score: float
    rationale: str
    max_score: float = field(default=1.0)

    def as_percentage(self) -> int:
        """Возвращает значение критерия в процентах."""
        return int(round((self.score / self.max_score) * 100))


@dataclass
class HypothesisEvaluation:
    """Итоговая оценка гипотезы."""

    overall_score: float
    property_scores: List[PropertyScore]

    def as_percentage(self) -> int:
        """Возвращает итоговую оценку в процентах."""
        return int(round(self.overall_score * 100))


class HypothesisEvaluator:
    """
    Правила подсчёта баллов по критериям:

    1. Универсальность — охват известных случаев и ссылок на прошлый опыт.
    2. Новизна — наличие расширяющих/новых утверждений и уникальных элементов.
    3. Простота — лаконичность формулировок и средняя длина предложений.
    4. Плодотворность — наличие предсказаний и сценариев будущих проверок.
    5. Проверяемость — чёткость тестов, экспериментов и условий фальсификации.

    Параметр `context` (необязателен) может содержать:
    {
        "historical_cases": Sequence[str],
        "novel_findings": Sequence[str],
        "predictions": Sequence[str],
        "test_plan": Sequence[str]
    }
    """

    UNIVERSALITY_KEYWORDS = [
        "различн", "широк", "многочисл", "во всех", "прошл", "истор", "ранее", "большинств"
    ]
    NOVELTY_KEYWORDS = [
        "нов", "впервые", "расшир", "оригин", "неизвест", "дополн", "инновац"
    ]
    PREDICTIVE_KEYWORDS = [
        "предска", "прогноз", "будущ", "если", "то", "приведет", "ожида", "покажет"
    ]
    TESTABLE_KEYWORDS = [
        "провер", "эксперимент", "тест", "измер", "наблюд", "контроль", "фальсифиц", "услов"
    ]

    def evaluate(
        self,
        hypothesis: str,
        context: Optional[Dict[str, Sequence[str]]] = None,
    ) -> HypothesisEvaluation:
        """
        Возвращает оценку гипотезы по пяти критериям.

        :param hypothesis: Текст гипотезы.
        :param context: Дополнительные сведения (исторические кейсы, предсказания и т.д.).
        """
        cleaned = (hypothesis or "").strip()
        if not cleaned:
            raise ValueError("Текст гипотезы не должен быть пустым.")

        context = context or {}
        normalized = cleaned.lower()
        tokens = re.findall(r"\w+", normalized, flags=re.UNICODE)
        sentences = [s.strip() for s in re.split(r"[.!?]+", cleaned) if s.strip()]

        universality = self._score_universality(normalized, context)
        novelty = self._score_novelty(normalized, context)
        simplicity = self._score_simplicity(sentences, tokens)
        predictive = self._score_predictive(normalized, context)
        testable = self._score_testable(normalized, context)

        property_scores = [universality, novelty, simplicity, predictive, testable]
        overall = mean(score.score for score in property_scores)

        return HypothesisEvaluation(overall_score=overall, property_scores=property_scores)

    def _score_universality(
        self,
        normalized_text: str,
        context: Dict[str, Sequence[str]],
    ) -> PropertyScore:
        keyword_hits = self._count_keywords(normalized_text, self.UNIVERSALITY_KEYWORDS)
        historical_cases = context.get("historical_cases") or []

        score = min(1.0, keyword_hits * 0.15 + min(0.45, len(historical_cases) * 0.15))
        rationale_parts = [
            f"упоминаний охвата прошлых случаев: {keyword_hits}",
        ]
        if historical_cases:
            rationale_parts.append(
                f"реальных кейсов из прошлого: {len(historical_cases)}"
            )
        else:
            rationale_parts.append("исторические примеры не указаны")

        return PropertyScore(
            name="Универсальность",
            score=round(score, 2),
            rationale=", ".join(rationale_parts),
        )

    def _score_novelty(
        self,
        normalized_text: str,
        context: Dict[str, Sequence[str]],
    ) -> PropertyScore:
        keyword_hits = self._count_keywords(normalized_text, self.NOVELTY_KEYWORDS)
        novel_findings = context.get("novel_findings") or []

        score = min(1.0, keyword_hits * 0.18 + min(0.5, len(novel_findings) * 0.2))
        rationale_parts = [f"сигналов новизны: {keyword_hits}"]
        if novel_findings:
            rationale_parts.append(f"новых элементов в контексте: {len(novel_findings)}")
        else:
            rationale_parts.append("новые элементы не перечислены")

        return PropertyScore(
            name="Расширяющая/новая",
            score=round(score, 2),
            rationale=", ".join(rationale_parts),
        )

    def _score_simplicity(
        self,
        sentences: Sequence[str],
        tokens: Sequence[str],
    ) -> PropertyScore:
        if sentences:
            avg_len = mean(len(sentence.split()) for sentence in sentences)
        else:
            avg_len = len(tokens)

        clause_penalty = min(0.3, max(0, len(tokens) - len(sentences) * 20) * 0.005)

        if avg_len <= 15:
            base = 1.0
        elif avg_len <= 22:
            base = 0.85
        elif avg_len <= 30:
            base = 0.65
        elif avg_len <= 40:
            base = 0.45
        else:
            base = 0.25

        score = max(0.1, round(base - clause_penalty, 2))
        rationale = (
            f"средняя длина предложения {avg_len:.1f} слов, "
            f"штраф за сложность {clause_penalty:.2f}"
        )

        return PropertyScore(
            name="Простота/лаконичность",
            score=score,
            rationale=rationale,
        )

    def _score_predictive(
        self,
        normalized_text: str,
        context: Dict[str, Sequence[str]],
    ) -> PropertyScore:
        keyword_hits = self._count_keywords(normalized_text, self.PREDICTIVE_KEYWORDS)
        predictions = context.get("predictions") or []

        score = min(1.0, keyword_hits * 0.15 + min(0.55, len(predictions) * 0.18))
        rationale_parts = [f"упоминаний предсказаний: {keyword_hits}"]
        if predictions:
            rationale_parts.append(f"формализованных прогнозов: {len(predictions)}")
        else:
            rationale_parts.append("конкретные прогнозы не указаны")

        return PropertyScore(
            name="Плодотворность/предсказательность",
            score=round(score, 2),
            rationale=", ".join(rationale_parts),
        )

    def _score_testable(
        self,
        normalized_text: str,
        context: Dict[str, Sequence[str]],
    ) -> PropertyScore:
        keyword_hits = self._count_keywords(normalized_text, self.TESTABLE_KEYWORDS)
        tests = context.get("test_plan") or []

        score = min(1.0, keyword_hits * 0.15 + min(0.6, len(tests) * 0.25))
        rationale_parts = [f"упоминаний проверяемости: {keyword_hits}"]
        if tests:
            rationale_parts.append(f"описанных тестов: {len(tests)}")
        else:
            rationale_parts.append("планы проверки отсутствуют")

        return PropertyScore(
            name="Проверяемость/фальсифицируемость",
            score=round(score, 2),
            rationale=", ".join(rationale_parts),
        )

    @staticmethod
    def _count_keywords(text: str, stems: Sequence[str]) -> int:
        """Подсчитывает количество вхождений заданных стемов."""
        total = 0
        for stem in stems:
            pattern = re.compile(rf"{re.escape(stem)}\w*", flags=re.IGNORECASE | re.UNICODE)
            total += len(pattern.findall(text))
        return total
