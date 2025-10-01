from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.create_database import create_db
from app.db.factory import create_comment, create_issue, create_project, create_user
from app.db.models import IssuePriority, IssueStatus


def seed_db():
    create_db()
    engine = create_engine(settings.database.build_url(), future=True)
    Session = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    demoSession = Session()

    # -----------------USERS--------------------
    adminUser = create_user(admin=True)
    disabledUser = create_user(
        name="Rueben Johnson",
        username="rjohnson",
        email="rjohnson@jdoe.com",
        disabled=True,
    )
    nonAdminData = [
        {
            "name": "Alice Megan",
            "username": "amegan",
            "email": "amegan@jdoe.com",
            "password": "secret2",
        },
        {
            "name": "Livia Bruce",
            "username": "lbruce",
            "email": "lbruce@jdoe.com",
            "password": "secret3",
        },
        {
            "name": "Aliya Willis",
            "username": "awillis",
            "email": "awillis@jdoe.com",
            "password": "secret4",
        },
        {
            "name": "Leon Tanner",
            "username": "ltanner",
            "email": "ltanner@jdoe.com",
            "password": "secret5",
        },
        {
            "name": "Denis Lambert",
            "username": "dlambert",
            "email": "dlambert@jdoe.com",
            "password": "secret6",
        },
        {
            "name": "Kara Le",
            "username": "kle",
            "email": "kle@jdoe.com",
            "password": "secret7",
        },
    ]
    nonAdminUsers = [create_user(**userDict) for userDict in nonAdminData]
    demoSession.add(adminUser)
    demoSession.add(disabledUser)
    for user in nonAdminUsers:
        demoSession.add(user)

    # -----------------PROJECTS--------------------
    projectData = [
        (adminUser, {"title": "Nimbus", "key": "NIM"}),
        (nonAdminUsers[0], {"title": "Ironleaf", "key": "IRON"}),
        (nonAdminUsers[0], {"title": "AeroTrack", "key": "AERO"}),
        (nonAdminUsers[1], {"title": "Luma", "key": "LUM"}),
        (nonAdminUsers[2], {"title": "Stonepath", "key": "STON"}),
    ]
    projects = [create_project(author, **projDict) for author, projDict in projectData]
    for project in projects:
        demoSession.add(project)

    # -----------------ISSUES--------------------
    issueData = [
        (
            projects[0],
            nonAdminUsers[0],
            nonAdminUsers[0],
            {
                "title": "MobileLogin",
                "key": "1",
                "description": "Login doesn’t work on mobile",
            },
        ),
        (
            projects[0],
            nonAdminUsers[1],
            nonAdminUsers[2],
            {
                "title": "FilterBug",
                "key": "2",
                "description": "Search results not updating after filter applied",
            },
        ),
        (
            projects[0],
            nonAdminUsers[1],
            nonAdminUsers[3],
            {
                "title": "SafariUpload",
                "key": "3",
                "description": "Profile picture upload fails on Safari",
                "status": IssueStatus.IN_PROGRESS,
                "priority": IssuePriority.LOW,
            },
        ),
        (
            projects[1],
            nonAdminUsers[1],
            nonAdminUsers[3],
            {
                "title": "DupNotify",
                "key": "1",
                "description": "Notifications show duplicates",
                "status": IssueStatus.IN_PROGRESS,
                "priority": IssuePriority.HIGH,
            },
        ),
        (
            projects[1],
            nonAdminUsers[1],
            nonAdminUsers[4],
            {
                "title": "ResetEmail",
                "key": "2",
                "description": "Password reset email not sent",
                "status": IssueStatus.CLOSED,
                "priority": IssuePriority.LOW,
            },
        ),
        (
            projects[1],
            nonAdminUsers[1],
            nonAdminUsers[2],
            {
                "title": "DarkToggle",
                "key": "3",
                "description": "Dark mode toggle doesn’t save preference",
            },
        ),
        (
            projects[2],
            nonAdminUsers[1],
            nonAdminUsers[1],
            {
                "title": "TabletCheckout",
                "key": "1",
                "description": "Checkout button unresponsive on tablet",
            },
        ),
        (
            projects[2],
            nonAdminUsers[2],
            nonAdminUsers[3],
            {
                "title": "ScrollStop",
                "key": "2",
                "description": "Infinite scroll stops loading after page 3",
                "status": IssueStatus.IN_PROGRESS,
                "priority": IssuePriority.LOW,
            },
        ),
        (
            projects[2],
            nonAdminUsers[2],
            nonAdminUsers[5],
            {
                "title": "InvalidEmail",
                "key": "3",
                "description": "Form validation allows invalid email",
            },
        ),
        (
            projects[3],
            nonAdminUsers[2],
            nonAdminUsers[5],
            {
                "title": "MenuOverlap",
                "key": "1",
                "description": "Dropdown menu overlaps footer",
            },
        ),
        (
            projects[3],
            nonAdminUsers[2],
            nonAdminUsers[4],
            {
                "title": "FastCarousel",
                "key": "2",
                "description": "Image carousel auto-plays too fast",
                "status": IssueStatus.RESOLVED,
                "priority": IssuePriority.HIGH,
            },
        ),
        (
            projects[3],
            nonAdminUsers[2],
            nonAdminUsers[4],
            {
                "title": "LatePush",
                "key": "3",
                "description": "Push notifications delayed by several minutes",
                "status": IssueStatus.IN_PROGRESS,
                "priority": IssuePriority.URGENT,
            },
        ),
        (
            projects[3],
            nonAdminUsers[2],
            nonAdminUsers[3],
            {
                "title": "TextCutoff",
                "key": "4",
                "description": "Text input cuts off characters in landscape mode",
            },
        ),
        (
            projects[3],
            nonAdminUsers[3],
            nonAdminUsers[3],
            {
                "title": "CartCurrency",
                "key": "5",
                "description": "Wrong currency displayed in cart",
            },
        ),
        (
            projects[4],
            nonAdminUsers[3],
            nonAdminUsers[2],
            {
                "title": "KeybindFail",
                "key": "1",
                "description": "Keyboard shortcuts not working in Firefox",
            },
        ),
        (
            projects[4],
            nonAdminUsers[3],
            nonAdminUsers[1],
            {
                "title": "StickyTooltip",
                "key": "2",
                "description": "Tooltip remains visible after hover out",
                "status": IssueStatus.IN_PROGRESS,
                "priority": IssuePriority.URGENT,
            },
        ),
        (
            projects[4],
            nonAdminUsers[3],
            nonAdminUsers[2],
            {
                "title": "BrokenDownload",
                "key": "3",
                "description": "File download link broken on Windows",
                "status": IssueStatus.RESOLVED,
                "priority": IssuePriority.URGENT,
            },
        ),
        (
            projects[4],
            nonAdminUsers[3],
            nonAdminUsers[5],
            {
                "title": "LostComment",
                "key": "4",
                "description": "Comment form loses text when refreshing",
                "status": IssueStatus.RESOLVED,
                "priority": IssuePriority.URGENT,
            },
        ),
        (
            projects[4],
            nonAdminUsers[3],
            nonAdminUsers[4],
            {
                "title": "DateBlock",
                "key": "5",
                "description": "Date picker doesn’t allow selecting today",
                "status": IssueStatus.CLOSED,
                "priority": IssuePriority.HIGH,
            },
        ),
    ]
    issues = [
        create_issue(project, author, assigned, **issueDict)
        for project, author, assigned, issueDict in issueData
    ]
    for issue in issues:
        demoSession.add(issue)

    # -----------------COMMENTS--------------------
    commentData = [
        (issues[7], nonAdminUsers[2], "Still broken"),
        (issues[3], nonAdminUsers[5], "Works on desktop"),
        (issues[12], nonAdminUsers[1], "Please fix soon"),
        (issues[0], nonAdminUsers[3], "Not reproducible"),
        (issues[18], nonAdminUsers[4], "Keeps happening"),
        (issues[6], nonAdminUsers[0], "Confirmed bug"),
        (issues[10], nonAdminUsers[2], "Fails again"),
        (issues[5], nonAdminUsers[1], "Seems fine"),
        (issues[14], nonAdminUsers[0], "Any update?"),
        (issues[2], nonAdminUsers[5], "Problem persists"),
        (issues[9], nonAdminUsers[4], "Affects checkout"),
        (issues[8], nonAdminUsers[3], "Cache issue"),
        (issues[1], nonAdminUsers[2], "Needs priority"),
        (issues[13], nonAdminUsers[0], "Error shown"),
        (issues[11], nonAdminUsers[5], "Quick fix?"),
        (issues[16], nonAdminUsers[1], "Reopened bug"),
        (issues[4], nonAdminUsers[2], "Critical issue"),
        (issues[17], nonAdminUsers[4], "Intermittent"),
        (issues[15], nonAdminUsers[3], "App crash"),
        (issues[7], nonAdminUsers[0], "Still failing"),
        (issues[3], nonAdminUsers[5], "Happens again"),
        (issues[10], nonAdminUsers[1], "Unusable"),
        (issues[6], nonAdminUsers[2], "Recheck logs"),
        (issues[0], nonAdminUsers[4], "Same problem"),
        (issues[9], nonAdminUsers[3], "Very annoying"),
        (issues[12], nonAdminUsers[0], "Broken flow"),
        (issues[8], nonAdminUsers[1], "Not fixed"),
        (issues[2], nonAdminUsers[5], "Needs patch"),
        (issues[11], nonAdminUsers[4], "Bug confirmed"),
        (issues[14], nonAdminUsers[2], "Timeout issue"),
        (issues[18], nonAdminUsers[0], "Works once"),
        (issues[1], nonAdminUsers[3], "Fails often"),
        (issues[13], nonAdminUsers[1], "Minor bug"),
        (issues[15], nonAdminUsers[5], "Big blocker"),
        (issues[4], nonAdminUsers[2], "Temporary fix"),
        (issues[17], nonAdminUsers[0], "Occurs daily"),
        (issues[7], nonAdminUsers[4], "Regression"),
        (issues[16], nonAdminUsers[3], "Needs testing"),
        (issues[3], nonAdminUsers[1], "Happens randomly"),
        (issues[5], nonAdminUsers[2], "UI glitch"),
        (issues[9], nonAdminUsers[0], "Not loading"),
        (issues[12], nonAdminUsers[5], "Data lost"),
        (issues[8], nonAdminUsers[4], "Hard to use"),
        (issues[10], nonAdminUsers[3], "Restart fails"),
        (issues[6], nonAdminUsers[1], "Error popup"),
        (issues[18], nonAdminUsers[2], "Happens daily"),
        (issues[0], nonAdminUsers[0], "No workaround"),
        (issues[11], nonAdminUsers[5], "Any ETA?"),
        (issues[14], nonAdminUsers[3], "Still waiting"),
        (issues[2], nonAdminUsers[4], "Please resolve"),
    ]
    comments = [
        create_comment(issue, author, body=body) for issue, author, body in commentData
    ]
    for comment in comments:
        demoSession.add(comment)

    demoSession.commit()

    created = {
        "users": 2 + len(nonAdminUsers),  # + 1 admin + 1 disabled
        "projects": len(projects),
        "issues": len(issues),
        "comments": len(comments),
    }
    print(
        f"Successfully created in {settings.database.build_url()}:\n{created["users"]} users\n{created["projects"]} projects\n{created["issues"]} issues\n{created["comments"]} comments"
    )


if __name__ == "__main__":
    seed_db()
