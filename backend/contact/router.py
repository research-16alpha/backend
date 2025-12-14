from fastapi import APIRouter, BackgroundTasks
from .models import ContactForm
from .service import ContactService

router = APIRouter(prefix="/api/contact", tags=["Contact"])

@router.post("/")
def submit(contact: ContactForm, background: BackgroundTasks):
    result = ContactService.save_message(contact.email, contact.message)
    background.add_task(ContactService.send_email, contact.email, contact.message)

    return {
        "success": True,
        "id": str(result.inserted_id),
        "message": "Thank you for contacting us!"
    }
