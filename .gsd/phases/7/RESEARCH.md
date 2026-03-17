# Phase 7 Research: Frontend Architecture & Auth System

## 1. Discovery Level
Level 2 — Standard Research
We are choosing a frontend technology stack to build out a professional stock screening dashboard that mimics the clean, data-dense look of screener.in. 

## 2. Requirements & Constraints
- Must look highly professional and modern. Needs to support dense data tables and interactive charts without feeling cluttered.
- Must include basic authentication (Login/Signup).
- Needs to integrate seamlessly with our existing Flask REST API.
- No constraints explicitly defined in SPEC.md for the UI layer (only Python constraints exist for the backend model).

## 3. Technology Stack Choice

### 3.1 Framework
**Decision**: React with Vite.
*Why*: Vite provides a lightning-fast development experience. React has the richest ecosystem for financial charts (e.g., Recharts, Chart.js) and data tables, which will be critical in Phase 9/10.

### 3.2 Styling
**Decision**: Tailwind CSS.
*Why*: Allows for rapid, utility-first styling to achieve the clean, "uncluttered" look requested by the user. Easier to maintain than pure Vanilla CSS when components scale up across multiple views (Dashboard, P&L, etc.).

### 3.3 State Management & Routing
**Decision**: React Router (for navigation) and Context API (for auth state).
*Why*: We just need to manage session tokens and basic user data. Redux is overkill for this currently.

### 3.4 Authentication Mechanism
**Decision**: JWT (JSON Web Tokens) with a local SQLite database (via Flask-SQLAlchemy).
*Why*: The user needs a full login system, but this is a personal/portfolio project. Setting up PostgreSQL is unnecessary overhead right now. SQLite is perfect for tracking basic users.

## 4. Phase 7 Deliverables Architecture

### Backend Updates (Flask)
- Add `Flask-SQLAlchemy` and `Flask-Bcrypt` (for password hashing).
- Add `PyJWT` for token generation.
- Create `/api/auth/register` and `/api/auth/login` endpoints.

### Frontend Architecture (React/Vite)
- Initialize standard Vite React template.
- Create `Login` and `Signup` views.
- Implement an `AuthProvider` context to manage login state.
- Create protected routes to prevent unauthenticated access to the main app layout.
