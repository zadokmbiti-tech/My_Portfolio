"""Run once after setting up the database to carry the three projects that
used to be hardcoded in index.html over into the projects table.

Usage:
    python seed.py
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

PROJECTS = [
    {
        "title": "Drumvale Welfare Platform",
        "description": "Full-stack chama management system — member registration, contribution tracking, M-Pesa STK Push payments, event management, attendance, and financial reporting with a five-tier RBAC system.",
        "icon": "🏦",
        "badge": "Live",
        "tech_stack": ["FastAPI", "PostgreSQL", "JavaScript", "M-Pesa", "JWT Auth", "Render"],
        "live_url": "https://drumvale-welfare.vercel.app",
        "github_url": "https://github.com/zadokmbiti-tech/drumvale-welfare",
        "sort_order": 1,
    },
    {
        "title": "FreshWash",
        "description": "Laundry management system with M-Pesa Daraja STK Push payments, Africa's Talking SMS/USSD notifications, and PWA support. Deployed on Railway with a PostgreSQL backend.",
        "icon": "🧺",
        "badge": "Deployed",
        "tech_stack": ["Django", "PostgreSQL", "M-Pesa", "Africa's Talking", "PWA", "Railway"],
        "live_url": "https://freshwashsystem.up.railway.app",
        "github_url": "https://github.com/zadokmbiti-tech/laundry-system",
        "sort_order": 2,
    },
    {
        "title": "Zaddy Business Directory",
        "description": "PHP/MySQL business directory with operation hours, open/closed status badges, star ratings, dark-themed UI, and business CRUD with category search pages.",
        "icon": "📁",
        "badge": "Hosted",
        "tech_stack": ["PHP", "MySQL", "XAMPP", "CSS", "InfinityFree"],
        "live_url": "http://zaddybusinessnetwork.kesug.com",
        "github_url": "https://github.com/zadokmbiti-tech/business-directory",
        "sort_order": 3,
    },
]


def main():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT DEFAULT '🔧',
            badge TEXT DEFAULT 'Live',
            tech_stack TEXT[] NOT NULL DEFAULT '{}',
            live_url TEXT,
            github_url TEXT,
            sort_order INT NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )

    cur.execute("SELECT COUNT(*) FROM projects;")
    if cur.fetchone()[0] > 0:
        print("projects table already has rows — skipping seed to avoid duplicates.")
        cur.close()
        conn.close()
        return

    for p in PROJECTS:
        cur.execute(
            """
            INSERT INTO projects (title, description, icon, badge, tech_stack, live_url, github_url, sort_order)
            VALUES (%(title)s, %(description)s, %(icon)s, %(badge)s, %(tech_stack)s, %(live_url)s, %(github_url)s, %(sort_order)s);
            """,
            p,
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Seeded {len(PROJECTS)} projects.")


if __name__ == "__main__":
    main()
