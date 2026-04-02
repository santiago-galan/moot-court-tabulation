from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.ruleset import Ruleset
from server.schemas.ruleset import RulesetCreate, RulesetRead, RulesetUpdate

router = APIRouter(prefix="/rulesets", tags=["rulesets"])


@router.get("/", response_model=list[RulesetRead])
def list_rulesets(db: Session = Depends(get_db)):
    return db.query(Ruleset).all()


@router.post("/", response_model=RulesetRead, status_code=201)
def create_ruleset(payload: RulesetCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["scoring_criteria"] = [c.model_dump() for c in payload.scoring_criteria]
    ruleset = Ruleset(**data)
    db.add(ruleset)
    db.commit()
    db.refresh(ruleset)
    return ruleset


@router.get("/{ruleset_id}", response_model=RulesetRead)
def get_ruleset(ruleset_id: int, db: Session = Depends(get_db)):
    ruleset = db.get(Ruleset, ruleset_id)
    if not ruleset:
        raise HTTPException(404, "Ruleset not found")
    return ruleset


@router.patch("/{ruleset_id}", response_model=RulesetRead)
def update_ruleset(ruleset_id: int, payload: RulesetUpdate, db: Session = Depends(get_db)):
    ruleset = db.get(Ruleset, ruleset_id)
    if not ruleset:
        raise HTTPException(404, "Ruleset not found")
    updates = payload.model_dump(exclude_unset=True)
    if "scoring_criteria" in updates and updates["scoring_criteria"] is not None:
        updates["scoring_criteria"] = [c.model_dump() for c in payload.scoring_criteria]
    for k, v in updates.items():
        setattr(ruleset, k, v)
    db.commit()
    db.refresh(ruleset)
    return ruleset


@router.delete("/{ruleset_id}", status_code=204)
def delete_ruleset(ruleset_id: int, db: Session = Depends(get_db)):
    ruleset = db.get(Ruleset, ruleset_id)
    if not ruleset:
        raise HTTPException(404, "Ruleset not found")
    db.delete(ruleset)
    db.commit()
