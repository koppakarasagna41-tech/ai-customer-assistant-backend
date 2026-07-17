from app.services.cache_service import CacheService
from app.services.health_monitor import HealthMonitorService
from app.services.urgency_predictor import UrgencyPredictor


def test_urgency_predictor_critical():
    predictor = UrgencyPredictor()
    result = predictor.predict_urgency("PROD IS DOWN ASAP PLEASE HELP", sentiment_score=0.9)
    assert result["level"] == "high"
    assert result["score"] >= 0.7


def test_urgency_predictor_low():
    predictor = UrgencyPredictor()
    result = predictor.predict_urgency("how to check subscription details?", sentiment_score=0.5)
    assert result["level"] == "low"
    assert result["score"] < 0.35


def test_cache_service_set_get():
    cache = CacheService()
    cache.set("my-test-key", {"foo": "bar"}, ttl_seconds=10)
    assert cache.get("my-test-key") == {"foo": "bar"}


def test_cache_service_delete():
    cache = CacheService()
    cache.set("delete-key", "some-value")
    cache.delete("delete-key")
    assert cache.get("delete-key") is None


def test_cache_service_clear():
    cache = CacheService()
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    cache.clear()
    assert cache.get("k1") is None
    assert cache.get("k2") is None


def test_health_monitor_service():
    monitor = HealthMonitorService()
    initial_metrics = monitor.get_health_metrics()

    # Record a success
    monitor.record_request(response_time_ms=150.0, is_error=False)
    metrics_after_success = monitor.get_health_metrics()
    assert metrics_after_success["total_requests"] == initial_metrics["total_requests"] + 1

    # Record an error
    monitor.record_request(response_time_ms=500.0, is_error=True)
    metrics_after_error = monitor.get_health_metrics()
    assert metrics_after_error["total_requests"] == initial_metrics["total_requests"] + 2
