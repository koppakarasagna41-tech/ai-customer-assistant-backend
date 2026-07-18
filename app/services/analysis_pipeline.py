import asyncio
import logging
from typing import Any, cast

from app.schemas.classification import ClassificationResponse
from app.schemas.entities import ExtractedEntities
from app.schemas.escalation import EscalationResponse
from app.schemas.intent import IntentResponse
from app.schemas.sentiment import SentimentResponse

from app.services.analysis_cache import AnalysisCache, get_analysis_cache
from app.services.classification_service import ClassificationService, get_classification_service
from app.services.confidence_service import ConfidenceService, get_confidence_service
from app.services.entity_extractor import EntityExtractor, get_entity_extractor
from app.services.escalation_service import EscalationService, get_escalation_service
from app.services.intent_service import IntentService, get_intent_service
from app.services.language_detector import LanguageDetector, get_language_detector
from app.services.message_normalizer import MessageNormalizer, get_message_normalizer
from app.services.risk_engine import RiskEngine, get_risk_engine
from app.services.sentiment_service import SentimentService, get_sentiment_service
from app.services.urgency_predictor import UrgencyPredictor, get_urgency_predictor

logger = logging.getLogger("app.services.analysis_pipeline")


class AnalysisPipeline:
    def __init__(
        self,
        normalizer: MessageNormalizer = None,
        lang_detector: LanguageDetector = None,
        entity_extractor: EntityExtractor = None,
        intent_service: IntentService = None,
        classification_service: ClassificationService = None,
        sentiment_service: SentimentService = None,
        escalation_service: EscalationService = None,
        urgency_predictor: UrgencyPredictor = None,
        risk_engine: RiskEngine = None,
        confidence_service: ConfidenceService = None,
        cache: AnalysisCache = None,
    ):
        self.normalizer = normalizer or get_message_normalizer()
        self.lang_detector = lang_detector or get_language_detector()
        self.entity_extractor = entity_extractor or get_entity_extractor()
        self.intent_service = intent_service or get_intent_service()
        self.classification_service = classification_service or get_classification_service()
        self.sentiment_service = sentiment_service or get_sentiment_service()
        self.escalation_service = escalation_service or get_escalation_service()
        self.urgency_predictor = urgency_predictor or get_urgency_predictor()
        self.risk_engine = risk_engine or get_risk_engine()
        self.confidence_service = confidence_service or get_confidence_service()
        self.cache = cache or get_analysis_cache()

    async def analyze(self, text: str) -> dict[str, Any]:
        if not text:
            return {}

        # Check cache
        cached_result = self.cache.get(text)
        if cached_result:
            logger.info("Retrieved analysis results from cache.")
            return cached_result

        # --- STAGE 1: INPUT OPTIMIZATION & PREPARATION ---
        # 1. Normalize
        normalized_text = self.normalizer.normalize(text)
        # 2. Detect language
        language = self.lang_detector.detect_language(normalized_text)
        # 3. Detect message type
        message_type = self.normalizer.detect_message_type(normalized_text)

        # 4. Extract entities (Async / LLM)
        entity_task = asyncio.create_task(self.entity_extractor.extract_entities(normalized_text))

        # --- STAGE 2: PARALLEL EXECUTION OF PRIMARY LLM TASKS ---
        intent_task = asyncio.create_task(self.intent_service.detect_intent(normalized_text))
        classification_task = asyncio.create_task(
            self.classification_service.classify_ticket(normalized_text)
        )
        sentiment_task = asyncio.create_task(
            self.sentiment_service.analyze_sentiment(normalized_text)
        )
        escalation_task = asyncio.create_task(
            self.escalation_service.assess_escalation(normalized_text)
        )

        # Wait for all LLM-powered tasks to finish concurrently
        entities_res, intent_res, classification_res, sentiment_res, escalation_res = (
            await asyncio.gather(
                entity_task,
                intent_task,
                classification_task,
                sentiment_task,
                escalation_task,
                return_exceptions=True,
            )
        )

        # Handle exceptions gracefully
        if isinstance(entities_res, Exception):
            logger.error(f"Error extracting entities: {entities_res}")
            from app.schemas.entities import ExtractedEntities

            entities_res = ExtractedEntities(entities=[])

        if isinstance(intent_res, Exception):
            logger.error(f"Error detecting intent: {intent_res}")
            from app.schemas.intent import IntentDetail, IntentResponse

            intent_res = IntentResponse(
                intents=[IntentDetail(intent="general_inquiry", confidence=0.5)]
            )

        if isinstance(classification_res, Exception):
            logger.error(f"Error classifying ticket: {classification_res}")
            from app.schemas.classification import ClassificationDetail, ClassificationResponse

            classification_res = ClassificationResponse(
                classifications=[ClassificationDetail(category="TECHNICAL", confidence=0.5)]
            )

        if isinstance(sentiment_res, Exception):
            logger.error(f"Error analyzing sentiment: {sentiment_res}")
            from app.schemas.sentiment import SentimentDetail, SentimentResponse

            sentiment_res = SentimentResponse(
                sentiment=SentimentDetail(label="neutral", score=0.5), escalation_recommended=False
            )

        if isinstance(escalation_res, Exception):
            logger.error(f"Error assessing escalation: {escalation_res}")
            from app.schemas.escalation import EscalationResponse

            escalation_res = EscalationResponse(
                escalation_score=0.0, escalation_recommended=False, reasons=[]
            )

        # ``gather(return_exceptions=True)`` returns exception unions.  The
        # fallback branches above guarantee concrete responses from this point.
        entities_res = cast(ExtractedEntities, entities_res)
        intent_res = cast(IntentResponse, intent_res)
        classification_res = cast(ClassificationResponse, classification_res)
        sentiment_res = cast(SentimentResponse, sentiment_res)
        escalation_res = cast(EscalationResponse, escalation_res)

        # Extract primary values for downstream reasoning
        primary_intent = intent_res.intents[0] if intent_res.intents else None
        primary_class = (
            classification_res.classifications[0] if classification_res.classifications else None
        )
        sentiment_score = sentiment_res.sentiment.score if sentiment_res.sentiment else 0.5
        escalation_score = escalation_res.escalation_score if escalation_res else 0.0

        # --- DYNAMIC REASONING & OPTIMIZATION (LOCAL) ---
        # 5. Predict Urgency
        urgency_res = self.urgency_predictor.predict_urgency(
            normalized_text,
            sentiment_score=sentiment_score if sentiment_res.sentiment.label == "negative" else 0.5,
        )

        # 6. Assess Risks
        risk_res = self.risk_engine.assess_risk(normalized_text, escalation_score=escalation_score)

        # 7. Overall Confidence Calculation
        scores_to_average = []
        if primary_intent:
            scores_to_average.append(primary_intent.confidence)
        if primary_class:
            scores_to_average.append(primary_class.confidence)
        if sentiment_res.sentiment:
            scores_to_average.append(0.9)  # Neutral baseline confidence for sentiment label
        if entities_res.entities:
            scores_to_average.extend([e.confidence for e in entities_res.entities])

        confidence_res = self.confidence_service.calculate_overall_confidence(scores_to_average)

        # 8. Formulate Response Recommendation
        recommendations = self.generate_recommendations(
            intent=primary_intent.intent if primary_intent else "general_inquiry",
            category=primary_class.category if primary_class else "TECHNICAL",
            urgency=urgency_res["level"],
            risk_level=risk_res["level"],
        )

        result = {
            "normalization": {
                "original": text,
                "normalized": normalized_text,
                "language": language,
                "message_type": message_type,
            },
            "intent": intent_res.model_dump(),
            "classification": classification_res.model_dump(),
            "sentiment": sentiment_res.model_dump(),
            "escalation": escalation_res.model_dump(),
            "entities": entities_res.model_dump(),
            "urgency": urgency_res,
            "risk": risk_res,
            "confidence": confidence_res.model_dump(),
            "recommendations": recommendations,
        }

        # Cache result
        self.cache.set(text, result)
        return result

    def generate_recommendations(
        self, intent: str, category: str, urgency: str, risk_level: str
    ) -> list[str]:
        recs = []
        if urgency == "high" or risk_level in ["HIGH", "CRITICAL"]:
            recs.append("IMMEDIATE: Route ticket to Senior Engineering / Support Manager.")
            recs.append("Alert Account Executive of operational risk.")

        if category == "BILLING":
            recs.append("Retrieve billing logs and transaction history.")
            recs.append("Verify payment portal status and invoice availability.")
        elif category == "TECHNICAL":
            recs.append("Retrieve server logs or error stack traces if provided.")
            recs.append("Check active system status pages for ongoing service disruptions.")

        if intent == "refund_request":
            recs.append("Review refund policy guidelines for current client tier.")
        elif intent == "account_access":
            recs.append("Generate secure, temporary password-reset token.")

        recs.append("Draft customized customer acknowledgment with estimated resolution time.")
        return recs


def get_analysis_pipeline() -> AnalysisPipeline:
    return AnalysisPipeline()
