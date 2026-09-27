from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Campaign, Application, User
from ..schemas import CampaignCreate, CampaignOut
from ..dependencies import get_current_user, require_coordinator

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])

def serialize_campaign(c, db):
    approved = db.query(func.count(Application.id)).filter(
        Application.campaign_id == c.id,
        Application.status == "approved"
    ).scalar() or 0
    total = db.query(func.count(Application.id)).filter(
        Application.campaign_id == c.id
    ).scalar() or 0

    return CampaignOut(
        **{k: getattr(c, k) for k in [
            "id", "title", "description", "location", "event_date",
            "event_time", "category", "required_volunteers",
            "image_url", "coordinator_id", "created_at"
        ]},
        approved_count=approved,
        application_count=total
    )

@router.get("", response_model=list[CampaignOut])
def list_campaigns(
    search: str = "",
    category: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(Campaign)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Campaign.title.ilike(pattern)) |
            (Campaign.description.ilike(pattern)) |
            (Campaign.location.ilike(pattern))
        )

    if category:
        query = query.filter(Campaign.category == category)

    campaigns = query.order_by(Campaign.event_date.asc()).all()
    return [serialize_campaign(c, db) for c in campaigns]

@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    c = db.get(Campaign, campaign_id)
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return serialize_campaign(c, db)

@router.post("", response_model=CampaignOut)
def create_campaign(
    data: CampaignCreate,
    coordinator: User = Depends(require_coordinator),
    db: Session = Depends(get_db)
):
    c = Campaign(**data.model_dump(), coordinator_id=coordinator.id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return serialize_campaign(c, db)

@router.put("/{campaign_id}", response_model=CampaignOut)
def update_campaign(
    campaign_id: int,
    data: CampaignCreate,
    coordinator: User = Depends(require_coordinator),
    db: Session = Depends(get_db)
):
    c = db.get(Campaign, campaign_id)

    if not c or c.coordinator_id != coordinator.id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    for key, value in data.model_dump().items():
        setattr(c, key, value)

    db.commit()
    db.refresh(c)
    return serialize_campaign(c, db)

@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    coordinator: User = Depends(require_coordinator),
    db: Session = Depends(get_db)
):
    c = db.get(Campaign, campaign_id)

    if not c or c.coordinator_id != coordinator.id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(c)
    db.commit()
    return {"message": "Campaign deleted"}
