from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import optimize

# Initialize FastAPI App
app = FastAPI(
    title="Prompt Advisor API",
    description="Backend service for optimization of AI prompts via Groq models.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local development and extension integration
# settings.cors_origins_list defaults to ["*"] but can be locked down in production config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check route
@app.get(
    "/health", status_code=status.HTTP_200_OK, tags=["health"], response_model=dict
)
def health_check():
    return {"status": "ok", "environment": settings.ENV}


# Mount v1 api routes
app.include_router(optimize.router, prefix="/api/v1")


# Global Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Format a simple, unified error message
    error_msgs = []
    for err in errors:
        loc = " -> ".join(str(x) for x in err["loc"])
        error_msgs.append(f"{loc}: {err['msg']}")
    detail = "; ".join(error_msgs)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": detail}
    )


# Generic Exception Handler
@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )
