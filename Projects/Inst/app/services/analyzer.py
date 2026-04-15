from __future__ import annotations

from dataclasses import dataclass
import re


CTA_PATTERNS = [
    r"\bподпиш[а-я]*\b",
    r"\bпиши\b",
    r"\bнапиши\b",
    r"\bсохрани\b",
    r"\bкоммент\b",
    r"\bпереходи\b",
    r"\bссылка в био\b",
    r"\bжми\b",
    r"\bотправь\b",
]

POSITIVE_PATTERNS = [r"\bкруто\b", r"\bсупер\b", r"\bкласс\b", r"\bполезно\b", r"\bспасибо\b", r"\bогонь\b"]
NEGATIVE_PATTERNS = [r"\bфигня\b", r"\bбред\b", r"\bне работает\b", r"\bплохо\b", r"\bдорого\b"]
QUESTION_PATTERNS = [r"\?", r"\bкак\b", r"\bгде\b", r"\bсколько\b", r"\bпочему\b"]


@dataclass
class AnalysisResult:
    hook_score: int
    hook_rationale: str
    retention_score: int
    retention_rationale: str
    transfer_score: int
    transfer_rationale: str
    confidence_score: int
    cta_detected: bool
    cta_type: str
    audience_reaction: dict
    actionable_recommendations: list[str]
    engagement_rate: float
    engagement_rate_by_views: float
    engagement_rate_proxy: float
    engagement_basis: str


def _matches_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def analyze_payload(caption: str, likes: int, comments_count: int, views: int, comments: list[dict]) -> AnalysisResult:
    caption = caption or ""
    caption_len = len(caption.strip())

    cta_detected = _matches_any(caption, CTA_PATTERNS)
    cta_type = "явный" if cta_detected else "неявный/отсутствует"

    hook_score = 4
    hook_reasons = []
    if caption_len >= 80:
        hook_score += 1
        hook_reasons.append("есть содержательный старт текста")
    if re.search(r"[!?]", caption[:120]):
        hook_score += 2
        hook_reasons.append("в начале есть эмоциональный триггер")
    if re.search(r"\b(ошибка|секрет|как|почему|никогда|всегда)\b", caption.lower()):
        hook_score += 2
        hook_reasons.append("используются триггерные слова")
    hook_score = min(hook_score, 10)
    if not hook_reasons:
        hook_reasons.append("хук выражен слабо, стоит усилить первые 1-2 фразы")

    retention_score = 4
    retention_reasons = []
    paragraphs = [p.strip() for p in caption.split("\n") if p.strip()]
    if len(paragraphs) >= 3:
        retention_score += 2
        retention_reasons.append("контент структурирован на несколько смысловых блоков")
    if len(caption.split()) >= 40:
        retention_score += 2
        retention_reasons.append("есть объем для удержания внимания")
    if views > 0 and likes > 0:
        engagement_by_views = likes / views
        if engagement_by_views >= 0.05:
            retention_score += 2
            retention_reasons.append("хорошее вовлечение по просмотрам")
    retention_score = min(retention_score, 10)
    if not retention_reasons:
        retention_reasons.append("удержание неочевидно, нужен более явный сценарий повествования")

    transfer_score = 3
    transfer_reasons = []
    if cta_detected:
        transfer_score += 3
        transfer_reasons.append("в тексте есть CTA")

    positive = 0
    negative = 0
    questions = 0
    for comment in comments:
        text = (comment.get("text") or "").lower()
        if _matches_any(text, POSITIVE_PATTERNS):
            positive += 1
        if _matches_any(text, NEGATIVE_PATTERNS):
            negative += 1
        if _matches_any(text, QUESTION_PATTERNS):
            questions += 1

    if questions > 0:
        transfer_score += 2
        transfer_reasons.append("аудитория задает вопросы, есть интерес к теме")
    if positive > negative and positive > 0:
        transfer_score += 2
        transfer_reasons.append("преобладает позитивный отклик на контент")
    transfer_score = min(transfer_score, 10)
    if not transfer_reasons:
        transfer_reasons.append("перелив выражен слабо, усилить CTA и путь к следующему шагу")

    total_interactions = likes + comments_count
    engagement_rate_by_views = (total_interactions / views * 100.0) if views else 0.0
    # Fallback proxy when views are unavailable from Instagram for this media.
    engagement_rate_proxy = 0.0
    if likes > 0 and comments_count > 0:
        # Convert comments-to-likes ratio to a bounded 0..100 score.
        comments_to_likes_pct = (comments_count / likes) * 100.0
        engagement_rate_proxy = min(100.0, comments_to_likes_pct * 20.0)
    elif likes > 0 and comments_count == 0:
        engagement_rate_proxy = 1.0
    engagement_rate = engagement_rate_by_views if views > 0 else engagement_rate_proxy
    engagement_basis = "views" if views > 0 else "comments_proxy"

    confidence = 45
    if caption_len > 0:
        confidence += 10
    if comments:
        confidence += 20
    if views > 0:
        confidence += 15
    confidence = min(confidence, 95)

    audience_reaction = {
        "positive_comments": positive,
        "negative_comments": negative,
        "questions_comments": questions,
        "comments_analyzed": len(comments),
    }

    recommendations = [
        "Добавить явный CTA в первых 2-3 строках и продублировать его в конце.",
        "Использовать микро-циклы удержания: вопрос -> короткий ответ -> следующий вопрос.",
        "Тестировать 2-3 варианта хука для одной темы и сравнивать отклик в комментариях.",
    ]

    return AnalysisResult(
        hook_score=hook_score,
        hook_rationale="; ".join(hook_reasons),
        retention_score=retention_score,
        retention_rationale="; ".join(retention_reasons),
        transfer_score=transfer_score,
        transfer_rationale="; ".join(transfer_reasons),
        confidence_score=confidence,
        cta_detected=cta_detected,
        cta_type=cta_type,
        audience_reaction=audience_reaction,
        actionable_recommendations=recommendations,
        engagement_rate=engagement_rate,
        engagement_rate_by_views=engagement_rate_by_views,
        engagement_rate_proxy=engagement_rate_proxy,
        engagement_basis=engagement_basis,
    )
