from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.gas_station_dtos import FuelType

from app.models import FuelType as FuelTypeModel

class FuelTypeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_name(self, fuel_type: FuelType) -> FuelTypeModel:
        result = await self.db.execute(
            select(FuelTypeModel).where(FuelTypeModel.name == fuel_type.value)
        )

        db_fuel_type = result.scalar_one_or_none()

        if db_fuel_type is None:
            raise ValueError(f"Fuel type does not exist: {fuel_type.value}")

        return db_fuel_type