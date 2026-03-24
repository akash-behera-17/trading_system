---
phase: 8
plan: 2
wave: 2
depends_on: ["1"]
---

# Plan 8.2: Frontend Home & Search UI

## Objective
Build a professional, clean React homepage featuring a central search bar that auto-suggests stocks from the new backend API and routes users to the (future) dashboard upon selection.

## Context
- .gsd/ROADMAP.md
- frontend/src/App.jsx
- src/routes/stock_routes.py (from Plan 8.1)

## Tasks

<task type="auto">
  <name>Create SearchBar Component</name>
  <files>frontend/src/components/SearchBar.jsx</files>
  <action>
    Build a React component with an input field styled functionally and minimally using Tailwind CSS.
    As the user types, it should debounce (e.g., 300ms) and send Axios GET requests to `/api/stocks/search?q=value`.
    Display returned results in an absolute-positioned dropdown `<ul>` right below the input.
    When a user clicks a result, it should use React Router's `useNavigate` hook to push to `/dashboard?ticker=XXXX`.
  </action>
  <verify>cat frontend/src/components/SearchBar.jsx | findstr /api/stocks/search</verify>
  <done>The component fetches from the API and correctly updates its local auto-suggestion state.</done>
</task>

<task type="auto">
  <name>Create Home Page Layout</name>
  <files>frontend/src/pages/Home.jsx, frontend/src/App.jsx</files>
  <action>
    Create a `Home.jsx` defining a clean landing page (e.g., large center headline "Stock Screener", elegant search bar centered).
    Import and place the `SearchBar` component here.
    Update `frontend/src/App.jsx` so the base path `/` renders `<Home />` (wrap inside `<ProtectedRoute` if required, or leave Home public and let the dashboard be protected. Make Home public so users can search before logging in - though `App.jsx` currently redirects `/` to `/dashboard`. Change this so `/` is Home).
  </action>
  <verify>cat frontend/src/App.jsx | findstr Home</verify>
  <done>App.jsx correctly mounts the Home page, providing the central layout and search functionality.</done>
</task>

## Success Criteria
- [ ] Search bar component issues GET requests on typing.
- [ ] Results show gracefully in a custom styled dropdown.
- [ ] Homepage has a clean, premium visual design resembling screener.in's entry page.
