from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/prescription")
async def analyze_prescription():
    # TODO: Orchestrate OCR → NER → FeatureGen → Risk-Engine
    return {"msg": "Pipeline not yet implemented"}
