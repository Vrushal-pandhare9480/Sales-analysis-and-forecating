from fastapi import APIRouter
from ml.forecast import predict_next_6_months

router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)

@router.get("/")
def get_forecast():

    df = predict_next_6_months()

    return df.to_dict(orient="records")

