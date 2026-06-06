from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
from typing import Optional

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.depression_flags import depression_flag_service

class EmotionRequest(BaseModel):
    text: Optional[str] = None
    image_base64: Optional[str] = None

class EmotionResponse(BaseModel):
    emotion: str
    confidence: float
    depression_flag_count: int = 0
    threshold_exceeded: bool = False

router = APIRouter()

@router.post(
    '/emotion',
    summary="Detect emotion from text or image",
    response_model=EmotionResponse,
    responses={
        200: {
            "description": "Emotion detection result",
            "content": {
                "application/json": {
                    "example": {
                        "emotion": "sad",
                        "confidence": 0.95,
                        "depression_flag_count": 2,
                        "threshold_exceeded": False
                    }
                }
            }
        }
    }
)
async def detect_emotion(
    request: EmotionRequest = Body(
        ...,
        examples={
            "textExample": {
                "summary": "Text emotion detection",
                "value": {
                    "text": "I feel so sad and hopeless",
                    "image_base64": None
                }
            },
            "imageExample": {
                "summary": "Image emotion detection",
                "value": {
                    "text": None,
                    "image_base64": "iVBORw0KGgoAAAANSUhE..."
                }
            }
        }
    ),
    current_user: User = Depends(get_current_user),
):
    """Detect emotion from provided text or base64-encoded image."""
    if request.image_base64:
        emotion = "happy"
        confidence = 0.92
    elif request.text and "sad" in request.text.lower():
        emotion = "sad"
        confidence = 0.95
    else:
        emotion = "calm"
        confidence = 0.80

    flag_status = await depression_flag_service.process_emotion(
        user_id=current_user.id,
        emotion_data={"dominant_emotion": emotion, "confidence": confidence},
        source="emotion_api",
    )

    return EmotionResponse(
        emotion=emotion,
        confidence=confidence,
        depression_flag_count=flag_status.flag_count,
        threshold_exceeded=flag_status.threshold_exceeded,
    )
