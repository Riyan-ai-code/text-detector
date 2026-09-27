from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.services.baseline_profiler import BaselineProfiler

router = APIRouter(prefix="/baseline", tags=["Personal Writing Fingerprint"])

class CreateBaselineRequest(BaseModel):
    samples: List[str] = Field(..., min_length=1, description="3 to 5 samples of user genuine writing")
    profile_name: Optional[str] = Field(default="My Genuine Writing Profile")

class CompareBaselineRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Target text to compare against baseline")
    baseline: Optional[Dict[str, Any]] = None

DEFAULT_GENUINE_SAMPLES = [
    (
        "I spent most of last weekend rummaging through my grandfather's attic, searching for an old wooden toolbox he used to carry everywhere. "
        "The air up there smelled like cedar and aged paper, and beneath a stack of dusty canvas tarps, I finally found it! "
        "Opening the rusted brass latch brought back a flood of memories—summer afternoons building lopsided birdhouses on the back porch while listening "
        "to the hum of cicadas in the maple trees. Dad used to say quality tools outlive their owners, and he wasn't wrong."
    ),
    (
        "Last Tuesday during our evening team walk, Sarah brought up how remote work altered our perceptions of time. "
        "Back when we commuted two hours every single day on the subway, the train ride felt like a buffer between professional chaos and home life. "
        "Now, closing a browser tab doesn't quite produce the same psychological boundary. We stopped for ice cream near the pier and debated whether "
        "scheduled unplugging ever works in practice—most of us agreed that putting phones in a kitchen drawer after 8 PM is the only way that actually holds up."
    ),
    (
        "When I started learning pottery two winters ago, my first dozen coffee mugs looked more like prehistoric clay relics than functional drinkware. "
        "The centering step is where everyone gets humbled. If your hands tremble even slightly while the wheel spins at top speed, the clay wobbles out of symmetry instantly. "
        "My instructor, Marcus, kept telling me to breathe with my diaphragm and brace my elbows against my thighs. By the fifth week, something clicked, and I pulled my first balanced cylinder."
    )
]

# Cached active in-memory baseline
ACTIVE_BASELINE = BaselineProfiler.create_baseline(DEFAULT_GENUINE_SAMPLES, "Default Author Profile")

@router.get("/default")
async def get_default_baseline():
    """Returns the default pre-loaded genuine author baseline."""
    return ACTIVE_BASELINE

@router.post("/create")
async def create_baseline(payload: CreateBaselineRequest):
    """Creates an authorial writing baseline from 3-5 genuine writing samples."""
    global ACTIVE_BASELINE
    if len(payload.samples) < 1:
        raise HTTPException(status_code=400, detail="Provide at least 1-3 genuine samples.")
    baseline = BaselineProfiler.create_baseline(payload.samples, payload.profile_name or "Personal Author Profile")
    ACTIVE_BASELINE = baseline
    return baseline

@router.post("/compare")
async def compare_to_baseline(payload: CompareBaselineRequest):
    """Compares new text against the established author baseline."""
    target_baseline = payload.baseline or ACTIVE_BASELINE
    return BaselineProfiler.compare_to_baseline(payload.text, target_baseline)
