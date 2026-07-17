from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def init_db():
    """Creates the projects table if it doesn't exist yet. Safe to call on
    every cold start — CREATE TABLE IF NOT EXISTS is a no-op once it exists."""
    conn = get_conn()
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
    conn.commit()
    cur.close()
    conn.close()


def require_admin(x_admin_secret: str | None = Header(default=None, alias="X-Admin-Secret")):
    """Dependency guarding every /admin/* route. Same shared-secret pattern
    as the MyShop backend — appropriate for a single-owner site."""
    expected = os.getenv("ADMIN_SECRET")
    if not expected:
        raise HTTPException(status_code=500, detail="Server misconfigured: ADMIN_SECRET not set")
    if not x_admin_secret or x_admin_secret != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


class ProjectCreate(BaseModel):
    title: str
    description: str
    icon: str = "🔧"
    badge: str = "Live"
    tech_stack: list[str] = []
    live_url: str | None = None
    github_url: str | None = None
    sort_order: int = 0


class ProjectUpdate(ProjectCreate):
    pass


class ReorderItem(BaseModel):
    id: int
    sort_order: int


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def read_root():
    return {"status": "running"}


@app.get("/projects")
def get_projects():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, title, description, icon, badge, tech_stack, live_url, github_url, sort_order
        FROM projects
        ORDER BY sort_order ASC, created_at DESC;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "icon": r[3],
            "badge": r[4],
            "tech_stack": r[5],
            "live_url": r[6],
            "github_url": r[7],
            "sort_order": r[8],
        }
        for r in rows
    ]


@app.post("/admin/projects", dependencies=[Depends(require_admin)])
def create_project(project: ProjectCreate):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO projects (title, description, icon, badge, tech_stack, live_url, github_url, sort_order)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (
            project.title,
            project.description,
            project.icon,
            project.badge,
            project.tech_stack,
            project.live_url,
            project.github_url,
            project.sort_order,
        ),
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": new_id, "message": "Project created"}


@app.put("/admin/projects/{project_id}", dependencies=[Depends(require_admin)])
def update_project(project_id: int, project: ProjectUpdate):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM projects WHERE id = %s;", (project_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")

    cur.execute(
        """
        UPDATE projects
        SET title = %s, description = %s, icon = %s, badge = %s,
            tech_stack = %s, live_url = %s, github_url = %s, sort_order = %s
        WHERE id = %s;
        """,
        (
            project.title,
            project.description,
            project.icon,
            project.badge,
            project.tech_stack,
            project.live_url,
            project.github_url,
            project.sort_order,
            project_id,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Project updated"}


@app.delete("/admin/projects/{project_id}", dependencies=[Depends(require_admin)])
def delete_project(project_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id = %s RETURNING id;", (project_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}


@app.put("/admin/projects/reorder", dependencies=[Depends(require_admin)])
def reorder_projects(items: list[ReorderItem]):
    conn = get_conn()
    cur = conn.cursor()
    for item in items:
        cur.execute("UPDATE projects SET sort_order = %s WHERE id = %s;", (item.sort_order, item.id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Order updated"}
