import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Application, Campaign, User
from ..schemas import ApplicationOut, StatusUpdate
from ..dependencies import require_volunteer, require_coordinator, get_current_user

router = APIRouter(prefix="/api/applications", tags=["Applications"])

def app_out(a):
    return ApplicationOut(
        id=a.id,
        volunteer_id=a.volunteer_id,
        campaign_id=a.campaign_id,
        status=a.status,
        applied_at=a.applied_at,
        volunteer_name=a.volunteer.name if a.volunteer else None,
        volunteer_email=a.volunteer.email if a.volunteer else None,
        volunteer_verification_status=a.volunteer.verification_status if a.volunteer else None,
        campaign_title=a.campaign.title if a.campaign else None,
        campaign_status=a.campaign.status if a.campaign else None
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

def build_certificate_pdf(volunteer_name: str, campaign: Campaign) -> bytes:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas

    ink = HexColor("#1B2420")
    gold = HexColor("#B8822E")
    muted = HexColor("#4B5752")

    buffer = io.BytesIO()
    page = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=page)
    width, height = page

    pdf.setStrokeColor(gold)
    pdf.setLineWidth(3)
    pdf.rect(1.1 * cm, 1.1 * cm, width - 2.2 * cm, height - 2.2 * cm)
    pdf.setLineWidth(0.8)
    pdf.rect(1.4 * cm, 1.4 * cm, width - 2.8 * cm, height - 2.8 * cm)

    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(width / 2, height - 3.4 * cm, "VOLUNTEERCONNECT")

    pdf.setFillColor(ink)
    pdf.setFont("Helvetica-Bold", 34)
    pdf.drawCentredString(width / 2, height - 5.2 * cm, "Certificate of Appreciation")

    pdf.setFont("Helvetica", 14)
    pdf.setFillColor(muted)
    pdf.drawCentredString(width / 2, height - 7.2 * cm, "This certificate is proudly presented to")

    pdf.setFont("Helvetica-Bold", 28)
    pdf.setFillColor(gold)
    pdf.drawCentredString(width / 2, height - 8.6 * cm, volunteer_name)

    pdf.setFont("Helvetica", 13)
    pdf.setFillColor(muted)
    text = f"for volunteering with the \"{campaign.title}\" campaign in {campaign.location}"
    pdf.drawCentredString(width / 2, height - 10.3 * cm, text)
    pdf.drawCentredString(
        width / 2, height - 11.1 * cm,
        f"held on {campaign.event_date.strftime('%d %B %Y')}"
    )

    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(muted)
    pdf.drawCentredString(
        width / 2, 2.6 * cm,
        f"Issued {datetime.utcnow().strftime('%d %B %Y')} • VolunteerConnect"
    )

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()

@router.get("/{application_id}/certificate")
def download_certificate(
    application_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    is_owner = application.volunteer_id == user.id
    is_coordinator = application.campaign.coordinator_id == user.id
    if not (is_owner or is_coordinator):
        raise HTTPException(status_code=403, detail="Not allowed to view this certificate")

    if application.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved volunteers receive a certificate")

    if application.campaign.status != "completed":
        raise HTTPException(status_code=400, detail="Certificates are available once the campaign is marked completed")

    pdf_bytes = build_certificate_pdf(application.volunteer.name, application.campaign)
    filename = f"certificate-{application.campaign.title}-{application.volunteer.name}".replace(" ", "-")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'}
    )
