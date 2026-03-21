from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import (
	Boolean,
	DateTime,
	Float,
	ForeignKey,
	Integer,
	String,
	Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
	pass


class User(SQLAlchemyBaseUserTable, Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True)
	hashed_password: Mapped[str] = mapped_column(String(length=1024))
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)
	is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
	is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
	forename: Mapped[str] = mapped_column(String(100))
	surname: Mapped[str] = mapped_column(String(100))
	pin: Mapped[str] = mapped_column(String(4))

	cars: Mapped[list["Car"]] = relationship(back_populates="owner", lazy="selectin")


class Station(Base):
	__tablename__ = "stations"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(100))
	description: Mapped[str | None] = mapped_column(Text, default=None)
	owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

	owner: Mapped[User] = relationship(back_populates="stations", lazy="selectin")


class Car(Base):
	__tablename__ = "cars"

	id: Mapped[int] = mapped_column(primary_key=True)
	type: Mapped[str] = mapped_column(String(100))
	license_plate_number: Mapped[str] = mapped_column(String(20), unique=True)
	owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

	owner: Mapped[User] = relationship(back_populates="cars", lazy="selectin")
	history_records: Mapped[list["HistoryRecord"]] = relationship(back_populates="car", lazy="selectin")


class FuelType(Base):
	__tablename__ = "fuel_types"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(50), unique=True)

	history_records: Mapped[list["HistoryRecord"]] = relationship(back_populates="fuel_type", lazy="selectin")


class HistoryRecord(Base):
	__tablename__ = "history_records"

	id: Mapped[int] = mapped_column(primary_key=True)
	timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	mileage: Mapped[float] = mapped_column(Float)
	price_per_litre: Mapped[float] = mapped_column(Float)
	litres: Mapped[float] = mapped_column(Float)
	car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"))
	fuel_type_id: Mapped[int] = mapped_column(ForeignKey("fuel_types.id"))

	car: Mapped[Car] = relationship(back_populates="history_records", lazy="selectin")
	fuel_type: Mapped[FuelType] = relationship(back_populates="history_records", lazy="selectin")


User.stations = relationship("Station", back_populates="owner", lazy="selectin")
