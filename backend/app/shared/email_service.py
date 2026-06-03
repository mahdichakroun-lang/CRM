"""
Email Notification Service — CRM Internal.

Handles sending email notifications to clients for:
- Ticket status changes (resolved, in_progress, waiting_customer, closed)
- New messages on tickets
- New quotes created
- Welcome emails

Uses SMTP (Gmail compatible) with beautiful HTML templates.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger("crm.email")


# ── Status Labels (French) ────────────────────────────────
STATUS_LABELS = {
    "open": "🟡 Ouvert",
    "in_progress": "🔵 En cours de traitement",
    "waiting_customer": "🟠 En attente de votre réponse",
    "resolved": "🟢 Résolu",
    "closed": "⚫ Fermé",
}

PRIORITY_LABELS = {
    "low": "Basse",
    "medium": "Moyenne",
    "high": "Haute",
    "urgent": "🔴 Urgente",
}


# ── HTML Email Base Template ──────────────────────────────
def _get_logo_data_uri() -> str:
    """Get the FRS logo as a data URI for email embedding."""
    try:
        from app.shared.logo_base64 import FRS_LOGO_BASE64
        return f"data:image/jpeg;base64,{FRS_LOGO_BASE64}"
    except ImportError:
        return ""


def _base_template(title: str, content: str, footer_text: str = "") -> str:
    """Generate a beautiful, responsive HTML email template with FRS logo."""
    settings = get_settings()
    app_name = settings.APP_NAME
    logo_uri = _get_logo_data_uri()

    logo_html = ""
    if logo_uri:
        logo_html = f"""
                                <img src="{logo_uri}" alt="FRS Logo"
                                     style="width:80px;height:80px;border-radius:16px;
                                            margin-bottom:12px;box-shadow:0 4px 16px rgba(0,0,0,0.2);" />
                                <br>"""

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI',Roboto,Arial,sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f0f4f8;">
            <tr>
                <td align="center" style="padding:40px 20px;">
                    <table role="presentation" width="600" cellspacing="0" cellpadding="0"
                           style="background-color:#ffffff;border-radius:16px;overflow:hidden;
                                  box-shadow:0 4px 24px rgba(0,0,0,0.08);">
                        <!-- Header with Logo -->
                        <tr>
                            <td style="background:linear-gradient(135deg,#1565C0,#1976D2);
                                       padding:32px 40px;text-align:center;">
                                {logo_html}
                                <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;
                                           letter-spacing:-0.5px;">
                                    FRS — IT Development Company
                                </h1>
                                <p style="margin:8px 0 0;color:rgba(255,255,255,0.85);font-size:13px;">
                                    Notification automatique — {app_name}
                                </p>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding:40px;">
                                <h2 style="margin:0 0 24px;color:#1e293b;font-size:20px;font-weight:700;
                                           letter-spacing:-0.3px;">
                                    {title}
                                </h2>
                                {content}
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color:#f8fafc;padding:24px 40px;
                                       border-top:1px solid #e2e8f0;">
                                <p style="margin:0;color:#94a3b8;font-size:12px;text-align:center;">
                                    {footer_text if footer_text else f"Cet email a été envoyé automatiquement par FRS — IT Development Company."}
                                    <br>Merci de ne pas répondre directement à cet email.
                                    <br><br>
                                    <span style="color:#cbd5e1;">FRS — IT Development Company | Tunis, Tunisie | contact@frs.tn</span>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# ── Info Row Helper ───────────────────────────────────────
def _info_row(label: str, value: str, color: str = "#6366f1") -> str:
    return f"""
    <tr>
        <td style="padding:8px 0;color:#64748b;font-size:14px;font-weight:600;
                   width:140px;vertical-align:top;">{label}</td>
        <td style="padding:8px 0;color:#1e293b;font-size:14px;">{value}</td>
    </tr>
    """


def _status_badge(status: str) -> str:
    """Generate a colored badge for ticket status."""
    colors = {
        "open": ("#f59e0b", "#fffbeb"),
        "in_progress": ("#3b82f6", "#eff6ff"),
        "waiting_customer": ("#f97316", "#fff7ed"),
        "resolved": ("#10b981", "#ecfdf5"),
        "closed": ("#6b7280", "#f9fafb"),
    }
    fg, bg = colors.get(status, ("#6b7280", "#f9fafb"))
    label = STATUS_LABELS.get(status, status)
    return f"""<span style="display:inline-block;padding:4px 12px;border-radius:20px;
                            font-size:13px;font-weight:600;color:{fg};background:{bg};">
                {label}
               </span>"""


# ── Send Email Function ───────────────────────────────────
def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send an email using SMTP settings from configuration.
    Returns True if successful, False otherwise.
    Failures are logged but never raise — email should not block CRM operations.
    """
    settings = get_settings()

    smtp_host = getattr(settings, "SMTP_HOST", "")
    smtp_port = getattr(settings, "SMTP_PORT", 587)
    smtp_user = getattr(settings, "SMTP_USER", "")
    smtp_password = getattr(settings, "SMTP_PASSWORD", "")
    smtp_from_name = getattr(settings, "SMTP_FROM_NAME", settings.APP_NAME)

    if not smtp_host or not smtp_user or not smtp_password:
        logger.warning("📧 Email non envoyé — configuration SMTP manquante dans .env")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{smtp_from_name} <{smtp_user}>"
        msg["To"] = to_email

        # Plain text fallback
        plain_text = f"{subject}\n\nCet email nécessite un client HTML pour être lu correctement."
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"📧 Email envoyé avec succès à {to_email} — Sujet: {subject}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("📧 ❌ Échec d'authentification SMTP — vérifiez SMTP_USER et SMTP_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"📧 ❌ Erreur SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"📧 ❌ Erreur inattendue lors de l'envoi d'email: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NOTIFICATION TEMPLATES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def notify_ticket_status_change(
    to_email: str,
    client_name: str,
    ticket_id: int,
    ticket_subject: str,
    old_status: str,
    new_status: str,
) -> bool:
    """Send email when a ticket status changes."""
    content = f"""
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Bonjour <strong>{client_name}</strong>,
    </p>
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Le statut de votre ticket a été mis à jour :
    </p>

    <div style="background:#f8fafc;border-radius:12px;padding:24px;margin:0 0 24px;
                border-left:4px solid #6366f1;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
            {_info_row("Ticket", f"#{ticket_id}")}
            {_info_row("Sujet", ticket_subject)}
            {_info_row("Ancien statut", _status_badge(old_status))}
            {_info_row("Nouveau statut", _status_badge(new_status))}
        </table>
    </div>

    <p style="color:#475569;font-size:14px;line-height:1.7;margin:0 0 16px;">
        {"🎉 Votre problème a été résolu. Si vous rencontrez encore des difficultés, n'hésitez pas à rouvrir le ticket via le portail client."
         if new_status == "resolved" else
         "⏳ Nous attendons votre réponse pour continuer le traitement de votre demande."
         if new_status == "waiting_customer" else
         "Notre équipe travaille activement sur votre demande."}
    </p>

    <div style="text-align:center;margin:32px 0 0;">
        <a href="http://localhost:3000/tickets" style="display:inline-block;padding:12px 32px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
                          color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;
                          font-size:14px;box-shadow:0 4px 12px rgba(99,102,241,0.3);">
            Voir mon ticket dans le portail
        </a>
    </div>
    """

    subject = f"🎫 Ticket #{ticket_id} — Statut mis à jour : {STATUS_LABELS.get(new_status, new_status)}"
    html = _base_template(f"Mise à jour du ticket #{ticket_id}", content)
    return send_email(to_email, subject, html)


