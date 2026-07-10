from __future__ import annotations

import json
import copy
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from chat.evaluation import get_evaluation_service, EvaluationService
from schemas.chat import AblationComparisonResponse, VariantResult, VariantDelta, SanityCheckResponse
from schemas.settings import RetrievalSettings
from config import get_settings_manager

router = APIRouter(prefix="/evaluate", tags=["evaluate"])

_VARIANTS_PATH = Path(__file__).resolve().parent.parent / "config" / "ablation-variants.json"


def _load_variants() -> list[dict]:
    if not _VARIANTS_PATH.exists():
        raise HTTPException(status_code=500, detail="ablation-variants.json not found")
    with open(_VARIANTS_PATH) as f:
        return json.load(f)


def _build_retrieval_config(overrides: dict) -> RetrievalSettings:
    base = get_settings_manager().config.retrieval.model_copy(deep=True)
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def _compute_deltas(comparisons: list[VariantResult]) -> list[VariantDelta]:
    if len(comparisons) < 2:
        return []
    baseline = comparisons[0].result
    deltas = []
    for c in comparisons[1:]:
        r = c.result
        deltas.append(VariantDelta(
            variant_name=c.variant_name,
            recall_delta=r.overall_recall - baseline.overall_recall if baseline.overall_recall is not None else None,
            groundedness_delta=r.overall_groundedness - baseline.overall_groundedness if baseline.overall_groundedness is not None else None,
            citation_coverage_delta=(
                (r.overall_citation_coverage or 0.0) - (baseline.overall_citation_coverage or 0.0)
            ),
            pass_rate_delta=(
                (r.passed_cases / r.total_cases if r.total_cases > 0 else 0.0)
                - (baseline.passed_cases / baseline.total_cases if baseline.total_cases > 0 else 0.0)
            ),
        ))
    return deltas


@router.post("/ablation", response_model=AblationComparisonResponse)
async def run_ablation(
    body: dict,
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
) -> AblationComparisonResponse:
    variant_names: list[str] = body.get("variants", [])
    if not variant_names:
        raise HTTPException(status_code=400, detail="'variants' list is required")

    all_variants = _load_variants()
    variant_map = {v["name"]: v for v in all_variants}

    for name in variant_names:
        if name not in variant_map:
            valid = list(variant_map.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Unknown variant '{name}'. Valid variants: {valid}"
            )

    comparisons: list[VariantResult] = []
    for name in variant_names:
        variant = variant_map[name]
        config = _build_retrieval_config(variant.get("overrides", {}))
        result = await evaluation_service.run_sanity_check(
            config_override=config,
            config_variant_name=name,
        )
        comparisons.append(VariantResult(
            variant_name=name,
            label=variant.get("label", name),
            result=result,
        ))

    deltas = _compute_deltas(comparisons)
    return AblationComparisonResponse(
        variants=variant_names,
        comparisons=comparisons,
        deltas=deltas,
    )
