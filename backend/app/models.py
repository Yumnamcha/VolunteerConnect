from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, Date, Time, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="volunteer")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Verification ID uploaded at signup, stored as a base64 data URL so no
    # separate file storage service is needed.
    verification_document: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(30), default="unverified")

    # Forgot-password flow
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reset_token_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    campaigns = relationship("Campaign", back_populates="coordinator")
    applications = relationship("Application", back_populates="volunteer")
    messages = relationship("Message", back_populates="sender")

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(180))
    event_date: Mapped[datetime.date] = mapped_column(Date)
    event_time: Mapped[datetime.time] = mapped_column(Time)
    category: Mapped[str] = mapped_column(String(80))
    required_volunteers: Mapped[int] = mapped_column(Integer, default=10)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    coordinator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # "active" | "completed" | "cancelled" - completed campaigns unlock
    # certificate downloads for their approved volunteers.
    status: Mapped[str] = mapped_column(String(30), default="active")
    donation_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    coordinator = relationship("User", back_populates="campaigns")
    applications = relationship("Application", back_populates="campaign", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="campaign", cascade="all, delete-orphan")

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("volunteer_id", "campaign_id", name="uq_volunteer_campaign"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    volunteer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    volunteer = relationship("User", back_populates="applications")
    campaign = relationship("Campaign", back_populates="applications")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="messages")
    sender = relationship("User", back_populates="messages")
