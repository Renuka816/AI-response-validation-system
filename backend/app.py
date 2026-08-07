from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
import os

# Import Routes

from backend.routes.evaluation import router as evaluation_router
from backend.routes.batch_evaluation import router as batch_router
# ============================
# Load Environment Variables
# ============================

load_dotenv()

# ============================
# Create FastAPI App
# ============================

app = FastAPI(
    title="AI Response Quality Evaluator",
    description="Evaluate AI-generated responses using RAG and Multi-Agent Evaluation",
    version="1.0.0"
)

# ============================
# Enable CORS
# ============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change later when deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# Static Files
# ============================

#app.mount(
#   "/static",
#   StaticFiles(directory="static"),
#   name="static"
#
#
# ============================
# HTML Templates
# ============================

#templates = Jinja2Templates(directory="templates")

# ============================
# Home Page
# ============================

@app.get("/")
async def home():

    return {
        "message": "AI Response Quality Evaluator API is running."
    }

# ============================
# Register API Routes
# ============================

app.include_router(
    evaluation_router,
    prefix="/api",
    tags=["Evaluation"]
)

app.include_router(
    batch_router,
    prefix="/api",
    tags=["Batch Evaluation"]
)