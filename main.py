from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from config.database import database
from config.settings import settings
from middlewares.rate_limit import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

# Import routers
from routers.auth_router import router as auth_router
from routers.event_router import router as event_router
from routers.registration_router import router as registration_router
from routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    await database.connect_db()
    yield
    # Shutdown
    await database.close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Add rate limiter state
app.state.limiter = limiter

# Add SlowAPI middleware for rate limiting
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )


# Include routers
app.include_router(auth_router)
app.include_router(event_router)
app.include_router(registration_router)
app.include_router(user_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "EventSync API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
