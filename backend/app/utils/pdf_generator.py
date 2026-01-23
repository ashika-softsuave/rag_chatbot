from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os


PDF_DIR = "generated_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)


def generate_joining_pdf(employee):
    file_path = f"{PDF_DIR}/joining_{employee.id}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Joining Letter")

    c.setFont("Helvetica", 11)
    y = height - 100

    lines = [
        f"Date: {datetime.utcnow().strftime('%d %B %Y')}",
        "",
        f"Dear {employee.name},",
        "",
        "We are pleased to inform you that you have successfully cleared",
        "the onboarding criteria and are selected to join our organization.",
        "",
        f"Tech Stack: {employee.tech_stack.capitalize()}",
        f"Seat Number: {employee.seat_number or 'To be assigned on joining day'}",
        "",
        "Reporting Instructions:",
        "- Report to the HR desk on your joining day",
        "- Carry a government-issued ID proof",
        "- Laptop and access details will be provided",
        "",
        "We look forward to welcoming you on board.",
        "",
        "Warm regards,",
        "HR Team",
        "SoftSuave Technologies"
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 18

    c.showPage()
    c.save()

    return file_path


def generate_rejection_pdf(employee):
    file_path = f"{PDF_DIR}/rejection_{employee.id}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Application Status Update")

    c.setFont("Helvetica", 11)
    y = height - 100

    lines = [
        f"Date: {datetime.utcnow().strftime('%d %B %Y')}",
        "",
        f"Dear {employee.name},",
        "",
        "Thank you for your interest in joining our organization",
        "and for taking the time to complete the onboarding process.",
        "",
        "After careful review, we regret to inform you that we",
        "will not be able to proceed further with your application at this time.",
        "",
        "This decision does not reflect your potential or capabilities.",
        "We encourage you to continue developing your skills.",
        "",
        "You may reapply after a cooling period of 6 months,",
        "at which point we would be happy to review your profile again.",
        "",
        "We wish you the very best in your future endeavors.",
        "",
        "Warm regards,",
        "HR Team",
        "SoftSuave Technologies"
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 18

    c.showPage()
    c.save()

    return file_path
