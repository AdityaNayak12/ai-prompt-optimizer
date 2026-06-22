from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.contract import DetailResponse, OptimizeRequest, OptimizeResponse
from app.services.groq import GroqService, get_groq_service

router = APIRouter(
    prefix="/optimize",
    tags=["optimize"],
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": DetailResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": DetailResponse},
    },
)


@router.post(
    "",
    response_model=OptimizeResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimize prompt",
    description="Analyze a raw prompt and return an improved version based on prompt engineering standards.",
)
async def optimize(
    request: OptimizeRequest, service: GroqService = Depends(get_groq_service)
) -> OptimizeResponse:
    try:
        # Check if API Key is configured
        from app.config import settings

        if not settings.GROQ_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Groq API Key is not configured on the backend server.",
            )

        return await service.optimize_prompt(request)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while optimizing prompt: {str(e)}",
        ) from e
