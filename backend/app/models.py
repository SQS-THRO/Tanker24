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
	UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
	pass


class User(SQLAlchemyBaseUserTable[int], Base):
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
	latitude: Mapped[float | None] = mapped_column(Float, default=None)
	longitude: Mapped[float | None] = mapped_column(Float, default=None)
	owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

	owner: Mapped[User] = relationship(back_populates="stations", lazy="selectin")


class TankerkoenigStation(Base):
	__tablename__ = "tankerkoenig_stations"
	__table_args__ = (UniqueConstraint("tankerkoenig_id", name="uix_tankerkoenig_id"),)

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	tankerkoenig_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
	name: Mapped[str] = mapped_column(String(100))
	brand: Mapped[str] = mapped_column(String(100))
	street: Mapped[str | None] = mapped_column(String(200), default=None)
	house_number: Mapped[str | None] = mapped_column(String(20), default=None)
	post_code: Mapped[int | None] = mapped_column(Integer, default=None)
	place: Mapped[str | None] = mapped_column(String(100), default=None)
	latitude: Mapped[float] = mapped_column(Float)
	longitude: Mapped[float] = mapped_column(Float)
	distance: Mapped[float | None] = mapped_column(Float, default=None)
	diesel: Mapped[float | None] = mapped_column(Float, default=None)
	e5: Mapped[float | None] = mapped_column(Float, default=None)
	e10: Mapped[float | None] = mapped_column(Float, default=None)
	is_open: Mapped[bool] = mapped_column(Boolean, default=True)
	cached_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


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
