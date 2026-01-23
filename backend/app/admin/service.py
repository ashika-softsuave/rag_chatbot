from sqlalchemy.orm import Session
from backend.app.db.models.seating import Seating

# def configure_seating_service(payload, db):
#     tech_stacks = payload["tech_stacks"]
#     rows = payload["rows"]
#     cols = payload["columns"]  # 5 seats per row
#
#     for tech in tech_stacks:
#         for r in range(1, rows + 1):
#             for c in range(1, cols + 1):
#                 seat = Seating(
#                     tech_stack=tech,
#                     row_number=r,
#                     column_number=c
#                 )
#                 db.add(seat)
#
#     db.commit()
#     return {
#         "message": "Seating configured successfully",
#         "rows": rows,
#         "columns": cols
#     }
from backend.app.db.models.seating import Seating

def configure_seating(db, tech_stack: str, rows: int, columns: int):
    db.query(Seating).filter(Seating.tech_stack == tech_stack).delete()

    for r in range(rows):
        for c in range(columns):
            db.add(
                Seating(
                    tech_stack=tech_stack,
                    row=r,
                    col=c,
                    employee_id=None
                )
            )

    db.commit()


def seating_status_service(db: Session):
    seats = (
        db.query(Seating)
        .order_by(Seating.row_number, Seating.column_number)
        .all()
    )

    status = {}

    for seat in seats:
        stack = seat.tech_stack.capitalize()
        status.setdefault(stack, [])

        status[stack].append(
            "X" if seat.employee_id is None else seat.employee_id
        )

    return status


def reset_seating_service(db: Session):
    seats = db.query(Seating).all()

    for seat in seats:
        seat.employee_id = None

    db.commit()
    return {"message": "All seats reset successfully"}
