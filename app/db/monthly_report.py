from pydantic import BaseModel
from .models import User, Issue, Project, IssuePriority, IssueStatus
from sqlalchemy.orm import Session
from sqlalchemy import select

from datetime import datetime, timezone

from collections import defaultdict

from typing import List

class IssueReport(BaseModel):
    key: str = "" # PROJ-1
    title: str = ""
    description: str = ""
    creator: str = "" #username
    priority: IssuePriority = IssuePriority.MEDIUM
    status: IssueStatus = IssueStatus.OPEN

class UserIssueReport(BaseModel):
    username: str = ""
    open_issues: List[IssueReport] = []


class ProjectReport(BaseModel):
    name: str = ""
    open_issues: int = 0
    created_issues_month: int = 0
    closed_issues_month: int = 0
    user_issues: List[UserIssueReport] = []


class MonthlyReport(BaseModel):
    title: str = ""
    username: str = ""
    projects: List[ProjectReport] = []

def generate_issue_report(session: Session, proj_key: str, issueDB: Issue) -> IssueReport:
    report = IssueReport()
    report.key = f"{proj_key}-{issueDB.key}"
    report.title = issueDB.title
    report.description = issueDB.description
    report.creator = issueDB.author.username
    report.priority = issueDB.priority
    report.status = issueDB.status

    return report

def generate_user_issue_report(session: Session, username: str, proj_key: str, issuesDB: list[Issue]) -> UserIssueReport:
    report = UserIssueReport()
    report.username = username

    for issueDB in issuesDB:
        report.open_issues.append(generate_issue_report(session, proj_key, issueDB))

    return report

def generate_project_report(session: Session, projectDB: Project) -> ProjectReport:
    report = ProjectReport()
    report.name = projectDB.title

    year = datetime.today().year
    month = datetime.today().month

    issuesByUser = defaultdict(list)

    for issueDB in projectDB.issues:
        if issueDB.created_at.year == year and issueDB.created_at.month == month:
                report.created_issues_month += 1

        match issueDB.status:
            case IssueStatus.OPEN:
                report.open_issues += 1
                issuesByUser[issueDB.assigned.username].append(issueDB)
            case IssueStatus.CLOSED:
                if issueDB.updated_at.year == year and issueDB.updated_at.month == month:
                    report.closed_issues_month += 1

    for username, issues in issuesByUser.items():
        report.user_issues.append(generate_user_issue_report(session, username, projectDB.key, issues))

    return report

def generate_monthly_report(session: Session, user_id: str) -> MonthlyReport:
    userQuery = select(User).where(User.public_id == user_id)
    userDB = session.execute(userQuery).scalars().first()
    if not userDB:
        # TODO return proper error
        return False
    
    report = MonthlyReport()
    report.title = f"FLYSWATTER MONTHLY REPORT - {userDB.username} - {datetime.now():%Y-%m}"
    report.username = userDB.username

    for projectDB in userDB.projects:
        report.projects.append(generate_project_report(session, projectDB))

    return report

def print_monthly_report(report: MonthlyReport):
    print(report.title)
    for project in report.projects:
        print(f"----Project {project.name}")
        print(f"--------Total Open Issues: {project.open_issues}")
        print(f"--------Created Issues this month: {project.created_issues_month}")
        print(f"--------Closed Issues this month: {project.closed_issues_month}")
        print("--------Open Issues by User:")
        for userIssue in project.user_issues:
            print(f"--------{userIssue.username}")
            for issue in userIssue.open_issues:
                print(f"------------{issue.key} - {issue.title}")
                print(f"------------Created by: {issue.creator}")
                print(f"------------Priority: {issue.priority}")
                print(f"------------Status: {issue.status}")