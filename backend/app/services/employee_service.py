"""
Employee Service — CRUD for internal team members.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.employee import Employee

logger = logging.getLogger(__name__)


class EmployeeService:
    """Manages internal team member records for an organization."""

    @staticmethod
    def list_employees(
        org_id: str,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> dict:
        query = select(Employee).where(Employee.organization_id == uuid.UUID(org_id))
        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                db.or_(
                    func.lower(Employee.name).like(term),
                    Employee.phone.like(term),
                    func.lower(Employee.email).like(term),
                    func.lower(Employee.department).like(term),
                )
            )
        total = db.session.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar() or 0
        employees = (
            db.session.execute(query.order_by(Employee.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
            .scalars().all()
        )
        return {
            "data": [
                {
                    "id": str(e.id), "organization_id": str(e.organization_id),
                    "name": e.name, "email": e.email, "phone": e.phone,
                    "department": e.department, "role": e.role, "status": e.status,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                    "updated_at": e.updated_at.isoformat() if e.updated_at else None,
                }
                for e in employees
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_employee(employee_id: str) -> Optional[Employee]:
        return db.session.get(Employee, uuid.UUID(employee_id))

    @staticmethod
    def create_employee(org_id: str, **kwargs) -> Employee:
        employee = Employee(organization_id=uuid.UUID(org_id), **kwargs)
        db.session.add(employee)
        db.session.commit()
        logger.info("Created employee %s (%s)", employee.name, employee.id)
        return employee

    @staticmethod
    def update_employee(employee_id: str, **kwargs) -> Optional[Employee]:
        employee = db.session.get(Employee, uuid.UUID(employee_id))
        if not employee:
            return None
        for key, value in kwargs.items():
            if hasattr(employee, key) and key not in ("id", "organization_id"):
                setattr(employee, key, value)
        db.session.commit()
        return employee

    @staticmethod
    def delete_employee(employee_id: str) -> bool:
        employee = db.session.get(Employee, uuid.UUID(employee_id))
        if not employee:
            return False
        db.session.delete(employee)
        db.session.commit()
        return True
