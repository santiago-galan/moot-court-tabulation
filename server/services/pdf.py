import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session, joinedload

from server.models.ballot import Ballot, OralistScore
from server.models.pairing import JudgeAssignment, Pairing
from server.models.round import Round
from server.models.team import Team
from server.models.tournament import Tournament
from server.services.tabulation import compute_standings


def generate_team_ballot_pdf(tournament_id: int, team_id: int, db: Session) -> io.BytesIO:
    tournament = db.query(Tournament).options(joinedload(Tournament.ruleset)).get(tournament_id)
    team = db.query(Team).options(joinedload(Team.oralists)).get(team_id)

    pairings = (
        db.query(Pairing)
        .join(Round)
        .filter(
            Round.tournament_id == tournament_id,
            (Pairing.petitioner_team_id == team_id) | (Pairing.respondent_team_id == team_id),
        )
        .options(
            joinedload(Pairing.judge_assignments)
            .joinedload(JudgeAssignment.ballot)
            .joinedload(Ballot.scores)
            .joinedload(OralistScore.oralist),
            joinedload(Pairing.round),
            joinedload(Pairing.petitioner_team),
            joinedload(Pairing.respondent_team),
        )
        .all()
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=16, spaceAfter=12)
    elements = []

    elements.append(Paragraph(f"{tournament.name} - Ballot Summary", title_style))
    elements.append(Paragraph(f"Team: {team.team_code} ({team.school_name})", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    for p in sorted(pairings, key=lambda x: x.round.round_number):
        side = "Petitioner" if p.petitioner_team_id == team_id else "Respondent"
        opponent = p.respondent_team if p.petitioner_team_id == team_id else p.petitioner_team
        elements.append(Paragraph(
            f"Round {p.round.round_number} ({p.round.round_type}) - {side} vs {opponent.team_code}",
            styles["Heading3"],
        ))

        for ja in p.judge_assignments:
            if not ja.ballot or not ja.ballot.submitted:
                continue
            elements.append(Paragraph(f"Judge: {ja.judge_name or 'Anonymous'}", styles["Normal"]))

            data = [["Oralist", "Criterion", "Score"]]
            for score in sorted(ja.ballot.scores, key=lambda s: (s.oralist.name, s.criterion_name)):
                data.append([score.oralist.name, score.criterion_name, f"{score.score:.1f}"])

            if len(data) > 1:
                t = Table(data, colWidths=[2 * inch, 2.5 * inch, 1 * inch])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ]))
                elements.append(t)
            elements.append(Spacer(1, 8))

        elements.append(Spacer(1, 12))

    doc.build(elements)
    buf.seek(0)
    return buf


def generate_tournament_report_pdf(tournament_id: int, db: Session) -> io.BytesIO:
    tournament = db.query(Tournament).options(joinedload(Tournament.ruleset)).get(tournament_id)
    standings = compute_standings(tournament_id, db)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=12)
    elements = []

    elements.append(Paragraph(f"{tournament.name} - Tournament Results", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Final Standings", styles["Heading2"]))
    data = [["Rank", "Team", "School", "W", "L", "Points", "Pt Diff"]]
    for s in standings:
        data.append([
            str(s.rank),
            s.team_code,
            s.school_name,
            str(s.wins),
            str(s.losses),
            f"{s.total_points:.1f}",
            f"{s.point_differential:+.1f}",
        ])

    t = Table(data, colWidths=[0.5 * inch, 1 * inch, 2 * inch, 0.5 * inch, 0.5 * inch, 0.8 * inch, 0.8 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 1), (2, -1), "LEFT"),
    ]))
    elements.append(t)

    doc.build(elements)
    buf.seek(0)
    return buf
