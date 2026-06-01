"""
FREEWAY M365 + CONSTRUCTION ENTERPRISE SIMULATOR
================================================
- Normalized (3NF) bronze layer (CSV)
- Silver layer (cleaned Parquet, still normalized)
- Gold star schema (denormalized dims & aggregated facts)
- Full M365 admin audit (every operation you listed)
- Nationality‑aware names for construction workforce
"""

import pandas as pd
import numpy as np
import uuid
import random
from faker import Faker
from datetime import datetime, timedelta
from pathlib import Path

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
class Config:
    OUTPUT_DIR = "freeway_m365_dataset"
    START_DATE = datetime(2025, 1, 1)
    END_DATE = datetime(2025, 12, 31)

    # Dimension sizes
    USERS = 10000
    PROJECTS = 50
    SITES = 75
    DEVICES = 12000
    VEHICLES = 200
    EQUIPMENT_TYPES = 50
    MATERIALS = 100
    CAMPS = 20

    # Event row counts
    SIGNINS = 500_000
    MFA_EVENTS = 150_000
    EMAILS = 400_000
    TEAMS_MEETINGS = 150_000
    TEAMS_CHATS = 150_000
    SHAREPOINT_EVENTS = 300_000
    ONEDRIVE_EVENTS = 250_000
    DEFENDER_ALERTS = 50_000
    DLP_INCIDENTS = 30_000
    ADMIN_AUDIT = 200_000
    ATTENDANCE = 300_000
    PAYROLL = 100_000
    IQAMA_TRACKING = 80_000
    GATE_ACCESS = 200_000
    SAFETY_INCIDENTS = 5_000
    TOOLBOX_TALKS = 10_000
    GPS_TRACKS = 500_000
    EQUIPMENT_USAGE = 150_000
    MATERIAL_CONSUMPTION = 200_000
    PURCHASE_ORDERS = 50_000

    @classmethod
    def rdate(cls):
        delta = int((cls.END_DATE - cls.START_DATE).total_seconds())
        return cls.START_DATE + timedelta(seconds=random.randint(0, delta))

# Initialize Faker instance for fallback
fake = Faker()

# ------------------------------------------------------------
# Nationality‑aware name generation (fixed locale mapping)
# ------------------------------------------------------------
class NationalityNameGenerator:
    # Fixed locale mapping - using only supported locales
    _locale_map = {
        "Pakistan": "en_PK",      # Supported
        "Bangladesh": "bn_BD",    # Supported
        "India": "hi_IN",         # Supported
        "Nepal": "en_NP",         # Fallback to English Nepal
        "Sri Lanka": "en_LK",     # Fallback to English Sri Lanka
        "Egypt": "ar_EG",         # Supported
        "Saudi Arabia": "ar_SA"   # Supported
    }
    _fakers = {}

    @classmethod
    def get_name(cls, nationality):
        if nationality not in cls._fakers:
            locale = cls._locale_map.get(nationality, "en_US")
            try:
                cls._fakers[nationality] = Faker(locale)
            except AttributeError:
                # If locale fails, use English with nationality-specific name patterns
                cls._fakers[nationality] = Faker('en_US')
        fake_instance = cls._fakers[nationality]
        
        # Generate culturally appropriate names based on nationality
        first_name = fake_instance.first_name()
        last_name = fake_instance.last_name()
        
        # Override with culturally specific names for better realism
        cultural_names = {
            "Pakistan": (["Ali", "Ahmed", "Muhammad", "Fatima", "Ayesha"], ["Khan", "Malik", "Bhatti", "Chaudhry"]),
            "Bangladesh": (["Mohammad", "Rahman", "Karim", "Nadia", "Shamim"], ["Hossain", "Islam", "Rahman", "Ahmed"]),
            "India": (["Raj", "Priya", "Amit", "Sunita", "Vikram"], ["Sharma", "Patel", "Kumar", "Singh"]),
            "Nepal": (["Bikram", "Sita", "Rajesh", "Gita", "Hari"], ["Shrestha", "Gurung", "Thapa", "Adhikari"]),
            "Sri Lanka": (["Dilshan", "Kumari", "Nimal", "Chamari", "Saman"], ["Perera", "Silva", "Jayawardene", "Bandara"]),
            "Egypt": (["Mohamed", "Ahmed", "Fatma", "Omar", "Nour"], ["Ali", "Hassan", "Mahmoud", "Ibrahim"]),
            "Saudi Arabia": (["Abdullah", "Fatima", "Mohammed", "Aisha", "Khalid"], ["Al-Otaibi", "Al-Ghamdi", "Al-Dosari", "Al-Qahtani"])
        }
        
        if nationality in cultural_names:
            first_names, last_names = cultural_names[nationality]
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
        return first_name, last_name

