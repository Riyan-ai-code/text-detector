from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.services.epoch_service import epoch_service
from backend.app.services.data_cleaning_service import data_cleaning_service

router = APIRouter(prefix="/model", tags=["Model Epochs & Performance Diagnostics"])


class CleanTextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text with potential HTML, watermarks, or boilerplate noise")


@router.get("/epochs")
async def get_epoch_trajectory() -> Dict[str, Any]:
    """
    Returns the comprehensive 10-epoch training trajectory:
    - Step-level training loss convergence with Exponential Moving Average (EMA) noise smoothing
    - Epoch evaluation checkpoints (Loss, Accuracy, F1, Precision, Recall) across all 10 epochs
    - Global minimum validation loss milestone (Epoch 6.0 / Step 3000)
    - Cosine annealing learning rate schedule
    """
    return epoch_service.get_epoch_trajectory()


@router.get("/epochs/{epoch_number}")
async def get_epoch_slice(epoch_number: float) -> Dict[str, Any]:
    """
    Returns performance metrics for a specific epoch number (1.0 to 10.0).
    """
    epoch_data = epoch_service.get_epoch_by_number(epoch_number)
    if not epoch_data:
        raise HTTPException(
            status_code=404,
            detail=f"Epoch {epoch_number} not found. Available epochs are 1.0 through 10.0."
        )
    return epoch_data


@router.get("/evaluation")
async def get_model_evaluation() -> Dict[str, Any]:
    """
    Returns independent evaluation metrics on 1,000 unseen test samples
    along with the 2x2 confusion matrix and diagnostic error rates.
    """
    return epoch_service.get_test_evaluation()


@router.get("/checkpoints")
async def get_checkpoints_catalog() -> List[Dict[str, Any]]:
    """
    Returns saved checkpoint artifacts catalog across the 10 epochs,
    highlighting the optimal early-stopping candidate (checkpoint-3000 / Epoch 6.0).
    """
    return epoch_service.get_checkpoints_catalog()


@router.get("/data-cleaning/stats")
async def get_data_cleaning_stats() -> Dict[str, Any]:
    """
    Returns empirical data cleaning and noise removal telemetry across the training dataset:
    - HTML/XML tags stripped
    - Zero-width watermarks neutralized
    - LLM conversational boilerplate filtered
    - Mojibake encodings repaired
    - Cleanliness score improvements
    """
    return data_cleaning_service.get_dataset_cleaning_stats()


@router.get("/data-cleaning/samples")
async def get_data_cleaning_samples() -> List[Dict[str, str]]:
    """
    Returns pre-configured noisy text samples for interactive frontend testing.
    """
    return data_cleaning_service.get_sample_noisy_texts()


@router.post("/data-cleaning/clean")
async def clean_text_noise(payload: CleanTextRequest) -> Dict[str, Any]:
    """
    Cleans raw noisy text: strips HTML/XML, neutralizes zero-width characters,
    removes LLM boilerplate prefixes, repairs mojibake, and normalizes runaway whitespace.
    """
    return data_cleaning_service.clean_sample(payload.text)