def notify_ticket_new_message(
    to_email: str,
    client_name: str,
    ticket_id: int,
    ticket_subject: str,
    agent_name: str,
    message_preview: str,
) -> bool:
    """Send email when a new message is added to a ticket."""
    # Truncate message preview
    preview = message_preview[:200] + "..." if len(message_preview) > 200 else message_preview

    content = f"""
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Bonjour <strong>{client_name}</strong>,
    </p>
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Un nouveau message a été ajouté à votre ticket :
    </p>

    <div style="background:#f8fafc;border-radius:12px;padding:24px;margin:0 0 24px;
                border-left:4px solid #10b981;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
            {_info_row("Ticket", f"#{ticket_id}", "#10b981")}
            {_info_row("Sujet", ticket_subject, "#10b981")}
            {_info_row("De", agent_name, "#10b981")}
        </table>
    </div>

    <div style="background:#f0fdf4;border-radius:12px;padding:20px;margin:0 0 24px;
                border:1px solid #bbf7d0;">
        <p style="margin:0;color:#166534;font-size:14px;line-height:1.6;font-style:italic;">
            "{preview}"
        </p>
    </div>

    <div style="text-align:center;margin:32px 0 0;">
        <a href="http://localhost:3000/tickets" style="display:inline-block;padding:12px 32px;background:linear-gradient(135deg,#10b981,#059669);
                          color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;
                          font-size:14px;box-shadow:0 4px 12px rgba(16,185,129,0.3);">
            Répondre au message
        </a>
    </div>
    """

    subject = f"💬 Nouveau message sur le ticket #{ticket_id} — {ticket_subject}"
    html = _base_template(f"Nouveau message — Ticket #{ticket_id}", content)
    return send_email(to_email, subject, html)


