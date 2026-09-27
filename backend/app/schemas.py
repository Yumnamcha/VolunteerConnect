from datetime import date, time, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    role: str = "volunteer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class CampaignCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10)
    location: str = Field(min_length=2, max_length=180)
    event_date: date
    event_time: time
    category: str
    required_volunteers: int = Field(default=10, ge=1, le=10000)
    image_url: str | None = None

class CampaignOut(CampaignCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    coordinator_id: int
    created_at: datetime
    approved_count: int = 0
    application_count: int = 0

class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    volunteer_id: int
    campaign_id: int
    status: str
    applied_at: datetime
    volunteer_name: str | None = None
    volunteer_email: str | None = None

class StatusUpdate(BaseModel):
    status: str

class MessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_id: int
    sender_id: int
    sender_name: str
    message: str
    created_at: datetime

class DashboardOut(BaseModel):
    campaigns: int
    applications: int
    approved: int
    volunteers: int
