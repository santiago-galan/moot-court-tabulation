from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.tournament import Tournament
from server.services.email import send_ballot_emails
from server.services.pdf import generate_team_ballot_pdf, generate_tournament_report_pdf

router = APIRouter(prefix="/tournaments/{tournament_id}/reports", tags=["reports"])


@router.get("/ballots/team/{team_id}")
def team_ballot_pdf(tournament_id: int, team_id: int, db: Session = Depends(get_db)):
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    buf = generate_team_ballot_pdf(tournament_id, team_id, db)
    return StreamingResponse(buf, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=ballots_team_{team_id}.pdf"
    })


@router.get("/tournament")
def tournament_report(tournament_id: int, db: Session = Depends(get_db)):
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    buf = generate_tournament_report_pdf(tournament_id, db)
    return StreamingResponse(buf, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=tournament_report_{tournament_id}.pdf"
    })


@router.post("/email-ballots")
def email_ballots(tournament_id: int, db: Session = Depends(get_db)):
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    count = send_ballot_emails(tournament_id, db)
    return {"emails_sent": count}
