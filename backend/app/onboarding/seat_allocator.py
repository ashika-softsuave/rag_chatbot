from sqlalchemy.orm import Session
from backend.app.db.models.seating import Seating

# def allocate_seat(db: Session, tech_stack: str, employee_id: int):
#     seat = (
#         db.query(Seating)
#         .filter(
#             Seating.tech_stack == tech_stack,
#             Seating.employee_id.is_(None)
#         )
#         .order_by(Seating.row_number, Seating.column_number)
#         .with_for_update(skip_locked=True)
#         .first()
#     )
#
#     if not seat:
#         return None
#
#     seat.employee_id = employee_id
#     db.commit()
#
#     return f"R{seat.row_number}C{seat.column_number}"
#
def allocate_seat(db, tech_stack: str, employee_id: int):
    seat = (
        db.query(Seating)
        .filter(
            Seating.tech_stack == tech_stack,
            Seating.employee_id.is_(None)
        )
        .order_by(
            Seating.row_number.asc(),
            Seating.column_number.asc()
        )
        .first()
    )

    if not seat:
        return None  # 🚨 no seat available

    seat.employee_id = employee_id
    db.commit()

    return {
        "row": seat.row_number,
        "column": seat.column_number
    }
