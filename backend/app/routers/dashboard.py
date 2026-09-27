from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Campaign, Application
from ..schemas import DashboardOut
from ..dependencies import get_current_user, require_coordinator

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/volunteer", response_model=DashboardOut)
def volunteer_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    applications = db.query(func.count(Application.id)).filter(
        Application.volunteer_id == user.id
    ).scalar() or 0

    approved = db.query(func.count(Application.id)).filter(
        Application.volunteer_id == user.id,
        Application.status == "approved"
    ).scalar() or 0

    return DashboardOut(
        campaigns=db.query(Campaign).count(),
        applications=applications,
        approved=approved,
        volunteers=db.query(User).filter(User.role == "volunteer").count()
    )

@router.get("/coordinator", response_model=DashboardOut)
def coordinator_dashboard(
    user: User = Depends(require_coordinator),
    db: Session = Depends(get_db)
):
    campaigns = db.query(func.count(Campaign.id)).filter(
        Campaign.coordinator_id == user.id
    ).scalar() or 0

    applications = db.query(func.count(Application.id)).join(Campaign).filter(
        Campaign.coordinator_id == user.id
    ).scalar() or 0

    approved = db.query(func.count(Application.id)).join(Campaign).filter(
        Campaign.coordinator_id == user.id,
        Application.status == "approved"
    ).scalar() or 0

    volunteers = db.query(func.count(User.id)).filter(
        User.role == "volunteer"
    ).scalar() or 0

    return DashboardOut(
        campaigns=campaigns,
        applications=applications,
        approved=approved,
        volunteers=volunteers
    )