# ------------------------------------------------------------
# Step 1: Generate normalized base tables (CSV - Bronze)
# ------------------------------------------------------------
def generate_normalized_users():
    rows = []
    nationalities = [
        ("Pakistan", 35), ("Bangladesh", 20), ("India", 15),
        ("Nepal", 10), ("Sri Lanka", 5), ("Egypt", 10), ("Saudi Arabia", 5)
    ]
    roles = ["Labor", "Foreman", "Supervisor", "Engineer", "Project Manager",
             "HR", "Procurement", "Finance", "Executive"]
    projects = list(range(1, Config.PROJECTS + 1))
    camps = list(range(1, Config.CAMPS + 1))
    cities = ["Riyadh", "Jeddah", "Dammam", "NEOM"]

    for uid in range(1, Config.USERS + 1):
        nat = random.choices([x[0] for x in nationalities],
                             weights=[x[1] for x in nationalities])[0]
        first, last = NationalityNameGenerator.get_name(nat)
        role = random.choice(roles)
        upn = f"{first.lower()}.{last.lower()}{uid}@freeway.local"

        rows.append({
            "user_id": uid,
            "first_name": first,
            "last_name": last,
            "nationality": nat,
            "role": role,
            "upn": upn,
            "project_id": random.choice(projects),
            "site_city": random.choice(cities),
            "camp_id": random.choice(camps),
            "iqama_number": f"IQ{uid:08d}" if random.random() > 0.1 else None,
            "visa_expiry_date": Config.rdate().date() if random.random() > 0.3 else None,
            "hire_date": Config.rdate().date()
        })
    df = pd.DataFrame(rows)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/users.csv", index=False)
    return df

def generate_normalized_projects():
    df = pd.DataFrame({
        "project_id": range(1, Config.PROJECTS + 1),
        "project_name": [f"Project_{i}" for i in range(1, Config.PROJECTS + 1)],
        "budget_usd": np.random.randint(500_000, 50_000_000, Config.PROJECTS)
    })
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/projects.csv", index=False)
    return df

def generate_normalized_sites():
    df = pd.DataFrame({
        "site_id": range(1, Config.SITES + 1),
        "site_name": [f"Site_{i}" for i in range(1, Config.SITES + 1)],
        "latitude": np.random.uniform(21.0, 32.0, Config.SITES),
        "longitude": np.random.uniform(35.0, 55.0, Config.SITES)
    })
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/sites.csv", index=False)
    return df

def generate_normalized_devices():
    df = pd.DataFrame({
        "device_id": range(1, Config.DEVICES + 1),
        "device_name": [f"DEV-{i:06d}" for i in range(1, Config.DEVICES + 1)],
        "os": np.random.choice(["Windows 11", "Windows 10", "Android", "iOS", "macOS"], Config.DEVICES)
    })
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/devices.csv", index=False)
    return df

