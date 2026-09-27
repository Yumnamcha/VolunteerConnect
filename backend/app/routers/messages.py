from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Message, Campaign, User
from ..schemas import MessageCreate, MessageOut
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/messages", tags=["Messages"])

def out(m):
    return MessageOut(
        id=m.id,
        campaign_id=m.campaign_id,
        sender_id=m.sender_id,
        sender_name=m.sender.name,
        message=m.message,
        created_at=m.created_at
    )

@router.get("/campaign/{campaign_id}", response_model=list[MessageOut])
def get_messages(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not db.get(Campaign, campaign_id):
        raise HTTPException(status_code=404, detail="Campaign not found")

    rows = db.query(Message).filter(
        Message.campaign_id == campaign_id
    ).order_by(Message.created_at.asc()).all()

    return [out(m) for m in rows]

@router.post("/campaign/{campaign_id}", response_model=MessageOut)
def send_message(
    campaign_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not db.get(Campaign, campaign_id):
        raise HTTPException(status_code=404, detail="Campaign not found")

    m = Message(
        campaign_id=campaign_id,
        sender_id=user.id,
        message=data.message.strip()
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return out(m)
