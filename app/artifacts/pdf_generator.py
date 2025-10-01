from fpdf import FPDF
from app.db.monthly_report import MonthlyReport
from dataclasses import dataclass, asdict


@dataclass
class rgb:
    r: float = 0
    g: float = 0
    b: float = 0

def monthly_report_pdf(report: MonthlyReport, filename: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style='B')

    pdfPallete = [
        rgb(25, 24, 59),   # box bg
        rgb(161, 194, 189),   # extra
        rgb(112, 137, 147),  # text outside box
        rgb(231, 242, 239)  # text in box
    ]

    pdf.set_fill_color(**asdict(pdfPallete[0])) #asdict returns a dictionary, ** unpacks the dict into named args

    pdf.set_line_width(3)
    titleWith = pdf.get_string_width(report.title) + 50
    pdf.set_text_color(**asdict(pdfPallete[3]))
    pdf.cell(titleWith, 10, report.title, ln=True, fill=True, align="C")
    pdf.ln(20)


    if not report.projects:
        pdf.set_text_color(**asdict(pdfPallete[2]))
        pdf.cell(40, 10, "No projects found", ln=True)
    else:
        for project in report.projects:
            pdf.set_text_color(**asdict(pdfPallete[2]))
            pdf.set_font("Arial", size=16, style='B')
            pdf.cell(40, 10, f"Project Overview: {project.name}", ln=True)

            pdf.set_font("Arial", size=12)
            pdf.set_text_color(**asdict(pdfPallete[3]))
            pdf.cell(60, 10, "Total Open Issues", fill=True)
            pdf.cell(10, 10, f"{project.open_issues}", ln=True, fill=True, align="C")
            pdf.cell(60, 10, "Created Issues this month", fill=True)
            pdf.cell(10, 10, f"{project.created_issues_month}", ln=True, fill=True, align="C")
            pdf.cell(60, 10, "Closed Issues this month", fill=True)
            pdf.cell(10, 10, f"{project.closed_issues_month}", ln=True, fill=True, align="C")

            pdf.ln(4)

            pdf.set_font("Arial", size=12, style='B')
            pdf.set_text_color(**asdict(pdfPallete[2]))
            pdf.cell(40, 10, f"Current Open Issues", ln=True)
            for userIssue in project.user_issues:
                pdf.set_text_color(**asdict(pdfPallete[2]))
                pdf.set_font("Arial", size=12, style='B')
                pdf.cell(40, 10, f"{userIssue.username}", ln=True)

                for issue in userIssue.open_issues:
                    pdf.set_text_color(**asdict(pdfPallete[3]))
                    pdf.set_font("Arial", size=10, style='B')
                    pdf.cell(10)
                    pdf.cell(50, 10, f"{issue.key} - {issue.title}", fill=True)

                    pdf.set_font("Arial", size=10)
                    pdf.cell(40, 10, f"Created by: {issue.creator}", fill=True)
                    pdf.cell(40, 10, f"Priority: {issue.priority}", fill=True)
                    pdf.cell(30, 10, f"Status: {issue.status}", ln=True, fill=True)
                    pdf.ln(1)
            pdf.ln(5)
            pdf.set_fill_color(**asdict(pdfPallete[1]))
            pdf.cell(180, 1, "", border=5, ln=True, fill=True, align="R")
            pdf.set_fill_color(**asdict(pdfPallete[0]))
            pdf.ln(5)

    pdf.output(filename)
