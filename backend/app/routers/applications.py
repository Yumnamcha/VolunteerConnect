from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Application, Campaign, User
from ..schemas import ApplicationOut, StatusUpdate
from ..dependencies import require_volunteer, require_coordinator

router = APIRouter(prefix="/api/applications", tags=["Applications"])

def app_out(a):
    return ApplicationOut(
        id=a.id,
        volunteer_id=a.volunteer_id,
        campaign_id=a.campaign_id,
        status=a.status,
        applied_at=a.applied_at,
        volunteer_name=a.volunteer.name if a.volunteer else None,
        volunteer_email=a.volunteer.email if a.volunteer else None
    )

@router.post("/campaign/{campaign_id}", response_model=ApplicationOut)
def apply(
    campaign_id: int,
    volunteer: User = Depends(require_volunteer),
    db: Session = Depends(get_db)
):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    existing = db.query(Application).filter(
        Application.volunteer_id == volunteer.id,
        Application.campaign_id == campaign_id
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Already applied")

    approved = db.query(func.count(Application.id)).filter(
        Application.campaign_id == campaign_id,
        Application.status == "approved"
    ).scalar() or 0

    if approved >= campaign.required_volunteers:
        raise HTTPException(status_code=400, detail="Campaign is full")

    application = Application(
        volunteer_id=volunteer.id,
        campaign_id=campaign_id
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return app_out(application)

@router.get("/mine", response_model=list[ApplicationOut])
def my_applications(
    volunteer: User = Depends(require_volunteer),
    db: Session = Depends(get_db)
):
    rows = db.query(Application).filter(
        Application.volunteer_id == volunteer.id
    ).order_by(Application.applied_at.desc()).all()
    return [app_out(a) for a in rows]

@router.get("/campaign/{campaign_id}", response_model=list[ApplicationOut])
def campaign_applications(
    campaign_id: int,
    coordinator: User = Depends(require_coordinator),
    db: Session = Depends(get_db)
):
    campaign = db.get(Campaign, campaign_id)
    if not campaign or campaign.coordinator_id != coordinator.id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    rows = db.query(Application).filter(
        Application.campaign_id == campaign_id
    ).order_by(Application.applied_at.desc()).all()
    return [app_out(a) for a in rows]

@router.patch("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int,
    data: StatusUpdate,
    coordinator: User = Depends(require_coordinator),
    db: Session = Depends(get_db)
):
    if data.status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.campaign.coordinator_id != coordinator.id:
        raise HTTPException(status_code=403, detail="Not your campaign")

    application.status = data.status
    db.commit()
    db.refresh(application)
    return app_out(application)
