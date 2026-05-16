import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from chat.evaluation import EvaluationService, get_evaluation_service
from schemas.evaluation import EvaluationDataset, EvaluationRun
from schemas.chat import AdvancedRetrievalConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/eval", tags=["evaluation"])


@router.get("/datasets", response_model=List[EvaluationDataset])
async def list_datasets(service: EvaluationService = Depends(get_evaluation_service)):
    """List all available evaluation datasets."""
    return service.list_datasets()


@router.get("/datasets/{dataset_id}", response_model=EvaluationDataset)
async def get_dataset(dataset_id: str, service: EvaluationService = Depends(get_evaluation_service)):
    """Get a specific dataset by ID."""
    dataset = service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.post("/datasets", response_model=EvaluationDataset)
async def save_dataset(dataset: EvaluationDataset, service: EvaluationService = Depends(get_evaluation_service)):
    """Save or update a dataset."""
    service.save_dataset(dataset)
    return dataset


@router.get("/runs", response_model=List[EvaluationRun])
async def list_runs(service: EvaluationService = Depends(get_evaluation_service)):
    """List all evaluation runs."""
    return service.list_runs()


@router.get("/runs/{run_id}", response_model=EvaluationRun)
async def get_run(run_id: str, service: EvaluationService = Depends(get_evaluation_service)):
    """Get a specific run by ID."""
    run = service._get_run(run_id) # Using internal method for now
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("/run/{dataset_id}")
async def trigger_run(
    dataset_id: str,
    config: AdvancedRetrievalConfig,
    background_tasks: BackgroundTasks,
    service: EvaluationService = Depends(get_evaluation_service)
):
    """Trigger a new evaluation run."""
    try:
        run_id = service.run_evaluation(dataset_id, config)
        background_tasks.add_task(service.execute_run, run_id)
        return {"run_id": run_id, "status": "pending"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
