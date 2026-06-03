"""Test email with FRS Logo."""
from app.shared.email_service import send_email, _base_template

content = """
<p style="color:#475569;font-size:15px;line-height:1.7;">
    Bonjour <strong>Karim Boumediene</strong>,
</p>
<p style="color:#475569;font-size:15px;line-height:1.7;">
    Le statut de votre ticket a été mis à jour :
</p>
<div style="background:#f8fafc;border-radius:12px;padding:24px;margin:0 0 24px;
            border-left:4px solid #10b981;">
    <p style="margin:0;color:#1e293b;font-size:14px;">
        <strong>Ticket #1</strong> — Erreur module comptabilité<br>
        Nouveau statut : <span style="display:inline-block;padding:4px 12px;border-radius:20px;
        font-size:13px;font-weight:600;color:#10b981;background:#ecfdf5;">🟢 Résolu</span>
    </p>
</div>
<p style="color:#475569;font-size:14px;">
    🎉 Votre problème a été résolu ! N'hésitez pas à rouvrir le ticket si nécessaire.
</p>
"""

html = _base_template("Mise à jour du Ticket #1", content)
result = send_email("karim@sonatrach.dz", "🎫 Ticket #1 — Résolu", html)

if result:
    print("✅ EMAIL AVEC LOGO ENVOYE A karim@sonatrach.dz !")
else:
    print("❌ ECHEC")
