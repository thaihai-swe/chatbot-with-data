"""Tests for ablation evaluation framework (TASK-004, TASK-005)."""
from __future__ import annotations

import json
import copy
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from schemas.settings import RetrievalSettings
from schemas.chat import (
    SanityCheckResponse,
    EvalResult,
    AblationComparisonResponse,
)
from chat.evaluation import EvaluationService
from config import get_settings_manager


def _make_mock_eval_result(case_id: str, passed: bool = True) -> EvalResult:
    return EvalResult(
        case_id=case_id,
        question="Test question",
        expected_document_id="doc-1",
        actual_answer="Test answer.",
        recall_status=passed,
        groundedness_score=0.85 if passed else 0.3,
        groundedness_reason="All good",
        citation_coverage=0.9 if passed else 0.2,
        latency_ms=100,
        passed=passed,
    )


class TestConfigDeepCopy:
    """AC-005: Config object must not be mutated by evaluation loop."""

    @pytest.mark.asyncio
    async def test_config_immutability_after_eval(self):
        original = RetrievalSettings(
            retrieval_mode="hybrid",
            dynamic_routing_enabled=True,
            query_expansion_enabled=False,
            hyde_enabled=False,
            reranker_enabled=True,
        )
        frozen_before = original.model_copy(deep=True)

        mock_chat = MagicMock()
        mock_chat.process_turn.return_value = MagicMock(
            retrieved_chunks_json="[]",
            answer_text="Test answer.",
            provenance_json=None,
            provenance=None,
        )
        mock_grounding = MagicMock()
        mock_grounding.calculate_groundedness.return_value = (0.85, "Good")
        mock_chat.grounding_service = mock_grounding

        manager = get_settings_manager()
        original_config = manager._config
        manager._config = MagicMock()
        manager._config.retrieval = original

        try:
            service = EvaluationService(mock_chat)

            with patch.object(service, "_load_dataset", return_value=[
                {"id": "CASE-001", "question": "Q1", "expected_document_id": "doc-1"},
            ]):
                with patch("repositories.evaluation_repository.EvaluationRepository.save_run"):
                    await service.run_sanity_check(
                        dataset_path="dummy.json",
                        config_override=original,
                    )
        finally:
            manager._config = original_config

        assert original.retrieval_mode == frozen_before.retrieval_mode
        assert original.dynamic_routing_enabled == frozen_before.dynamic_routing_enabled
        assert original.query_expansion_enabled == frozen_before.query_expansion_enabled
        assert original.hyde_enabled == frozen_before.hyde_enabled
        assert original.reranker_enabled == frozen_before.reranker_enabled


