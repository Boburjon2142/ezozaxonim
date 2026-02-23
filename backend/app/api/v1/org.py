import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.schemas.org import InviteMemberRequest, OrgAggregateOut, OrganizationCreate
from app.services.org_analytics import org_aggregate_metrics

router = APIRouter(prefix="/org", tags=["organization"])


def _ensure_org_role(db: Session, user_id: str, org_id: str, allowed_roles: set[str]) -> None:
    member = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == org_id, OrganizationMember.user_id == user_id)
        .first()
    )
    if not member or member.role not in allowed_roles:
        raise HTTPException(status_code=403, detail={"code": "forbidden", "message": "Insufficient organization permissions"})


@router.post("")
def create_org(payload: OrganizationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    org = Organization(name=payload.name)
    db.add(org)
    db.flush()
    db.add(OrganizationMember(organization_id=org.id, user_id=current_user.id, role="org_admin"))
    db.commit()
    return {"id": org.id, "name": org.name}


@router.post("/{org_id}/invite")
def invite_member(org_id: str, payload: InviteMemberRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_org_role(db, current_user.id, org_id, {"org_admin"})
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": "User not found"})

    exists = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == org_id, OrganizationMember.user_id == user.id)
        .first()
    )
    if exists:
        return {"status": "already_member"}

    db.add(OrganizationMember(organization_id=org_id, user_id=user.id, role=payload.role))
    db.commit()
    return {"status": "invited"}


@router.get("/{org_id}/dashboard", response_model=OrgAggregateOut)
def org_dashboard(org_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_org_role(db, current_user.id, org_id, {"org_admin", "hr_viewer"})
    return OrgAggregateOut(**org_aggregate_metrics(db, org_id))


@router.get("/{org_id}/report.csv")
def report_csv(org_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_org_role(db, current_user.id, org_id, {"org_admin", "hr_viewer"})
    m = org_aggregate_metrics(db, org_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value", "generated_at"])
    now = datetime.utcnow().isoformat()
    for k in ["avg_work_hours", "avg_break_compliance", "avg_stress", "burnout_risk_index"]:
        writer.writerow([k, m[k], now])

    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=lifepause_org_report.csv"})


@router.get("/{org_id}/report.pdf")
def report_pdf_stub(org_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), _: str = Query(default="summary")):
    _ensure_org_role(db, current_user.id, org_id, {"org_admin", "hr_viewer"})
    m = org_aggregate_metrics(db, org_id)
    content = f"LifePause Org Summary\nOrg: {org_id}\nWork hours: {m['avg_work_hours']}\nStress: {m['avg_stress']}"
    return StreamingResponse(iter([content.encode("utf-8")]), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=lifepause_org_summary.pdf"})
