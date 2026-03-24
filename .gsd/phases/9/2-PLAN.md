---
phase: 9
plan: 2
wave: 2
depends_on: ["1"]
---

# Plan 9.2: Frontend Dashboard UI

## Objective
Build the `Dashboard.jsx` page rendering a clean, premium analytical layout. It will fetch data from the new backend endpoint based on the selected ticker, plot historical prices with `recharts`, and cleanly list fundamental ratios alongside programmatic Pros and Cons.

## Context
- .gsd/ROADMAP.md
- frontend/package.json
- frontend/src/App.jsx

## Tasks

<task type="auto">
  <name>Install Recharts</name>
  <files>frontend/package.json</files>
  <action>
    Run `npm install recharts` in the frontend directory to acquire the charting dependencies.
  </action>
  <verify>cat frontend/package.json | findstr recharts</verify>
  <done>Recharts exists in the package dependencies.</done>
</task>

<task type="auto">
  <name>Build Dashboard Component Layout</name>
  <files>frontend/src/pages/Dashboard.jsx, frontend/src/App.jsx</files>
  <action>
    Implement `Dashboard.jsx`. Use React Router's `useSearchParams` to extract `?ticker=XYZ`.
    Display a loading spinner while fetching from `/api/stocks/dashboard?ticker=XYZ`.
    Design a Tailwind CSS grid layout meeting the prompt constraint "DONT MAKE IT CLADED":
    - Top title bar with Ticker Name and Last Price.
    - 4x Grid displaying Market Cap, 52W High/Low, P/E, P/B.
    - Main split-view: A `Recharts` `LineChart` spanning the left column, and the Pros/Cons bulleted list on the right column.
    Integrate existing `/predict` Neuro-Symbolic AI call if possible, or leave a stub for the final Phase 10 integration. For now, fetch only the dashboard stats.
  </action>
  <verify>cat frontend/src/App.jsx | findstr Dashboard</verify>
  <done>The Dashboard page is seamlessly integrated into the Protected Routes and fetches layout data successfully.</done>
</task>

## Success Criteria
- [ ] Recharts line chart accurately portrays historical prices.
- [ ] Fundamentals and Pros/Cons render cleanly.
- [ ] UI maintains the premium, uncluttered, professional aesthetic standard requested by the user.