class TestEvaluationService:
    """EvaluationService unit tests with mocked ChatService."""

    @pytest.mark.asyncio
    async def test_run_sanity_check_returns_summary(self):
        mock_chat = MagicMock()
        mock_chat.process_turn.return_value = MagicMock(
            retrieved_chunks_json=json.dumps([{"document_id": "doc-1"}]),
            answer_text="Test answer.",
            provenance_json=None,
            provenance=None,
        )
        mock_grounding = MagicMock()
        mock_grounding.calculate_groundedness.return_value = (0.85, "Good")
        mock_chat.grounding_service = mock_grounding

        service = EvaluationService(mock_chat)

        with patch.object(service, "_load_dataset", return_value=[
            {"id": "CASE-001", "question": "Q1", "expected_document_id": "doc-1"},
            {"id": "CASE-002", "question": "Q2", "expected_document_id": "doc-2"},
        ]):
            with patch("repositories.evaluation_repository.EvaluationRepository.save_run"):
                result = await service.run_sanity_check(dataset_path="dummy.json")

        assert result.total_cases == 2
        assert result.overall_groundedness == 0.85
        assert len(result.results) == 2

    @pytest.mark.asyncio
    async def test_run_sanity_check_empty_dataset(self):
        mock_chat = MagicMock()
        service = EvaluationService(mock_chat)

        with patch.object(service, "_load_dataset", return_value=[]):
            result = await service.run_sanity_check(dataset_path="dummy.json")

        assert result.total_cases == 0
        assert result.passed_cases == 0

    @pytest.mark.asyncio
    async def test_run_sanity_check_with_config_override_persists_variant(self):
        mock_chat = MagicMock()
        mock_chat.process_turn.return_value = MagicMock(
            retrieved_chunks_json="[]",
            answer_text="Test.",
            provenance_json=None,
            provenance=None,
        )
        mock_grounding = MagicMock()
        mock_grounding.calculate_groundedness.return_value = (0.5, "OK")
        mock_chat.grounding_service = mock_grounding

        manager = get_settings_manager()
        original_config = manager._config
        manager._config = MagicMock()
        manager._config.retrieval = RetrievalSettings()

        try:
            service = EvaluationService(mock_chat)
            config = RetrievalSettings(retrieval_mode="keyword")

            save_run = MagicMock()
            with patch.object(service, "_load_dataset", return_value=[
                {"id": "CASE-001", "question": "Q", "expected_document_id": "doc-1"},
            ]):
                with patch("repositories.evaluation_repository.EvaluationRepository.save_run", save_run):
                    with patch.object(manager, "save_run_snapshot", return_value="/tmp/snap.json"):
                        await service.run_sanity_check(
                            dataset_path="dummy.json",
                            config_override=config,
                            config_variant_name="baseline",
                        )

            save_run.assert_called_once()
            _, kwargs = save_run.call_args
            assert kwargs.get("config_variant_name") == "baseline"
            assert kwargs.get("config_snapshot_json") is not None
        finally:
            manager._config = original_config


class TestAblationRouter:
    """Integration tests for POST /evaluate/ablation."""

    @pytest.fixture
    def client(self):
        from app import create_app
        app = create_app()
        return TestClient(app)

    @pytest.fixture
    def mock_eval_service(self):
        service = MagicMock(spec=EvaluationService)
        service.run_sanity_check = AsyncMock(return_value=SanityCheckResponse(
            timestamp="2026-01-01T00:00:00",
            total_cases=2,
            passed_cases=2,
            overall_recall=1.0,
            overall_groundedness=0.85,
            overall_citation_coverage=0.9,
            results=[
                _make_mock_eval_result("CASE-001"),
                _make_mock_eval_result("CASE-002"),
            ],
        ))
        return service

    def _override_deps(self, app, service):
        from chat.evaluation import get_evaluation_service
        app.dependency_overrides[get_evaluation_service] = lambda: service

    def test_ablation_happy_path(self, client, mock_eval_service):
        self._override_deps(client.app, mock_eval_service)
        resp = client.post("/evaluate/ablation", json={"variants": ["baseline", "full_pipeline"]})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparisons"]) == 2
        assert data["comparisons"][0]["variant_name"] == "baseline"
        assert data["comparisons"][1]["variant_name"] == "full_pipeline"
        assert len(data["deltas"]) == 1

    def test_ablation_unknown_variant(self, client, mock_eval_service):
        self._override_deps(client.app, mock_eval_service)
        resp = client.post("/evaluate/ablation", json={"variants": ["nonexistent"]})
        assert resp.status_code == 400
        assert "Unknown variant" in resp.json()["detail"]

    def test_ablation_single_variant(self, client, mock_eval_service):
        self._override_deps(client.app, mock_eval_service)
        resp = client.post("/evaluate/ablation", json={"variants": ["baseline"]})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparisons"]) == 1
        assert len(data["deltas"]) == 0

    def test_ablation_empty_variants_list(self, client, mock_eval_service):
        self._override_deps(client.app, mock_eval_service)
        resp = client.post("/evaluate/ablation", json={"variants": []})
        assert resp.status_code == 400

    def test_existing_sanity_check_unaffected(self, client, mock_eval_service):
        self._override_deps(client.app, mock_eval_service)
        resp = client.post("/chat/evaluate/sanity-check")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_cases" in data