def generate_normalized_vehicles():
    df = pd.DataFrame({
        "vehicle_id": range(1, Config.VEHICLES + 1),
        "plate_number": [f"ABC{1234+i}" for i in range(Config.VEHICLES)],
        "type": np.random.choice(["Truck", "Bus", "Pickup", "Crane", "Excavator"], Config.VEHICLES)
    })
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/vehicles.csv", index=False)
    return df

def generate_normalized_equipment():
    df = pd.DataFrame({
        "equipment_id": range(1, Config.EQUIPMENT_TYPES + 1),
        "equipment_name": [f"Eq_{i}" for i in range(1, Config.EQUIPMENT_TYPES + 1)],
        "category": np.random.choice(["Heavy", "Light", "Safety", "Electrical"], Config.EQUIPMENT_TYPES)
    })
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/equipment.csv", index=False)
    return df

def generate_normalized_materials():
    df = pd.DataFrame({
        "material_id": range(1, Config.MATERIALS + 1),
        "material_name": [f"Material_{i}" for i in range(1, Config.MATERIALS + 1)],
        "unit": np.random.choice(["kg", "ton", "m3", "piece", "liter"], Config.MATERIALS)
    })
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/materials.csv", index=False)
    return df

def generate_normalized_camps():
    df = pd.DataFrame({
        "camp_id": range(1, Config.CAMPS + 1),
        "camp_name": [f"Camp_{i}" for i in range(1, Config.CAMPS + 1)],
        "capacity": np.random.randint(50, 500, Config.CAMPS)
    })
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/camps.csv", index=False)
    return df

