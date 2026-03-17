---
phase: 7
plan: 2
wave: 2
---

# Plan 7.2: Frontend React Setup & Protected Routes

## Objective
Initialize the React frontend application using Vite and set up the foundation for authentication (React Router, Login page, Protected Routes context).

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- .gsd/phases/7/RESEARCH.md
- src/routes/auth_routes.py (from Plan 7.1)

## Tasks

<task type="auto">
  <name>Initialize React Vite Project</name>
  <files>frontend/package.json</files>
  <action>
    Run `npm create vite@latest frontend -- --template react`.
    Navigate into `frontend/` and install standard dependencies: `react-router-dom`, `axios`, `lucide-react`, and Tailwind CSS (per its Vite guide).
  </action>
  <verify>cd frontend && npm run build</verify>
  <done>Vite builds the empty project successfully with dependencies installed.</done>
</task>

<task type="auto">
  <name>Setup Tailwind CSS & Basic Theme</name>
  <files>frontend/tailwind.config.js, frontend/src/index.css</files>
  <action>
    Configure `tailwind.config.js` and `postcss.config.js`.
    Create a clean, minimalist typography and color theme in `index.css` (primary brand color, neutral grays for text/borders) suitable for a financial dashboard.
  </action>
  <verify>cat frontend/tailwind.config.js</verify>
  <done>Tailwind utility classes are available in React components.</done>
</task>

<task type="auto">
  <name>Implement AuthContext and Protected Routes</name>
  <files>frontend/src/context/AuthContext.jsx, frontend/src/App.jsx</files>
  <action>
    Create an `AuthContext` to store the JWT token and user info, checking `localStorage` on load.
    Create a abstract `ProtectedRoute` component that redirects to `/login` if no user state exists.
    Wrap the main App routing using `react-router-dom`.
  </action>
  <verify>cat frontend/src/App.jsx | findstr ProtectedRoute</verify>
  <done>The application correctly guards routes when an unauthenticated user attempts access.</done>
</task>

## Success Criteria
- [ ] React project is successfully initialized and builds via Vite.
- [ ] Tailwind CSS is correctly configured.
- [ ] Routing logic prevents access to the dashboard without a valid session.
