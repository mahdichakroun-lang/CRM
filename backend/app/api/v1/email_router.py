"""
API Router — Email notifications (test & status & manual send).
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.api.deps import get_current_user, require_roles, require_internal
from app.domain.auth.models import User, UserRole
from app.config import get_settings
from app.shared.email_service import send_email, _base_template, _info_row
from app.shared.email_helpers import get_client_email_for_ticket

logger = logging.getLogger("crm.email")

router = APIRouter(prefix="/email", tags=["Email"])


class EmailTestRequest(BaseModel):
    to_email: str
    subject: Optional[str] = "🧪 Test — CRM Email Notification"
    message: Optional[str] = "Ceci est un email de test envoyé depuis le CRM."


class EmailSendRequest(BaseModel):
    to_email: str
    subject: str
    message: str


class EmailTicketNotifyRequest(BaseModel):
    subject: Optional[str] = None
    message: str


class EmailConfigStatus(BaseModel):
    configured: bool
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_from_name: str


@router.get("/status", response_model=EmailConfigStatus)
def email_config_status(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    """Check if email SMTP is properly configured (admin only)."""
    settings = get_settings()
    return EmailConfigStatus(
        configured=bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD),
        smtp_host=settings.SMTP_HOST or "(non configuré)",
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER or "(non configuré)",
        smtp_from_name=settings.SMTP_FROM_NAME,
    )


@router.post("/test")
def send_test_email(
    payload: EmailTestRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    """Send a test email to verify SMTP configuration (admin only)."""
    content = f"""
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Bonjour <strong>{current_user.name}</strong>,
    </p>
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        {payload.message}
    </p>

    <div style="background:#f0fdf4;border-radius:12px;padding:20px;margin:0 0 24px;
                border:1px solid #bbf7d0;">
        <p style="margin:0;color:#166534;font-size:14px;line-height:1.6;">
            ✅ Si vous recevez cet email, la configuration SMTP fonctionne correctement !
        </p>
    </div>

    <div style="background:#f8fafc;border-radius:12px;padding:24px;margin:0 0 24px;
                border-left:4px solid #6366f1;">
        <p style="margin:0 0 8px;color:#64748b;font-size:13px;">Envoyé par :</p>
        <p style="margin:0;color:#1e293b;font-size:14px;font-weight:600;">
            {current_user.name} ({current_user.email})
        </p>
    </div>
    """

    html = _base_template("🧪 Email de test", content)
    success = send_email(payload.to_email, payload.subject, html)

    if success:
        return {"status": "success", "message": f"Email de test envoyé à {payload.to_email}"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Échec de l'envoi — vérifiez la configuration SMTP dans le fichier .env",
        )


@router.post("/send")
def send_custom_email(
    payload: EmailSendRequest,
    current_user: User = Depends(require_internal),
):
    """Send a custom email to any recipient (internal users only)."""
    content = f"""
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        {payload.message}
    </p>

    <div style="background:#f8fafc;border-radius:12px;padding:24px;margin:0 0 24px;
                border-left:4px solid #6366f1;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
            {_info_row("Envoyé par", current_user.name)}
            {_info_row("Rôle", current_user.role.value.capitalize())}
        </table>
    </div>
    """

    html = _base_template(payload.subject, content)
    success = send_email(payload.to_email, payload.subject, html)

    if success:
        return {"status": "success", "message": f"Email envoyé à {payload.to_email}"}
    else:
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email")


@router.post("/ticket/{ticket_id}/notify")
def notify_ticket_client(
    ticket_id: int,
    payload: EmailTicketNotifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    """Send a custom email notification to the client linked to a ticket."""
    recipient = get_client_email_for_ticket(db, ticket_id)
    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Aucun email client trouvé pour ce ticket",
        )

    email, client_name = recipient
    subject = payload.subject or f"📧 Message de FRS — Ticket #{ticket_id}"

    content = f"""
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Bonjour <strong>{client_name}</strong>,
    </p>
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        {payload.message}
    </p>

    <div style="background:#f8fafc;border-radius:12px;padding:24px;margin:0 0 24px;
                border-left:4px solid #6366f1;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
            {_info_row("Ticket", f"#{ticket_id}")}
            {_info_row("Agent", current_user.name)}
        </table>
    </div>

    <div style="text-align:center;margin:32px 0 0;">
        <a href="http://localhost:3000/tickets" style="display:inline-block;padding:12px 32px;background:linear-gradient(135deg,#1565C0,#1976D2);
                          color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;
                          font-size:14px;box-shadow:0 4px 12px rgba(21,101,192,0.3);">
            Voir mon ticket
        </a>
    </div>
    """

    html = _base_template(subject, content)
    success = send_email(email, subject, html)

    if success:
        return {
            "status": "success",
            "message": f"Email envoyé à {client_name} ({email})",
            "to_email": email,
            "client_name": client_name,
        }
    else:
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email")
