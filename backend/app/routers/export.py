import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.auth import get_current_active_user
from app.database import get_db
from app.models import HistoryRecord,Car
from app.schemas.user import UserRead
from app.schemas.history_record import HistoryRecordCreate

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/json", status_code=status.HTTP_200_OK, summary="Get the user data as json", description="Returns the user data of the authenticated user as a json string.")
async def get_userdata(
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
) -> str:
    result = []
    car_query_result = await db.execute(select(Car).where(Car.owner_id == user.id))
    cars = car_query_result.scalars().all()
    for car in cars:
        history = []
        history_query_result = await db.execute(select(HistoryRecord).where(HistoryRecord.car_id == car.id))
        history_records = history_query_result.scalars().all()
        # Check if the car has any history records before processing
        if len(history_records) > 0:
            for record in history_records:
                history.append({
                    "id": record.id,
                    "car_id": record.car_id,
                    "created_at": record.timestamp,
                    "milage": record.milage,
                    "price_per_litre": record.price_per_litre,
                    "litres": record.litres,
                    "total_price": record.price_per_litre * record.litres,
                    "fuel_type": record.fuel_type.name,
                })
        result.append({
            "id": car.id,
            "type": car.type,
            "license_plate": car.license_plate,
            "history": history
        })

    return json.dumps(result)