def notify_new_quote(
    to_email: str,
    client_name: str,
    quote_reference: str,
    quote_amount: float,
    deal_name: str,
) -> bool:
    """Send email when a new quote is created for the client's account."""
    content = f"""
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Bonjour <strong>{client_name}</strong>,
    </p>
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Un nouveau devis a été créé pour votre entreprise :
    </p>

    <div style="background:#f8fafc;border-radius:12px;padding:24px;margin:0 0 24px;
                border-left:4px solid #ec4899;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
            {_info_row("Référence", quote_reference, "#ec4899")}
            {_info_row("Projet", deal_name, "#ec4899")}
            {_info_row("Montant", f"<strong style='font-size:18px;color:#ec4899;'>{quote_amount:,.2f} DT</strong>", "#ec4899")}
        </table>
    </div>

    <p style="color:#475569;font-size:14px;line-height:1.7;margin:0 0 16px;">
        Vous pouvez consulter ce devis en détail depuis votre portail client.
    </p>

    <div style="text-align:center;margin:32px 0 0;">
        <a href="http://localhost:3000/quotes" style="display:inline-block;padding:12px 32px;background:linear-gradient(135deg,#ec4899,#db2777);
                          color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;
                          font-size:14px;box-shadow:0 4px 12px rgba(236,72,153,0.3);">
            Voir mes devis
        </a>
    </div>
    """

    subject = f"📄 Nouveau devis {quote_reference} — {quote_amount:,.2f} DT"
    html = _base_template(f"Nouveau devis — {quote_reference}", content)
    return send_email(to_email, subject, html)


def notify_welcome_client(
    to_email: str,
    client_name: str,
    company_name: str,
) -> bool:
    """Send a welcome email to a new client user."""
    content = f"""
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Bonjour <strong>{client_name}</strong>,
    </p>
    <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px;">
        Bienvenue sur le portail client de <strong>FRS — IT Development Company</strong> ! 🎉
    </p>

    <div style="background:linear-gradient(135deg,#eff6ff,#f0fdf4);border-radius:12px;
                padding:24px;margin:0 0 24px;border:1px solid #e2e8f0;">
        <h3 style="margin:0 0 16px;color:#1e293b;font-size:16px;">
            ✨ Ce que vous pouvez faire :
        </h3>
        <ul style="margin:0;padding:0 0 0 20px;color:#475569;font-size:14px;line-height:2;">
            <li>📊 Consulter votre <strong>tableau de bord</strong> personnalisé</li>
            <li>🎫 Créer et suivre vos <strong>tickets de support</strong></li>
            <li>📄 Consulter vos <strong>devis</strong></li>
            <li>🤖 Utiliser notre <strong>chatbot IA</strong> pour des réponses rapides</li>
        </ul>
    </div>

    <div style="background:#f8fafc;border-radius:12px;padding:24px;margin:0 0 24px;
                border-left:4px solid #6366f1;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
            {_info_row("Entreprise", company_name)}
            {_info_row("Email", to_email)}
            {_info_row("Support", "Dimanche — Jeudi, 8h — 17h")}
        </table>
    </div>

    <div style="text-align:center;margin:32px 0 0;">
        <a href="http://localhost:3000/" style="display:inline-block;padding:12px 32px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
                          color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;
                          font-size:14px;box-shadow:0 4px 12px rgba(99,102,241,0.3);">
            Accéder au portail client
        </a>
    </div>
    """

    subject = "🎉 Bienvenue sur le portail client FRS !"
    html = _base_template("Bienvenue sur le portail client !", content)
    return send_email(to_email, subject, html)
