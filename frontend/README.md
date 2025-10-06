
# suRxit Frontend

AI-powered medication safety dashboard for doctors and patients.

## Features
- Unified prescription intake (text/file)
- Doctor & patient dashboards
- Risk gauge, DDI/ADR/DFI tables, home-remedy cards
- Evidence modal, alerts banner, chatbot widget, history timeline
- JWT auth, WebSocket/SSE alerts, i18n, PWA-ready
- Cypress E2E & integration tests

## Getting Started

1. **Install dependencies:**
	```bash
	npm install
	```
2. **Copy environment variables:**
	```bash
	cp .env.example .env
	```
3. **Run the dev server:**
	```bash
	npm run dev
	```

## Scripts
- `npm run dev` — Start Vite dev server
- `npm run build` — Build for production
- `npm run test` — Run integration tests
- `npx cypress open` — Launch Cypress E2E UI

## Environment Variables
See `.env.example` for all required variables.

## Tech Stack
- React 18, Vite, Tailwind CSS, shadcn/ui
- Axios, React Query, React Router
- JWT, WebSocket/SSE, i18n, PWA

## Accessibility & Responsiveness
- ADA-compliant, mobile-first UI

## License
MIT
