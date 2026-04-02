import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from server.config import settings
from server.models.team import Team
from server.services.pdf import generate_team_ballot_pdf


def send_ballot_emails(tournament_id: int, db: Session) -> int:
    if not settings.smtp_host:
        return 0

    teams = db.query(Team).filter(Team.tournament_id == tournament_id).all()
    sent = 0

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        if settings.smtp_port == 587:
            server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)

        for team in teams:
            if not team.contact_email:
                continue
            pdf_buf = generate_team_ballot_pdf(tournament_id, team.id, db)

            msg = MIMEMultipart()
            msg["From"] = settings.smtp_from or settings.smtp_user
            msg["To"] = team.contact_email
            msg["Subject"] = f"Ballot Summary - {team.team_code}"
            msg.attach(MIMEText(
                f"Attached is the ballot summary for team {team.team_code} ({team.school_name}).",
                "plain",
            ))

            attachment = MIMEApplication(pdf_buf.read(), _subtype="pdf")
            attachment.add_header("Content-Disposition", "attachment", filename=f"ballots_{team.team_code}.pdf")
            msg.attach(attachment)

            server.sendmail(msg["From"], [team.contact_email], msg.as_string())
            sent += 1

    return sent
