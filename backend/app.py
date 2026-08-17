from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

# Import Routes
from backend.routes.evaluation import router as evaluation_router
from backend.routes.batch_evaluation import router as batch_router
from backend.routes import dashboard
from backend.database.database import init_database

# ============================
# Load Environment Variables
# ============================

load_dotenv()


# ============================
# Initialize Database
# ============================

init_database()

# ============================
# Create FastAPI App
# ============================

app = FastAPI(
    title="AI Response Validation System",
    description="Development of AI Response Validation System with Hallucination Detection Assistance (Group 1)",
    version="1.0.0"
)


# ============================
# Enable CORS
# ============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================
# Home Page
# ============================

@app.get("/")
async def home():

    return {
        "message": "AI Response Quality Evaluator API is running."
    }


# ============================
# Register Evaluation Routes
# ============================

app.include_router(
    evaluation_router,
    prefix="/api",
    tags=["Evaluation"]
)


# ============================
# Register Batch Evaluation
# ============================

app.include_router(
    batch_router,
    prefix="/api",
    tags=["Batch Evaluation"]
)


# ============================
# Register Dashboard
# ============================

app.include_router(
    dashboard.router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)