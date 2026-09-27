from datetime import date, time
from sqlalchemy.orm import Session
from .models import User, Campaign
from .security import hash_password

def seed_demo(db: Session):
    admin = db.query(User).filter(User.email == "admin@volunteerconnect.com").first()

    if not admin:
        admin = User(
            name="VolunteerConnect Admin",
            email="admin@volunteerconnect.com",
            password_hash=hash_password("admin123"),
            role="coordinator"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    if db.query(Campaign).count() == 0:
        demo = [
            Campaign(
                title="Beach Cleanup Drive",
                description="Join volunteers to clean public beach areas and promote responsible waste management.",
                location="Chennai Beach",
                event_date=date(2026, 10, 15),
                event_time=time(8, 0),
                category="Environment",
                required_volunteers=30,
                image_url="https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=1000&q=80",
                coordinator_id=admin.id
            ),
            Campaign(
                title="Weekend Learning Camp",
                description="Support school students through basic digital literacy, mathematics and reading activities.",
                location="Chennai",
                event_date=date(2026, 10, 24),
                event_time=time(9, 30),
                category="Education",
                required_volunteers=20,
                image_url="https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1000&q=80",
                coordinator_id=admin.id
            ),
            Campaign(
                title="Community Health Awareness",
                description="Help coordinate a community awareness program focused on healthy lifestyle and preventive care.",
                location="Tambaram",
                event_date=date(2026, 11, 5),
                event_time=time(10, 0),
                category="Health",
                required_volunteers=15,
                image_url="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1000&q=80",
                coordinator_id=admin.id
            )
        ]
        db.add_all(demo)
        db.commit()
