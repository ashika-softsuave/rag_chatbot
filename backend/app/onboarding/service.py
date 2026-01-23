from backend.app.db.models.employee import Employee
from backend.app.onboarding.constants import ONBOARDING_STEPS, TECH_STACKS
from backend.app.onboarding.seat_allocator import allocate_seat

from backend.app.utils.pdf_generator import (
    generate_joining_pdf,
    generate_rejection_pdf
)
from backend.app.utils.email_sender import send_email_with_pdf


# HELPERS

def get_or_create_employee(db, user):
    employee = db.query(Employee).filter(Employee.email == user.email).first()

    if not employee:
        employee = Employee(
            email=user.email,
            onboarding_state={
                "active": False,
                "paused": False,
                "step_index": 0,
                "data": {}
        }
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)

    return employee


def get_next_question(step: str) -> str:
    questions = {
        "name": "What is your full name?",
        "email": "Please enter your email address.",
        "phone": "Please enter your phone number.",
        "tech_stack": "Which tech stack do you work in? (python / java / node / qa)",
        "tenth_percentage": "What is your 10th percentage?",
        "twelfth_percentage": "What is your 12th percentage?",
        "confirm": "Do you want to submit your details? (yes/no)"
    }
    return questions[step]


def validate_input(step: str, value: str):
    if step == "name" and not value.strip():
        return False, "Name cannot be empty"

    if step == "email":
        if "@" not in value or "." not in value:
            return False, "Please enter a valid email address"

    if step == "phone":
        if not value.isdigit() or len(value) < 10:
            return False, "Please enter a valid phone number"

    if step == "tech_stack":
        if value.lower() not in TECH_STACKS:
            return False, "Invalid tech stack. Choose from python, java, node, qa"

    if step in ["tenth_percentage", "twelfth_percentage"]:
        try:
            percentage = float(value)
            if percentage < 0 or percentage > 100:
                return False, "Percentage must be between 0 and 100"
        except ValueError:
            return False, "Please enter a valid number"

    if step == "confirm":
        if value.lower() not in ["yes", "no"]:
            return False, "Please type yes or no"

    return True, None


# SERVICES

def start_onboarding_service(db, current_user):
    employee = get_or_create_employee(db, current_user)

    employee.onboarding_state = {
        "step_index": 0,
        "data": {}
    }
    db.commit()

    first_step = ONBOARDING_STEPS[0]

    return {
        "message": get_next_question(first_step),
        "step": first_step
    }


def onboarding_next_service(db, current_user, user_input: str):
    employee = get_or_create_employee(db, current_user)
    state = dict(employee.onboarding_state)

    step_index = state["step_index"]

    if step_index >= len(ONBOARDING_STEPS):
        return {
            "message": "Onboarding already completed.",
            "step": "completed",
            "completed": True
        }

    step = ONBOARDING_STEPS[step_index]

    is_valid, error = validate_input(step, user_input)
    if not is_valid:
        return {
            "message": error,
            "step": step,
            "completed": False
        }

    state["data"][step] = user_input
    state["step_index"] += 1

    employee.onboarding_state = state
    db.commit()

    # FINAL STEP
    if state["step_index"] >= len(ONBOARDING_STEPS):
        data = state["data"]

        employee.name = data["name"]
        employee.phone = data["phone"]
        employee.email = current_user.email
        employee.tech_stack = data["tech_stack"].lower()

        tenth = float(data["tenth_percentage"])
        twelfth = float(data["twelfth_percentage"])

        employee.eligibility_status = (
            "selected" if tenth > 70 and twelfth > 70 else "rejected"
        )

        # SELECTED
        if employee.eligibility_status == "selected":
            seat_number = allocate_seat(db, employee.tech_stack, employee.id)
            employee.seat_number = seat_number

            pdf_path = generate_joining_pdf(employee)
            subject = "Joining Confirmation – SoftSuave Technologies"

            body = (
                f"Hi {employee.name},\n\n"
                "We are pleased to inform you that you have successfully cleared the onboarding process.\n\n"
                f"Seat Number: {seat_number or 'To be assigned'}\n"
                f"Tech Stack: {employee.tech_stack.capitalize()}\n\n"
                "Please find your joining letter attached.\n\n"
                "Regards,\nHR Team\nSoftSuave Technologies"
            )

        # REJECTED
        else:
            pdf_path = generate_rejection_pdf(employee)
            subject = "Application Update – SoftSuave Technologies"

            body = (
                f"Hi {employee.name},\n\n"
                "Thank you for your interest.\n\n"
                "We regret to inform you that we will not proceed further at this time.\n\n"
                "Regards,\nHR Team\nSoftSuave Technologies"
            )

        send_email_with_pdf(
            to_email=employee.email,
            subject=subject,
            body=body,
            pdf_path=pdf_path
        )

        db.commit()

        return {
            "message": (
                "Congratulations! You are eligible for onboarding."
                if employee.eligibility_status == "selected"
                else "Thank you for your interest. We will not proceed further at this time."
            ),
            "step": "completed",
            "completed": True
        }

    #  NEXT QUESTION
    next_step = ONBOARDING_STEPS[state["step_index"]]

    return {
        "message": get_next_question(next_step),
        "step": next_step,
        "completed": False
    }


def reset_onboarding_service(db, current_user):
    employee = get_or_create_employee(db, current_user)

    employee.onboarding_state = {
        "started": False,
        "step_index": 0,
        "data": {},
        "paused": False
    }
    employee.eligibility_status = None
    employee.seat_number = None

    db.commit()

    return {"message": "Onboarding reset successfully"}
