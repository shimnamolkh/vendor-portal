# Copilot / AI Agent Instructions for Vendor Portal

This file gives focused, actionable guidance for AI coding agents working on this repository so they can be productive immediately.

## Big Picture
- **Frontend-only React app** built with Vite (`package.json` scripts: `dev`, `build`, `preview`). Start with `npm run dev` (Vite opens at port `3000`).
- **Single-page app** with two primary workflows: `SupplierInwardEntry` (mandatory docs) and `DirectPurchaseEntry` (optional docs). The main app wiring is in `src/App.jsx` and `src/components/VendorDashboard.jsx`.
- **Local mock persistence**: `src/services/entryService.js` uses `localStorage` under key `vendor_portal_entries` and supplies `initialize`, `getEntries`, `addEntry`, `generateId` — replace or adapt these when adding a real backend.

## Useful Developer Workflows
- Run local dev server: `npm install` then `npm run dev` (Vite, port 3000). See `vite.config.js`.
- Build for production: `npm run build`; preview build: `npm run preview`.
- No tests present in repo — treat changes as exploratory and verify in browser.

## Project-specific Patterns & Conventions
- Component naming: PascalCase, one component per file in `src/components/`, CSS colocated with same basename (`LoginPage.jsx` + `LoginPage.css`).
- Styling: vanilla CSS + CSS variables. Expect global styles in `src/index.css` and per-component CSS files.
- Default exports: components are exported as default; imports are relative and extensionless in Vite (`import LoginPage from './components/LoginPage'`).
- Mock auth: `src/components/LoginPage.jsx` performs a simulated login and calls `entryService.initialize()` on mount. When replacing with real auth, update this file and remove mocks.

## Integration Points / Where To Hook Real Backends
- Authentication: mock logic in `src/components/LoginPage.jsx`. Target API endpoints (as documented in `README.md`) like `POST /api/v1/auth/login`.
- Submissions: `entryService` abstracts storage. To integrate a backend, replace `addEntry`, `getEntries`, and `initialize` to call the real APIs and preserve the same return shapes (see `MOCK_INITIAL_DATA` structure for the expected entry shape).

## Concrete Examples To Reference
- Vendor session: `vendorData.legalName` is passed from `App.jsx` into `VendorDashboard` and shown as the “Vendor Session Entity” (see `src/components/VendorDashboard.jsx`).
- ID generation: `entryService.generateId(type)` produces IDs like `INW-2024-001` or `DIR-2024-015` — keep this format if migrating server-side.
- LocalStorage key: `vendor_portal_entries` in `src/services/entryService.js`.

## How To Make Safe, Small Changes
- Preserve component export shapes (default exports) and props (`vendorData`, `onLogin`, `onLogout`).
- When changing persistence, keep `getEntries()` returning an array of objects like the `MOCK_INITIAL_DATA` so UIs continue to function during migration.

## What Not To Assume
- There are no tests or CI here; run the app manually in the browser after changes.
- The README lists API endpoints but they are only placeholders — do not remove mock initialization without providing a migration path.

## Where To Look First For New Work
- `src/components/` for UI changes and UX flows.
- `src/services/entryService.js` for any data/persistence changes.
- `src/App.jsx` and `src/components/VendorDashboard.jsx` for session and routing/tab state.

If anything here is unclear or you'd like the instructions expanded (for example, adding a checklist for migrating to a real backend or adding a recommended commit message format), tell me which part to expand and I will iterate.
