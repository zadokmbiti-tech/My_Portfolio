# Zadok Mutethia Mbiti — Personal Portfolio

A clean, responsive personal portfolio website showcasing my projects, skills, and background as a developer and cloud engineering enthusiast.

🌐 **Live:** [my-portfolio-zadok.vercel.app](https://my-portfolio-zadok.vercel.app)

---

## About

This portfolio serves as my digital presence — a single-page site that highlights who I am, what I build, and how to reach me. Built with pure HTML, CSS, and JavaScript with no frameworks or dependencies.

---

## Features

- Responsive design — works on mobile and desktop
- Projects section with live links and descriptions
- Skills and tech stack overview
- Contact section
- Fast load — no frameworks, no build step

---

## Tech Stack

| Layer | Technology |
|---|---|
| Markup | HTML5 |
| Styling | CSS3 |
| Interactivity | Vanilla JavaScript |
| Projects backend | FastAPI + PostgreSQL (`/backend`) |
| Deployment | Vercel (frontend + backend as two separate projects) |

---

## Managing Projects

The "Real Projects" section no longer has hardcoded cards — it fetches from a small backend and renders itself. To add, edit, reorder, or remove a project:

1. Open `manage.html` on the deployed site (e.g. `your-site.vercel.app/manage.html`)
2. Enter the admin password when prompted
3. Fill in the form and save — the change is live on `index.html` immediately, no redeploy needed

### Setting it up

```bash
# backend
cd backend
python -m venv venv
venv\Scripts\activate        # or `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

# copy .env.example to .env and fill in:
# DATABASE_URL — Postgres connection string (Neon, Supabase, etc.)
# ADMIN_SECRET — a password only you know

uvicorn main:app --reload     # http://localhost:8000 — creates the projects table on first run
```

Deploy `/backend` as its own Vercel project (it has its own `vercel.json`), set `DATABASE_URL` and `ADMIN_SECRET` in its Vercel environment variables, then point `config.js` at the deployed URL:

```js
const API_URL = "https://your-portfolio-backend.vercel.app";
```

`manage.html` sends the same `ADMIN_SECRET` as an `X-Admin-Secret` header on every write — there's no full login system, which is intentional for a single-owner site.

---

## Projects Featured

- **ChamaLink** — Welfare group management platform (FastAPI + PostgreSQL)
- **FreshWash** — Laundry management system with M-Pesa integration (Django)
- **Zaddy Business Directory** — Business listing platform with reviews (PHP/MySQL)

*(Managed dynamically via `manage.html` — the list above reflects what's typically featured, but the live site is the source of truth.)*

---

## Developer

**Zadok Mutethia Mbiti**
- GitHub: [@zadokmbiti-tech](https://github.com/zadokmbiti-tech)
- Final year BSc ICT Management — Maseno University
- Interests: Cloud Engineering, AWS, DevOps, Full-Stack Development
