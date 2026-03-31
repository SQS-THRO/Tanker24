import json

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.auth import get_current_active_user
from app.database import get_db
from app.models import HistoryRecord,Car
from app.schemas.user import UserRead

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/json",
            status_code=status.HTTP_200_OK,
            summary="Get the user data as json",
            description="Returns the user data of the authenticated user as a json string.",
            responses={503:{"Database temporarily unavailable."}}
            )
async def get_user_data_as_json(
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
) -> str:
    result = []

    try:
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
                        "mileage": record.mileage,
                        "price_per_litre": record.price_per_litre,
                        "litres": record.litres,
                        "total_price": record.price_per_litre * record.litres,
                        "fuel_type": record.fuel_type.name,
                    })
            result.append({
                "id": car.id,
                "type": car.type,
                "license_plate_number": car.license_plate_number,
                "history": history
            })

        return json.dumps(result)

    except SQLAlchemyError as e:
        await db.rollback()
        # Return a 503 Service Unavailable exception
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable."
        ) from e
