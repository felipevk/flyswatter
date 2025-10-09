import sys
import time

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.create_database import create_db
from app.db.factory import (
    create_comment,
    create_issue,
    create_job,
    create_project,
    create_user,
)
from app.db.models import IssuePriority, IssueStatus, JobState
from app.worker.tasks import generate_report


def check_pdf_exists(url: str) -> bool:
    # Ask for the file itself
    response = requests.get(url, stream=True, timeout=10)
    if response.status_code != 200:
        return False

    # Peek at the first 1 KB just to prove we can access it
    for chunk in response.iter_content(1024):
        break  # stop immediately after one chunk

    response.close()
    return True


def seed_db():
    create_db()
    engine = create_engine(settings.database.build_url(), future=True)
    Session = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    demoSession = Session()

    # -----------------USERS--------------------
    userData = [
        {"admin": True},
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
        {
            "name": "Rueben Johnson",
            "username": "rjohnson",
            "email": "rjohnson@jdoe.com",
            "password": "secret8",
            "disabled": True,
        },
        {
            "name": "Iris Caldwell",
            "username": "icaldwell",
            "email": "icaldwell@jdoe.com",
            "password": "secret9",
        },
        {
            "name": "Theo Rivas",
            "username": "trivas",
            "email": "trivas@jdoe.com",
            "password": "secret10",
        },
        {
            "name": "Mila Ortega",
            "username": "mortega",
            "email": "mortega@jdoe.com",
            "password": "secret11",
        },
        {
            "name": "Jonas Fry",
            "username": "jfry",
            "email": "jfry@jdoe.com",
            "password": "secret12",
        },
        {
            "name": "Lara Quinn",
            "username": "lquinn",
            "email": "lquinn@jdoe.com",
            "password": "secret13",
        },
        {
            "name": "Zane Patel",
            "username": "zpatel",
            "email": "zpatel@jdoe.com",
            "password": "secret14",
        },
        {
            "name": "Noah Kim",
            "username": "nkim",
            "email": "nkim@jdoe.com",
            "password": "secret15",
        },
        {
            "name": "Eva Rossi",
            "username": "erossi",
            "email": "erossi@jdoe.com",
            "password": "secret16",
        },
        {
            "name": "Caleb Novak",
            "username": "cnovak",
            "email": "cnovak@jdoe.com",
            "password": "secret17",
        },
        {
            "name": "Priya Das",
            "username": "pdas",
            "email": "pdas@jdoe.com",
            "password": "secret18",
        },
        {
            "name": "Tariq Hassan",
            "username": "thassan",
            "email": "thassan@jdoe.com",
            "password": "secret19",
        },
        {
            "name": "Jade Laurent",
            "username": "jlaurent",
            "email": "jlaurent@jdoe.com",
            "password": "secret20",
        },
        {
            "name": "Ben Adler",
            "username": "badler",
            "email": "badler@jdoe.com",
            "password": "secret21",
        },
        {
            "name": "Aisha Noor",
            "username": "anoor",
            "email": "anoor@jdoe.com",
            "password": "secret22",
        },
        {
            "name": "Mateo Greer",
            "username": "mgreer",
            "email": "mgreer@jdoe.com",
            "password": "secret23",
        },
        {
            "name": "Selene Fox",
            "username": "sfox",
            "email": "sfox@jdoe.com",
            "password": "secret24",
        },
        {
            "name": "Victor Lang",
            "username": "vlang",
            "email": "vlang@jdoe.com",
            "password": "secret25",
        },
        {
            "name": "Rina Solis",
            "username": "rsolis",
            "email": "rsolis@jdoe.com",
            "password": "secret26",
        },
        {
            "name": "Harvey Owen",
            "username": "howen",
            "email": "howen@jdoe.com",
            "password": "secret27",
        },
        {
            "name": "Camila Beck",
            "username": "cbeck",
            "email": "cbeck@jdoe.com",
            "password": "secret28",
        },
    ]
    users = [create_user(**userDict) for userDict in userData]
    for user in users:
        demoSession.add(user)

    # -----------------PROJECTS--------------------
    projectData = [
        (users[0], {"title": "Nimbus", "key": "NIM"}),
        (users[1], {"title": "Ironleaf", "key": "IRON"}),
        (users[2], {"title": "AeroTrack", "key": "AERO"}),
        (users[2], {"title": "Luma", "key": "LUM"}),
        (users[3], {"title": "Stonepath", "key": "STON"}),
        (users[5], {"title": "Bluewave", "key": "BLU"}),
        (users[8], {"title": "Helios", "key": "HEL"}),
        (users[10], {"title": "Everlight", "key": "EVE"}),
        (users[3], {"title": "Quantum", "key": "QNT"}),
        (users[12], {"title": "Obsidian", "key": "OBS"}),
        (users[6], {"title": "Vortex", "key": "VTX"}),
        (users[4], {"title": "SolarEdge", "key": "SOL"}),
        (users[9], {"title": "CryoCore", "key": "CRY"}),
        (users[2], {"title": "PulseNet", "key": "PUL"}),
        (users[13], {"title": "Hydra", "key": "HYD"}),
    ]
    projects = [create_project(author, **projDict) for author, projDict in projectData]
    for project in projects:
        demoSession.add(project)

    # -----------------ISSUES--------------------
    issueData = [
        (
            projects[0],
            users[1],
            users[1],
            {
                "title": "MobileLogin",
                "key": "1",
                "description": "Login doesn’t work on mobile",
            },
        ),
        (
            projects[0],
            users[2],
            users[3],
            {
                "title": "FilterBug",
                "key": "2",
                "description": "Search results not updating after filter applied",
            },
        ),
        (
            projects[0],
            users[2],
            users[4],
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
            users[2],
            users[4],
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
            users[2],
            users[5],
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
            users[2],
            users[3],
            {
                "title": "DarkToggle",
                "key": "3",
                "description": "Dark mode toggle doesn’t save preference",
            },
        ),
        (
            projects[2],
            users[2],
            users[2],
            {
                "title": "TabletCheckout",
                "key": "1",
                "description": "Checkout button unresponsive on tablet",
            },
        ),
        (
            projects[2],
            users[3],
            users[4],
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
            users[3],
            users[6],
            {
                "title": "InvalidEmail",
                "key": "3",
                "description": "Form validation allows invalid email",
            },
        ),
        (
            projects[3],
            users[2],
            users[6],
            {
                "title": "MenuOverlap",
                "key": "1",
                "description": "Dropdown menu overlaps footer",
            },
        ),
        (
            projects[3],
            users[3],
            users[5],
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
            users[3],
            users[5],
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
            users[3],
            users[4],
            {
                "title": "TextCutoff",
                "key": "4",
                "description": "Text input cuts off characters in landscape mode",
            },
        ),
        (
            projects[3],
            users[4],
            users[4],
            {
                "title": "CartCurrency",
                "key": "5",
                "description": "Wrong currency displayed in cart",
            },
        ),
        (
            projects[4],
            users[4],
            users[3],
            {
                "title": "KeybindFail",
                "key": "1",
                "description": "Keyboard shortcuts not working in Firefox",
            },
        ),
        (
            projects[4],
            users[4],
            users[2],
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
            users[4],
            users[3],
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
            users[4],
            users[6],
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
            users[4],
            users[5],
            {
                "title": "DateBlock",
                "key": "5",
                "description": "Date picker doesn’t allow selecting today",
                "status": IssueStatus.CLOSED,
                "priority": IssuePriority.HIGH,
            },
        ),
        (
            projects[0],
            users[5],
            users[2],
            {
                "title": "SessionDrop",
                "key": "4",
                "description": "Session expires too early on mobile",
            },
        ),
        (
            projects[0],
            users[6],
            users[3],
            {
                "title": "LangSwitch",
                "key": "5",
                "description": "Language switch resets filters",
            },
        ),
        (
            projects[0],
            users[7],
            users[4],
            {
                "title": "AvatarCrop",
                "key": "6",
                "description": "Avatar cropper cuts edges",
            },
        ),
        (
            projects[0],
            users[8],
            users[1],
            {
                "title": "TimezoneShift",
                "key": "7",
                "description": "Event times off by one hour",
            },
        ),
        # Project 1 (existing keys 1..3) → add 4..7
        (
            projects[1],
            users[9],
            users[5],
            {
                "title": "BadgeCount",
                "key": "4",
                "description": "Unread badge count inconsistent",
            },
        ),
        (
            projects[1],
            users[10],
            users[3],
            {
                "title": "WebSocketDrop",
                "key": "5",
                "description": "WebSocket disconnects under load",
            },
        ),
        (
            projects[1],
            users[11],
            users[4],
            {
                "title": "CSVExport",
                "key": "6",
                "description": "CSV export escapes quotes incorrectly",
            },
        ),
        (
            projects[1],
            users[12],
            users[2],
            {
                "title": "RTLLayout",
                "key": "7",
                "description": "RTL layout breaks sidebar order",
            },
        ),
        # Project 2 (existing keys 1..3) → add 4..7
        (
            projects[2],
            users[13],
            users[6],
            {
                "title": "MapPinDrift",
                "key": "4",
                "description": "Map pins drift at high zoom",
            },
        ),
        (
            projects[2],
            users[14],
            users[2],
            {
                "title": "PdfPreview",
                "key": "5",
                "description": "PDF preview shows blank on Safari",
            },
        ),
        (
            projects[2],
            users[15],
            users[3],
            {
                "title": "OAuthScope",
                "key": "6",
                "description": "Missing scope blocks calendar sync",
            },
        ),
        (
            projects[2],
            users[16],
            users[4],
            {
                "title": "SlowQuery",
                "key": "7",
                "description": "Dashboard query exceeds 2s",
            },
        ),
        # Project 3 (existing keys 1..5) → add 6..9
        (
            projects[3],
            users[17],
            users[5],
            {
                "title": "PushDup",
                "key": "6",
                "description": "Duplicate push notifications",
            },
        ),
        (
            projects[3],
            users[18],
            users[6],
            {
                "title": "VideoStutter",
                "key": "7",
                "description": "Video player stutters at 1.5x",
            },
        ),
        (
            projects[3],
            users[19],
            users[3],
            {
                "title": "TooltipDelay",
                "key": "8",
                "description": "Tooltip delay feels too long",
            },
        ),
        (
            projects[3],
            users[20],
            users[4],
            {
                "title": "ThemeContrast",
                "key": "9",
                "description": "Low contrast in dark theme",
            },
        ),
        # Project 4 (existing keys 1..5) → add 6..9
        (
            projects[4],
            users[21],
            users[2],
            {
                "title": "SSEMemory",
                "key": "6",
                "description": "Event stream increases memory usage",
            },
        ),
        (
            projects[4],
            users[22],
            users[3],
            {
                "title": "AuditTrail",
                "key": "7",
                "description": "Audit events missing for deletes",
            },
        ),
        (
            projects[4],
            users[23],
            users[4],
            {
                "title": "GzipAssets",
                "key": "8",
                "description": "Static assets not gzipped in prod",
            },
        ),
        (
            projects[4],
            users[24],
            users[6],
            {
                "title": "DateParsing",
                "key": "9",
                "description": "Date parser fails for dd/mm/yyyy",
            },
        ),
        # New Projects 5..14 → add keys 1..3 each (10 * 3 = 30)
        # Project 5
        (
            projects[5],
            users[4],
            users[2],
            {
                "title": "ColdStart",
                "key": "1",
                "description": "Cold starts spike p95 latency",
            },
        ),
        (
            projects[5],
            users[6],
            users[3],
            {
                "title": "HeaderCut",
                "key": "2",
                "description": "Headers clipped on iPhone SE",
            },
        ),
        (
            projects[5],
            users[8],
            users[5],
            {
                "title": "EmojiCrash",
                "key": "3",
                "description": "Emoji picker crashes keyboard",
            },
        ),
        # Project 6
        (
            projects[6],
            users[10],
            users[4],
            {
                "title": "WebhookRetry",
                "key": "1",
                "description": "Webhook retries not exponential",
            },
        ),
        (
            projects[6],
            users[12],
            users[6],
            {
                "title": "ACLDrift",
                "key": "2",
                "description": "ACL view shows stale permissions",
            },
        ),
        (
            projects[6],
            users[14],
            users[3],
            {
                "title": "SnackOverlap",
                "key": "3",
                "description": "Snackbar overlaps FAB",
            },
        ),
        # Project 7
        (
            projects[7],
            users[16],
            users[5],
            {
                "title": "Throttling",
                "key": "1",
                "description": "Rate limit kicks in too early",
            },
        ),
        (
            projects[7],
            users[18],
            users[2],
            {
                "title": "AvatarBlur",
                "key": "2",
                "description": "Avatar renders blurry on retina",
            },
        ),
        (
            projects[7],
            users[20],
            users[6],
            {
                "title": "ConfettiCPU",
                "key": "3",
                "description": "Confetti animation spikes CPU",
            },
        ),
        # Project 8
        (
            projects[8],
            users[22],
            users[4],
            {
                "title": "ImportLoop",
                "key": "1",
                "description": "Import job loops on bad rows",
            },
        ),
        (
            projects[8],
            users[24],
            users[3],
            {
                "title": "CSPBlock",
                "key": "2",
                "description": "CSP blocks inline styles",
            },
        ),
        (
            projects[8],
            users[26],
            users[5],
            {
                "title": "DragGhost",
                "key": "3",
                "description": "Drag ghost misaligned in grid",
            },
        ),
        # Project 9
        (
            projects[9],
            users[1],
            users[2],
            {
                "title": "LinkUnderline",
                "key": "1",
                "description": "Links lose underline on hover",
            },
        ),
        (
            projects[9],
            users[3],
            users[4],
            {"title": "HighCPUIdle", "key": "2", "description": "High CPU while idle"},
        ),
        (
            projects[9],
            users[5],
            users[6],
            {
                "title": "BadgeOverflow",
                "key": "3",
                "description": "Badge text overflows",
            },
        ),
        # Project 10
        (
            projects[10],
            users[7],
            users[5],
            {
                "title": "ModalTrap",
                "key": "1",
                "description": "Focus trapped after modal close",
            },
        ),
        (
            projects[10],
            users[9],
            users[3],
            {
                "title": "PrintStyles",
                "key": "2",
                "description": "Print stylesheet missing",
            },
        ),
        (
            projects[10],
            users[11],
            users[4],
            {
                "title": "PXtoREM",
                "key": "3",
                "description": "Hardcoded px break rem scaling",
            },
        ),
        # Project 11
        (
            projects[11],
            users[13],
            users[6],
            {
                "title": "UndoRedo",
                "key": "1",
                "description": "Undo redo stack corrupts",
            },
        ),
        (
            projects[11],
            users[15],
            users[2],
            {
                "title": "SharePerm",
                "key": "2",
                "description": "Share dialog doesn’t respect perms",
            },
        ),
        (
            projects[11],
            users[17],
            users[5],
            {
                "title": "StickyHeader",
                "key": "3",
                "description": "Sticky header flickers",
            },
        ),
        # Project 12
        (
            projects[12],
            users[19],
            users[3],
            {
                "title": "BulkEdit",
                "key": "1",
                "description": "Bulk edit skips first row",
            },
        ),
        (
            projects[12],
            users[21],
            users[4],
            {
                "title": "CaptchaLoop",
                "key": "2",
                "description": "Captcha loops for VPN users",
            },
        ),
        (
            projects[12],
            users[23],
            users[6],
            {
                "title": "SplitPane",
                "key": "3",
                "description": "Split pane resizer misbehaves",
            },
        ),
        # Project 13
        (
            projects[13],
            users[25],
            users[2],
            {
                "title": "ShortcutClash",
                "key": "1",
                "description": "Keyboard shortcut clashes with OS",
            },
        ),
        (
            projects[13],
            users[20],
            users[4],
            {"title": "MinZoom", "key": "2", "description": "Map minZoom ignored"},
        ),
        (
            projects[13],
            users[16],
            users[5],
            {
                "title": "OfflineQueue",
                "key": "3",
                "description": "Offline queue not persisted",
            },
        ),
        # Project 14
        (
            projects[14],
            users[12],
            users[6],
            {
                "title": "QRDecode",
                "key": "1",
                "description": "QR code decoder times out",
            },
        ),
        (
            projects[14],
            users[8],
            users[3],
            {
                "title": "RTLIcons",
                "key": "2",
                "description": "Icon alignment off in RTL",
            },
        ),
        (
            projects[14],
            users[4],
            users[2],
            {
                "title": "ScrollLock",
                "key": "3",
                "description": "Scroll lock sticks after modal",
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
        (issues[7], users[3], "Still broken"),
        (issues[3], users[6], "Works on desktop"),
        (issues[12], users[2], "Please fix soon"),
        (issues[0], users[4], "Not reproducible"),
        (issues[18], users[5], "Keeps happening"),
        (issues[6], users[1], "Confirmed bug"),
        (issues[10], users[3], "Fails again"),
        (issues[5], users[2], "Seems fine"),
        (issues[14], users[1], "Any update?"),
        (issues[2], users[6], "Problem persists"),
        (issues[9], users[5], "Affects checkout"),
        (issues[8], users[4], "Cache issue"),
        (issues[1], users[3], "Needs priority"),
        (issues[13], users[1], "Error shown"),
        (issues[11], users[6], "Quick fix?"),
        (issues[16], users[2], "Reopened bug"),
        (issues[4], users[3], "Critical issue"),
        (issues[17], users[5], "Intermittent"),
        (issues[15], users[5], "App crash"),
        (issues[7], users[1], "Still failing"),
        (issues[3], users[6], "Happens again"),
        (issues[10], users[2], "Unusable"),
        (issues[6], users[3], "Recheck logs"),
        (issues[0], users[5], "Same problem"),
        (issues[9], users[4], "Very annoying"),
        (issues[12], users[1], "Broken flow"),
        (issues[8], users[2], "Not fixed"),
        (issues[2], users[6], "Needs patch"),
        (issues[11], users[5], "Bug confirmed"),
        (issues[14], users[3], "Timeout issue"),
        (issues[18], users[1], "Works once"),
        (issues[1], users[4], "Fails often"),
        (issues[13], users[2], "Minor bug"),
        (issues[15], users[6], "Big blocker"),
        (issues[4], users[3], "Temporary fix"),
        (issues[17], users[1], "Occurs daily"),
        (issues[7], users[5], "Regression"),
        (issues[16], users[4], "Needs testing"),
        (issues[3], users[2], "Happens randomly"),
        (issues[5], users[3], "UI glitch"),
        (issues[9], users[1], "Not loading"),
        (issues[12], users[6], "Data lost"),
        (issues[8], users[5], "Hard to use"),
        (issues[10], users[4], "Restart fails"),
        (issues[6], users[2], "Error popup"),
        (issues[18], users[3], "Happens daily"),
        (issues[0], users[1], "No workaround"),
        (issues[11], users[6], "Any ETA?"),
        (issues[14], users[4], "Still waiting"),
        (issues[2], users[5], "Please resolve"),
        (issues[19], users[7], "Seeing this on staging"),
        (issues[20], users[8], "Logs attached"),
        (issues[21], users[9], "Repro steps added"),
        (issues[22], users[10], "Needs triage"),
        (issues[23], users[11], "Edge-case only"),
        (issues[24], users[12], "Affects VIP users"),
        (issues[25], users[13], "Probably caching"),
        (issues[26], users[14], "Suspect race condition"),
        (issues[27], users[15], "Please prioritize"),
        (issues[28], users[16], "Regression from 1.2"),
        (issues[29], users[17], "Customer reported"),
        (issues[30], users[18], "Happens after deploy"),
        (issues[31], users[19], "Can’t reproduce locally"),
        (issues[32], users[20], "Occurs under load"),
        (issues[33], users[21], "Workaround exists"),
        (issues[34], users[22], "UI only"),
        (issues[35], users[23], "Backend related"),
        (issues[36], users[24], "Possible duplicate"),
        (issues[37], users[25], "Linked to outage"),
        (issues[38], users[26], "Might be data issue"),
        (issues[39], users[27], "Feature flag off fixes it"),
        (issues[40], users[7], "Adding to sprint"),
        (issues[41], users[8], "Not happening on Android"),
        (issues[42], users[9], "QA confirmed"),
        (issues[43], users[10], "Need design input"),
        (issues[44], users[11], "Worse on slow network"),
        (issues[45], users[12], "Null check missing"),
        (issues[46], users[13], "Narrow scope fix"),
        (issues[47], users[14], "Will hotfix"),
        (issues[48], users[15], "Tentative root cause"),
        (issues[49], users[16], "Pending canary"),
        (issues[50], users[17], "Metrics attached"),
        (issues[51], users[18], "Dashboards updated"),
        (issues[52], users[19], "Alert triggered"),
        (issues[53], users[20], "Needs SRE review"),
        (issues[54], users[21], "Rollout blocked"),
        (issues[55], users[22], "Config drift?"),
        (issues[56], users[23], "Retry helped once"),
        (issues[57], users[24], "Timeout threshold low"),
        (issues[58], users[25], "Connection pool saturated"),
        (issues[59], users[26], "Queue length rising"),
        (issues[60], users[27], "Memory spike observed"),
        (issues[61], users[7], "CPU pinned to 90%"),
        (issues[62], users[8], "DB lock suspected"),
        (issues[63], users[9], "Added tracing"),
        (issues[64], users[10], "Can replicate with 3 steps"),
        (issues[65], users[11], "A/B variant only"),
        (issues[66], users[12], "Schema mismatch"),
        (issues[67], users[13], "Bad migration earlier"),
        (issues[68], users[14], "Fix verified in canary"),
        # Second pass over a variety of issues for volume (repeatable pattern, different comments)
        (issues[5], users[15], "Labeling as P2"),
        (issues[8], users[16], "Reopening"),
        (issues[12], users[17], "Downgrading severity"),
        (issues[1], users[18], "UX concern here"),
        (issues[3], users[19], "Needs product signoff"),
        (issues[4], users[20], "Blocked by dependency"),
        (issues[6], users[21], "Root cause unclear"),
        (issues[7], users[22], "Added test case"),
        (issues[9], users[23], "Verified in Firefox"),
        (issues[10], users[24], "Network flakiness suspected"),
        (issues[11], users[25], "Intermittent still"),
        (issues[13], users[26], "User impact limited"),
        (issues[14], users[27], "Docs need update"),
        (issues[15], users[7], "Can’t reproduce after cache clear"),
        (issues[16], users[8], "Pinned to team"),
        (issues[17], users[9], "Good first issue?"),
        (issues[18], users[10], "Needs more logs"),
        (issues[0], users[11], "Happens in incognito"),
        (issues[2], users[12], "Adding to epic"),
        (issues[4], users[13], "Estimate: 2 points"),
        (issues[5], users[14], "Edge device specific"),
        (issues[6], users[15], "Cannot reproduce in staging"),
        (issues[7], users[16], "Present since v1.1.0"),
        (issues[8], users[17], "Seems related to CSP"),
        (issues[9], users[18], "Rolling back helped"),
        (issues[10], users[19], "Retry loop fails"),
        (issues[11], users[20], "Added Sentry breadcrumb"),
        (issues[12], users[21], "Perf budget exceeded"),
        (issues[13], users[22], "Feature request overlap"),
        (issues[14], users[23], "Won’t fix?"),
        (issues[15], users[24], "Triaged to team A"),
        (issues[16], users[25], "Paging on-call"),
        (issues[17], users[26], "Added Grafana panel"),
        (issues[18], users[27], "Linked to outage #42"),
        # Third pass with different phrasing
        (issues[19], users[7], "Consider circuit breaker"),
        (issues[20], users[8], "Noise in logs reduced"),
        (issues[21], users[9], "Flaked once in CI"),
        (issues[22], users[10], "Re-running with trace"),
        (issues[23], users[11], "Pinned version fixes"),
        (issues[24], users[12], "Rollback planned"),
        (issues[25], users[13], "Added unit test"),
        (issues[26], users[14], "E2E added"),
        (issues[27], users[15], "Needs canary for 24h"),
        (issues[28], users[16], "Rate limit adjusted"),
        (issues[29], users[17], "Backoff increased"),
        (issues[30], users[18], "Added jitter"),
        (issues[31], users[19], "Sharding considered"),
        (issues[32], users[20], "Shard imbalance noted"),
        (issues[33], users[21], "Index missing"),
        (issues[34], users[22], "Added partial index"),
        (issues[35], users[23], "Query plan attached"),
        (issues[36], users[24], "Analyze shows seq scan"),
        (issues[37], users[25], "Added covering index"),
        (issues[38], users[26], "Vacuum scheduled"),
        (issues[39], users[27], "Autovacuum tuned"),
        (issues[40], users[7], "Timeout bumped"),
        (issues[41], users[8], "Pool size reduced"),
        (issues[42], users[9], "GC pressure suspected"),
        (issues[43], users[10], "Heap growth leveled"),
        (issues[44], users[11], "Lock contention confirmed"),
        (issues[45], users[12], "Deadlock avoided"),
        (issues[46], users[13], "Retry policy updated"),
        (issues[47], users[14], "Circuit closed"),
        (issues[48], users[15], "Queue depth OK now"),
        (issues[49], users[16], "Throughput improved"),
        (issues[50], users[17], "p95 down 30%"),
        (issues[51], users[18], "p99 acceptable"),
        (issues[52], users[19], "SLO met"),
        (issues[53], users[20], "On-call acked"),
        (issues[54], users[21], "Runbook updated"),
        (issues[55], users[22], "Ownership changed"),
        (issues[56], users[23], "Feature flagged"),
        (issues[57], users[24], "Flag off fixes it"),
        (issues[58], users[25], "Experiment rolled back"),
        (issues[59], users[26], "Canary green"),
        (issues[60], users[27], "Ready to close"),
        # Final pass to reach 200 new comments
        (issues[61], users[10], "Docs added"),
        (issues[62], users[11], "Test matrix expanded"),
        (issues[63], users[12], "Device lab test OK"),
        (issues[64], users[13], "Locale-specific bug"),
        (issues[65], users[14], "DST edge case"),
        (issues[66], users[15], "Unicode normalization"),
        (issues[67], users[16], "Timezone aligned"),
        (issues[68], users[17], "Final verification"),
        (issues[0], users[18], "Closing soon if no repro"),
        (issues[1], users[19], "Reassigning owner"),
        (issues[2], users[20], "Marking as duplicate"),
        (issues[3], users[21], "Pending design review"),
        (issues[4], users[22], "Escalated"),
        (issues[5], users[23], "De-escalated"),
        (issues[6], users[24], "Added acceptance criteria"),
        (issues[7], users[25], "QA signoff pending"),
        (issues[8], users[26], "QA signoff complete"),
        (issues[9], users[27], "Release train 34"),
        (issues[10], users[7], "Postmortem scheduled"),
        (issues[11], users[8], "Follow-up task filed"),
        (issues[12], users[9], "Customer notified"),
        (issues[13], users[10], "Legal approved"),
        (issues[14], users[11], "Security reviewed"),
        (issues[15], users[12], "Observability improved"),
        (issues[16], users[13], "Chaos test passed"),
        (issues[17], users[14], "Load test stable"),
        (issues[18], users[15], "Merging PR"),
        (issues[19], users[16], "Deployed to prod"),
        (issues[20], users[17], "No incidents reported"),
        (issues[21], users[18], "Rolling forward"),
        (issues[22], users[19], "All good now"),
        (issues[23], users[20], "Thanks everyone"),
        (issues[24], users[21], "Closing as resolved"),
        (issues[25], users[22], "Reopen if needed"),
        (issues[26], users[23], "Audit complete"),
        (issues[27], users[24], "Telemetry clean"),
        (issues[28], users[25], "Cleanup tasks filed"),
        (issues[29], users[26], "Final QA pass"),
        (issues[30], users[27], "Ready for release"),
        (issues[31], users[7], "Ship it"),
        (issues[32], users[8], "Done"),
        (issues[33], users[9], "Done and dusted"),
        (issues[34], users[10], "Verified in prod"),
        (issues[35], users[11], "Happy path green"),
        (issues[36], users[12], "Edge cases good"),
        (issues[37], users[13], "No further action"),
        (issues[38], users[14], "Note: monitor next week"),
        (issues[39], users[15], "Archived"),
        (issues[40], users[16], "SLA met"),
        (issues[41], users[17], "Thanks for the fix"),
        (issues[42], users[18], "Appreciated"),
        (issues[43], users[19], "👏"),
        (issues[44], users[20], "LGTM"),
        (issues[45], users[21], "✅"),
        (issues[46], users[22], "🎉"),
        (issues[47], users[23], "🙏"),
        (issues[48], users[24], "🏁"),
        (issues[49], users[25], "📈"),
        (issues[50], users[26], "📉"),
        (issues[51], users[27], "🧰"),
        (issues[52], users[7], "🧪"),
        (issues[53], users[8], "🧹"),
        (issues[54], users[9], "🛡️"),
        (issues[55], users[10], "🔧"),
        (issues[56], users[11], "🔎"),
        (issues[57], users[12], "🧭"),
        (issues[58], users[13], "🧱"),
        (issues[59], users[14], "🗂️"),
        (issues[60], users[15], "🛰️"),
        (issues[61], users[16], "🧩"),
        (issues[62], users[17], "🧯"),
        (issues[63], users[18], "🚑"),
        (issues[64], users[19], "🚀"),
        (issues[65], users[20], "🌟"),
        (issues[66], users[21], "🌈"),
        (issues[67], users[22], "🌊"),
        (issues[68], users[23], "🌱"),
    ]
    comments = [
        create_comment(issue, author, body=body) for issue, author, body in commentData
    ]
    for comment in comments:
        demoSession.add(comment)

    # -----------------REPORT JOBS--------------------
    reportData = [
        (users[0], "generate-report"),
        (users[1], "generate-report"),
        (users[2], "generate-report"),
        (users[3], "generate-report"),
        (users[5], "generate-report"),
        (users[8], "generate-report"),
        (users[10], "generate-report"),
        (users[12], "generate-report"),
        (users[6], "generate-report"),
        (users[4], "generate-report"),
        (users[9], "generate-report"),
        (users[13], "generate-report"),
    ]
    reportJobs = [create_job(user, job_type=job_type) for user, job_type in reportData]
    for job in reportJobs:
        demoSession.add(job)

    # Commiting database before running async tasks
    demoSession.commit()
    for job in reportJobs:
        generate_report.apply_async(
            args=[job.public_id, job.user.public_id], queue="pdfs"
        )

    failedJobs = []
    timeoutJobs = []
    generatedPdfs = []
    for job in reportJobs:
        maxAttempts = 5
        attempts = 0
        checkAfterSeconds = 3
        while True:
            demoSession.refresh(job)
            match job.state:
                case JobState.FAILED:
                    failedJobs.append(job)
                    break
                case JobState.QUEUED | JobState.RUNNING:
                    if attempts > maxAttempts:
                        timeoutJobs.append(job)
                        break
                    attempts += 1
                    time.sleep(checkAfterSeconds)
                    continue
                case JobState.SUCCEEDED:
                    generatedPdfs.append(
                        (check_pdf_exists(job.artifact.url), job.artifact.url)
                    )
                    break

    # -----------------RESULT--------------------
    demoSession.commit()

    result = (
        f"Successfully created in {settings.database.build_url()}:\n"
        f"{len(users)} users\n"
        f"{len(projects)} projects\n"
        f"{len(issues)} issues\n"
        f"{len(comments)} comments\n"
        f"{len(reportJobs)} pdf report jobs\n"
        f"\tfailed: {len(failedJobs)}\n"
        f"\tTimeout: {len(timeoutJobs)}\n"
        f"\tgenerated PDFs: {len(generatedPdfs)}\n"
    )

    result_file = "demo_results.txt"

    print(result)

    with open(result_file, "w") as results_file:
        results_file.write(result)
        for pdf in generatedPdfs:
            pdfReachable = "✅" if pdf[0] else "❌"
            results_file.write(f"\t{pdfReachable}{pdf[1]}\n")

    print(f"detailed results written to {result_file}")

    if failedJobs or timeoutJobs:
        print("ERROR: Executed with failed or timed out jobs")
        sys.exit(1)


if __name__ == "__main__":
    seed_db()