# ------------------------------------------------------------
# Step 2: Generate normalized event tables (CSV - Bronze)
# ------------------------------------------------------------
def generate_normalized_signins(users_df, devices_df):
    print("  Generating signins...")
    data = []
    for _ in range(Config.SIGNINS):
        user = users_df.sample(1).iloc[0]
        device = devices_df.sample(1).iloc[0]
        data.append({
            "signin_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "device_id": device.device_id,
            "timestamp": Config.rdate(),
            "status": random.choice(["Success", "Success", "Success", "Failure"]),
            "ip_address": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
            "risk_level": random.choice(["Low", "Medium", "High", "Critical"]),
            "application": random.choice(["Teams", "SharePoint", "Exchange", "Power BI", "Azure Portal", "OneDrive"])
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/signins.csv", index=False)
    return df

def generate_normalized_mfa(users_df):
    print("  Generating MFA events...")
    data = []
    for _ in range(Config.MFA_EVENTS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "mfa_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "event_type": random.choice(["MFARegistered", "MFAChallengePassed", "MFAChallengeFailed"]),
            "method": random.choice(["SMS", "Phone call", "Authenticator app", "FIDO2"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/mfa_events.csv", index=False)
    return df

def generate_normalized_emails(users_df):
    print("  Generating emails...")
    data = []
    for _ in range(Config.EMAILS):
        sender = users_df.sample(1).iloc[0]
        receiver = users_df.sample(1).iloc[0]
        data.append({
            "email_id": str(uuid.uuid4()),
            "sender_user_id": sender.user_id,
            "receiver_user_id": receiver.user_id,
            "attachments_count": random.randint(0, 10),
            "size_kb": random.randint(1, 5000),
            "sensitivity_label": random.choice(["Normal", "Confidential", "High"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/emails.csv", index=False)
    return df

def generate_normalized_teams_meetings(users_df):
    print("  Generating Teams meetings...")
    data = []
    for _ in range(Config.TEAMS_MEETINGS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "meeting_id": str(uuid.uuid4()),
            "organizer_user_id": user.user_id,
            "duration_minutes": random.randint(5, 120),
            "participants_count": random.randint(2, 50),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/teams_meetings.csv", index=False)
    return df

def generate_normalized_teams_chats(users_df):
    print("  Generating Teams chats...")
    data = []
    for _ in range(Config.TEAMS_CHATS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "chat_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "message_type": random.choice(["ChatMessageSent", "CallStarted"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/teams_chats.csv", index=False)
    return df

def generate_normalized_sharepoint_events(users_df):
    print("  Generating SharePoint events...")
    data = []
    for _ in range(Config.SHAREPOINT_EVENTS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "event_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "activity_type": random.choice(["FileUploaded", "FileDownloaded", "FileModified", "FileShared"]),
            "file_name": f"Doc_{random.randint(1,50000)}.pdf",
            "site_url": f"https://freeway.sharepoint.com/sites/project_{random.randint(1,Config.PROJECTS)}",
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/sharepoint_events.csv", index=False)
    return df

def generate_normalized_onedrive_events(users_df):
    print("  Generating OneDrive events...")
    data = []
    for _ in range(Config.ONEDRIVE_EVENTS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "event_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "activity_type": random.choice(["Upload", "Download", "Delete"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/onedrive_events.csv", index=False)
    return df

def generate_normalized_defender_alerts(users_df):
    print("  Generating Defender alerts...")
    data = []
    for _ in range(Config.DEFENDER_ALERTS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "alert_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "alert_type": random.choice(["ImpossibleTravel", "MalwareDetected", "BruteForce", "MassDownload"]),
            "severity": random.choice(["Medium", "High", "Critical"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/defender_alerts.csv", index=False)
    return df

def generate_normalized_dlp_incidents(users_df):
    print("  Generating DLP incidents...")
    data = []
    for _ in range(Config.DLP_INCIDENTS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "incident_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "policy_name": random.choice(["HIPAA", "PCI", "GDPR", "Internal Only"]),
            "action_taken": random.choice(["Blocked", "AlertOnly", "AllowOverride"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/dlp_incidents.csv", index=False)
    return df

# ========== EXTENDED ADMIN AUDIT (all operations from your list) ==========
ADMIN_OPERATIONS_FULL = [
    # Admin centers & PowerShell
    "Accessing the admin centers", "Setting up PowerShell", "Viewing Microsoft 365 roadmap",
    "Discovering changes via Message center", "Opening a service request", "Monitoring service request status",
    # Domain & user management
    "Adding a domain", "Changing the domain for users", "Assigning a license to a user",
    "Assigning a license to a group", "Customizing navigation of the admin center",
    "Getting a list of all available commands", "Creating a user", "Disabling a user",
    "Changing user settings or profile information", "Getting a list of all users with user properties",
    "Changing a user password",
    # SharePoint & OneDrive admin
    "Connecting via PowerShell to SharePoint Online", "Creating a SharePoint Online site",
    "Adding a new site admin to all SharePoint Online sites", "Restoring a deleted OneDrive site",
    "Hiding Microsoft 365 groups from the Global Address List",
    "Preventing external senders from emailing internal Microsoft 365 groups",
    "Personalizing your admin center home page", "Creating a new user with a mailbox",
    # Exchange admin
    "Creating a mail-enabled security group", "Creating an Exchange Online shared mailbox",
    "Creating a distribution list", "Creating a dynamic distribution list",
    "Creating an Exchange-specific retention policy", "Creating a mail flow rule",
    "Configuring spam filter policies", "Creating room and equipment resources",
    "Enabling Advanced Threat Protection (ATP) features",
    # Microsoft Search
    "Creating an acronym", "Creating a bookmark", "Importing bookmarks in bulk from CSV",
    "Adding a location", "Adding a Q&A result", "Setting up usage of Microsoft Search in Bing",
    "Assigning Search Administrator and Search Editor roles", "Using Search Insights dashboard reports",
    # External sharing & sync
    "Enabling external sharing", "Configuring external sharing permission levels",
    "Restricting sharing to specific domains", "Enabling local sync of files",
    "Restricting local syncing to PCs on specific domains", "Setting up compliance safeguards",
    "Providing individuals access to another user's OneDrive content",
    # Power Platform & Power BI
    "Creating a new Power Platform environment", "Creating a Dataverse database",
    "Restricting certain connectors in Power Apps and Power Automate from accessing business data",
    "Using Analytics to explore usage, failures, and performance in Microsoft Power Platform",
    "Installing an on-premises data gateway", "Restricting users from installing on-premises data gateways",
    "Restricting Power BI's Publish to web (anonymous share) ability to specific security group members",
    "Auditing Power BI embed codes created by your organization",
    "Configuring a default logo, cover image, and theme for Power BI",
    # SharePoint site admin (extended)
    "Creating a new site", "Deleting a site", "Limiting external sharing abilities",
    "Setting stricter external sharing settings for a specific site", "Setting the default share link type",
    "Configuring site collection storage", "Importing data from network locations using Migration Manager or SPMT",
    "Hiding the subsite creation button", "Designating a site as a hub site and associating other sites with it",
    "Restricting access by IP address",
    # Teams admin
    "Creating a team", "Creating a Team policy", "Configuring meeting settings",
    "Creating a Meeting policy", "Creating an Events policy", "Creating a Messaging policy",
    "Applying a policy (Team/Meeting/Messaging) to specific users", "Configuring Teams setup policies",
    "Configuring external access", "Configuring guest access", "Reviewing all teams and their owners",
    # Viva Engage
    "Understanding admin roles for Viva Engage", "Pinning Viva Engage in Teams",
    "Assigning the Corporate Communicator role to a user", "Customizing the look of your Viva Engage network",
    "Creating a Viva Engage community", "Creating a dynamic Viva Engage community",
    "Restricting posts in the All Company community",
    # Entra ID (Azure AD)
    "Creating and populating Microsoft Entra ID", "Adding branding to the Entra ID sign-in page",
    "Adding a privacy statement to the Entra ID sign-in page", "Adding SSO for an application",
    "Getting direct sign-on links for organizational apps", "Installing and connecting to the Microsoft Graph SDK via PowerShell",
    "Adding/removing users via PowerShell in Microsoft Graph", "Creating an Access review report in Entra ID",
    "Reviewing and completing an Access review report in Entra ID",
    # Security & Compliance (Defender, Purview)
    "Creating a threat protection policy", "Setting up a Safe Links policy",
    "Setting up a Safe Attachments policy", "Accessing and reviewing an organization's Secure Score",
    "Complying with Secure Score security configuration recommendations",
    "Assigning permissions for non-IT users to Microsoft Defender", "Monitoring Microsoft Defender reports",
    "Utilizing threat investigation and response capabilities",
    "Utilizing automated investigation and response capabilities", "Enabling self-service password reset",
    "Viewing a report on all users who have accessed a specific SharePoint file",
    "Accessing Microsoft's HIPAA business associate agreement",
    "Creating a DLP policy to protect content with HIPAA-protected data detected",
    "Using DLP to automatically report HIPAA incident reports",
    "Creating a custom sensitive information type based on keywords",
    "Creating a DLP policy for content with custom keywords in the name or subject",
    "Tuning a DLP policy's sensitivity", "Creating a retention policy to retain content for seven years",
    "Creating and using an eDiscovery case", "Assigning permissions for non-IT users to Microsoft Purview",
    "Using Communication Compliance to identify potential policy violations in messages",
    "Finding at-risk users", "Creating alerts for specific activities performed by users in OneDrive",
    "Reviewing mail handling to see spam and malware history", "Identifying your least active SharePoint sites",
    "Analyzing search activity throughout Microsoft 365", "Checking service health status and known issues",
    "Checking general usage data for Microsoft 365 apps and services", "Checking Teams usage and user activity",
    "Monitoring Power Apps and Power Automate usage and activity"
]

def generate_normalized_admin_audit(users_df):
    print("  Generating admin audit logs...")
    data = []
    for _ in range(Config.ADMIN_AUDIT):
        admin = users_df.sample(1).iloc[0]
        data.append({
            "audit_id": str(uuid.uuid4()),
            "user_id": admin.user_id,
            "operation": random.choice(ADMIN_OPERATIONS_FULL),
            "result": random.choice(["Success", "Failure"]),
            "target_resource": random.choice([None, "SharePoint site", "Exchange mailbox", "Teams policy", "User license"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/admin_audit.csv", index=False)
    return df

# Construction events (normalized)
def generate_normalized_attendance(users_df):
    print("  Generating attendance records...")
    data = []
    for _ in range(Config.ATTENDANCE):
        user = users_df.sample(1).iloc[0]
        data.append({
            "attendance_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "date": Config.rdate().date(),
            "check_in_time": Config.rdate().time(),
            "check_out_time": Config.rdate().time(),
            "status": random.choice(["Present", "Absent", "Late", "Overtime"])
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/attendance.csv", index=False)
    return df

def generate_normalized_payroll(users_df):
    print("  Generating payroll records...")
    data = []
    for _ in range(Config.PAYROLL):
        user = users_df.sample(1).iloc[0]
        data.append({
            "payroll_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "month_start": Config.rdate().replace(day=1),
            "base_salary": random.randint(1500, 15000),
            "overtime_hours": random.randint(0, 50),
            "bonus": random.randint(0, 2000),
            "deductions": random.randint(0, 500)
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/payroll.csv", index=False)
    return df

def generate_normalized_iqama_tracking(users_df):
    print("  Generating iqama tracking records...")
    data = []
    for _ in range(Config.IQAMA_TRACKING):
        user = users_df.sample(1).iloc[0]
        data.append({
            "tracking_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "iqama_number": user.iqama_number,
            "expiry_date": Config.rdate().date(),
            "renewal_status": random.choice(["Renewed", "Pending", "Expired"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/iqama_tracking.csv", index=False)
    return df

def generate_normalized_gate_access(users_df):
    print("  Generating gate access logs...")
    data = []
    for _ in range(Config.GATE_ACCESS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "access_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "gate_name": random.choice(["Main Gate", "North Gate", "East Gate"]),
            "direction": random.choice(["IN", "OUT"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/gate_access.csv", index=False)
    return df

def generate_normalized_safety_incidents(users_df):
    print("  Generating safety incidents...")
    data = []
    for _ in range(Config.SAFETY_INCIDENTS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "incident_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "incident_type": random.choice(["Fall", "Equipment malfunction", "Electrical", "Fire", "Chemical spill"]),
            "severity": random.choice(["Low", "Medium", "High", "Fatality"]),
            "description": fake.sentence(),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/safety_incidents.csv", index=False)
    return df

def generate_normalized_toolbox_talks(users_df):
    print("  Generating toolbox talks...")
    data = []
    for _ in range(Config.TOOLBOX_TALKS):
        user = users_df.sample(1).iloc[0]
        data.append({
            "talk_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "topic": random.choice(["Ladder safety", "PPE", "Excavation", "Crane operation"]),
            "attendees_count": random.randint(5, 30),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/toolbox_talks.csv", index=False)
    return df

def generate_normalized_gps_tracking(vehicles_df):
    print("  Generating GPS tracking data...")
    data = []
    for _ in range(Config.GPS_TRACKS):
        vehicle = vehicles_df.sample(1).iloc[0]
        data.append({
            "gps_id": str(uuid.uuid4()),
            "vehicle_id": vehicle.vehicle_id,
            "latitude": np.random.uniform(21.0, 32.0),
            "longitude": np.random.uniform(35.0, 55.0),
            "speed_kmh": random.randint(0, 120),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/gps_tracking.csv", index=False)
    return df

def generate_normalized_equipment_usage(equipment_df, users_df):
    print("  Generating equipment usage records...")
    data = []
    for _ in range(Config.EQUIPMENT_USAGE):
        eq = equipment_df.sample(1).iloc[0]
        user = users_df.sample(1).iloc[0]
        data.append({
            "usage_id": str(uuid.uuid4()),
            "equipment_id": eq.equipment_id,
            "user_id": user.user_id,
            "hours_used": round(random.uniform(0.5, 12), 1),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/equipment_usage.csv", index=False)
    return df

def generate_normalized_material_consumption(materials_df, users_df):
    print("  Generating material consumption records...")
    data = []
    for _ in range(Config.MATERIAL_CONSUMPTION):
        mat = materials_df.sample(1).iloc[0]
        user = users_df.sample(1).iloc[0]
        data.append({
            "consumption_id": str(uuid.uuid4()),
            "material_id": mat.material_id,
            "user_id": user.user_id,
            "quantity": round(random.uniform(10, 1000), 2),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/material_consumption.csv", index=False)
    return df

def generate_normalized_purchase_orders(materials_df, users_df):
    print("  Generating purchase orders...")
    data = []
    for _ in range(Config.PURCHASE_ORDERS):
        mat = materials_df.sample(1).iloc[0]
        user = users_df.sample(1).iloc[0]
        data.append({
            "po_id": str(uuid.uuid4()),
            "material_id": mat.material_id,
            "requested_by_user_id": user.user_id,
            "quantity": random.randint(100, 10000),
            "unit_price": round(random.uniform(10, 5000), 2),
            "status": random.choice(["Draft", "Approved", "Shipped", "Delivered"]),
            "timestamp": Config.rdate()
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{Config.OUTPUT_DIR}/bronze/purchase_orders.csv", index=False)
    return df

# ------------------------------------------------------------
# Step 3: Silver layer – convert CSV to Parquet (still normalized)
# ------------------------------------------------------------
def bronze_to_silver():
    print("\nStep 3: Converting to Silver Parquet (normalized)...")
    bronze_dir = Path(Config.OUTPUT_DIR) / "bronze"
    silver_dir = Path(Config.OUTPUT_DIR) / "silver"
    silver_dir.mkdir(exist_ok=True, parents=True)

    for csv_file in bronze_dir.glob("*.csv"):
        print(f"  Converting {csv_file.name}...")
        df = pd.read_csv(csv_file)
        parquet_file = silver_dir / (csv_file.stem + ".parquet")
        df.to_parquet(parquet_file, index=False)
    print("Silver layer created (normalized Parquet).")

# ------------------------------------------------------------
# Step 4: Gold star schema – denormalized dimensions & aggregated facts
# ------------------------------------------------------------
def build_gold_star_schema():
    print("\nStep 4: Building Gold Star Schema...")
    silver_dir = Path(Config.OUTPUT_DIR) / "silver"
    gold_dir = Path(Config.OUTPUT_DIR) / "gold"
    gold_dir.mkdir(exist_ok=True, parents=True)

    # Load normalized tables
    print("  Loading silver tables...")
    users = pd.read_parquet(silver_dir / "users.parquet")
    projects = pd.read_parquet(silver_dir / "projects.parquet")
    sites = pd.read_parquet(silver_dir / "sites.parquet")
    devices = pd.read_parquet(silver_dir / "devices.parquet")
    vehicles = pd.read_parquet(silver_dir / "vehicles.parquet")
    equipment = pd.read_parquet(silver_dir / "equipment.parquet")
    materials = pd.read_parquet(silver_dir / "materials.parquet")
    camps = pd.read_parquet(silver_dir / "camps.parquet")

    # Denormalized dimensions (star schema)
    print("  Creating dimension tables...")
    dim_user = users.merge(projects, on="project_id", how="left") \
                     .merge(camps, on="camp_id", how="left")
    dim_user.to_parquet(gold_dir / "dim_user.parquet", index=False)

    dim_project = projects.copy()
    dim_project.to_parquet(gold_dir / "dim_project.parquet", index=False)

    dim_site = sites.copy()
    dim_site.to_parquet(gold_dir / "dim_site.parquet", index=False)

    dim_device = devices.copy()
    dim_device.to_parquet(gold_dir / "dim_device.parquet", index=False)

    dim_vehicle = vehicles.copy()
    dim_vehicle.to_parquet(gold_dir / "dim_vehicle.parquet", index=False)

    dim_equipment = equipment.copy()
    dim_equipment.to_parquet(gold_dir / "dim_equipment.parquet", index=False)

    dim_material = materials.copy()
    dim_material.to_parquet(gold_dir / "dim_material.parquet", index=False)

    dim_camp = camps.copy()
    dim_camp.to_parquet(gold_dir / "dim_camp.parquet", index=False)

    # Fact tables (denormalized for reporting)
    print("  Creating fact tables...")
    signins = pd.read_parquet(silver_dir / "signins.parquet")
    fact_signin = signins.merge(users[["user_id", "upn", "nationality", "role"]], on="user_id") \
                         .merge(devices, on="device_id")
    fact_signin.to_parquet(gold_dir / "fact_signin.parquet", index=False)

    # Aggregated examples
    signins["date"] = pd.to_datetime(signins["timestamp"]).dt.date
    daily_signins = signins.groupby(["user_id", "date"]).size().reset_index(name="signin_count")
    daily_signins.to_parquet(gold_dir / "fact_daily_signins.parquet", index=False)

    print("Gold star schema created.")

# ------------------------------------------------------------
# Main execution
# ------------------------------------------------------------
def main():
    print("=" * 60)
    print("FREEWAY M365 + CONSTRUCTION ENTERPRISE SIMULATOR")
    print("=" * 60)
    
    # Create folders
    for layer in ["bronze", "silver", "gold"]:
        Path(Config.OUTPUT_DIR, layer).mkdir(parents=True, exist_ok=True)

    print("\nStep 1: Generating normalized base tables...")
    users_df = generate_normalized_users()
    generate_normalized_projects()
    generate_normalized_sites()
    devices_df = generate_normalized_devices()
    vehicles_df = generate_normalized_vehicles()
    equipment_df = generate_normalized_equipment()
    materials_df = generate_normalized_materials()
    generate_normalized_camps()

    print("\nStep 2: Generating normalized event tables (M365 + Construction)...")
    generate_normalized_signins(users_df, devices_df)
    generate_normalized_mfa(users_df)
    generate_normalized_emails(users_df)
    generate_normalized_teams_meetings(users_df)
    generate_normalized_teams_chats(users_df)
    generate_normalized_sharepoint_events(users_df)
    generate_normalized_onedrive_events(users_df)
    generate_normalized_defender_alerts(users_df)
    generate_normalized_dlp_incidents(users_df)
    generate_normalized_admin_audit(users_df)
    generate_normalized_attendance(users_df)
    generate_normalized_payroll(users_df)
    generate_normalized_iqama_tracking(users_df)
    generate_normalized_gate_access(users_df)
    generate_normalized_safety_incidents(users_df)
    generate_normalized_toolbox_talks(users_df)
    generate_normalized_gps_tracking(vehicles_df)
    generate_normalized_equipment_usage(equipment_df, users_df)
    generate_normalized_material_consumption(materials_df, users_df)
    generate_normalized_purchase_orders(materials_df, users_df)

    bronze_to_silver()
    build_gold_star_schema()

    print("\n" + "=" * 60)
    print(f"✅ Complete! Output in '{Config.OUTPUT_DIR}/'")
    print("   - bronze/  : normalized CSV (3NF)")
    print("   - silver/  : normalized Parquet")
    print("   - gold/    : star schema Parquet for Power BI")
    print(f"   Total admin operations in audit: {len(ADMIN_OPERATIONS_FULL)}")
    print("=" * 60)

if __name__ == "__main__":
    main()