from routes.reports import router as reports_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.dashboard import router as dashboard_router
from routes.analysis import router as analysis_router
from routes.forecast import router as forecast_router
from routes.auth import router as auth_router

app = FastAPI(title="Sales Analysis API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "https://sales-analysis-and-forecating.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(analysis_router)
app.include_router(forecast_router)
app.include_router(reports_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "message": "Sales Analysis & Forecasting API Running Successfully 🚀"
    }