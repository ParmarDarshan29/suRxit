# <p align="center">
	<img src="surxit.png" alt="suRxit logo" width="160" />
</p>

# suRxit

suRxit is an AI-driven healthcare risk intelligence platform that processes unstructured medical documents and produces explainable risk signals for clinicians and payers. The project is split into modular services (backend, frontend, model assets, and microservices).

This README focuses on: 1) how to run the project locally, and 2) how to prepare the repository to be made public safely (important: do not commit API keys or other secrets).

## Table of contents
- Overview
- Quick start (local)
- Environment variables (where to set API keys)
- Making the repo public safely (checklist + remediation)
- Removing secrets from git history (commands)
- Security checklist before publishing
- Contributing

## Quick start (local)

Prerequisites
- Git
- Python 3.10+ (for backend services)
- Node.js 18+ and npm/yarn/pnpm (for frontend)
- Docker (optional, some services may have containers)

Typical local steps (high level)

1. Clone the repository:

	 git clone <your-repo-url>
	 cd suRxit

2. Backend (Python)

- Create a virtual environment and install requirements:

	python -m venv .venv
	source .venv/bin/activate
	pip install -r backend/requirements.txt

- Copy `backend/.env.example` -> `backend/.env` and fill values (see Environment variables below).

- Run the backend service (example):

	cd backend
	# small helper exists: start.sh or simple_main.py; check backend/README.md for exact command

3. Frontend (Vite + React)

- Install and run the frontend:

	cd frontend
	npm install
	# create .env from .env.example
	cp .env.example .env
	# set VITE_GEMINI_API_KEY and other values in .env
	npm run dev

Notes
- The repo contains demo credentials and example env files. DO NOT commit real API keys. See the Security section below before publishing.

## Environment variables (high level)

Backend (`backend/.env.example` contains the expected keys):
- JWT_SECRET_KEY - secret for signing JWT tokens (rotate in production)
- OPENAI_API_KEY - OpenAI API key (do not commit)
- ANTHROPIC_API_KEY - Anthropic key placeholder (do not commit)
- DATABASE_URL - optional DB connection string

Frontend (`frontend/.env.example`):
- VITE_API_BASE_URL - backend URL
- VITE_JWT_SECRET - used for demo/local only
- VITE_GEMINI_API_KEY - the Gemini / Google Generative API key (must be set in `.env` locally)

Always store real secrets in environment variables or CI/CD secrets (GitHub Actions secrets, etc.). Add local `.env` to `.gitignore` (this repo already ignores `*.env`).

## Making the repository public — safety checklist and recommended steps

Before flipping a repo to public, follow this checklist:

1. Search the repository for secrets and credentials. Examples to search for: `API_KEY`, `api_key`, `SECRET`, `password`, `-----BEGIN PRIVATE KEY-----`, `AIza` (Google API key patterns), `AKIA` (AWS), and `OPENAI_API_KEY`.

2. Remove or replace any hard-coded secrets in source files. Replace them with environment variable access and update `.env.example`.

3. If you find secrets that were committed in the past, treat the key as compromised: rotate the key (revoke and re-create) and remove it from the git history (instructions below).

4. Ensure `.gitignore` includes local env files and other sensitive artifacts (this repo already contains `*.env` in `.gitignore`).

5. Use GitHub repository settings or the `gh` CLI to change visibility to public only after completing the steps above.

6. Add a `SECURITY.md` (this repo already has `SECURITY.md`) and clear instructions for reporting issues and handling data.

### Quick commands to change repo visibility (one-line)

Use the GitHub web UI (Settings → Danger Zone → Change repository visibility) or the `gh` CLI:

	gh repo edit <owner/repo> --visibility public

Run that only after you've completed the security checklist and removed any sensitive data.

## Removing sensitive data from git history

If secrets were committed, removing them from the working tree is not enough — they live in git history. Two common tools to purge history:

1) BFG Repo-Cleaner (simpler to use)

	# Download BFG jar and run (example)
	bfg --delete-files YOUR_FILE_WITH_SECRET
	git reflog expire --expire=now --all && git gc --prune=now --aggressive

2) git filter-repo (recommended for complex rewrites)

	# Example: remove all occurrences of a string
	git filter-repo --replace-text replacements.txt

Where `replacements.txt` contains lines like:

	literal-string-to-remove==>REDACTED

After rewriting history, force-push to the remote (note: this is destructive and will rewrite commit SHAs):

	git push --force --all
	git push --force --tags

Important: coordinate with collaborators before forcing history changes. If you prefer not to rewrite history, rotate the leaked keys immediately and keep note of what was exposed.

## Rotating compromised keys

If any API key was accidentally committed:

1. Revoke the exposed key in the provider's console (Google Cloud, OpenAI, AWS, etc.).
2. Create a new key and update your environment variables / CI secrets.
3. Remove the old key from code and history (see previous section) or at minimum mark it rotated and not usable.

## Security checklist before publishing (quick)
- [ ] No hard-coded secrets in source files
- [ ] `.env` or other secret files are in `.gitignore`
- [ ] Any leaked keys rotated and revoked
- [ ] Sensitive files removed from git history or keys revoked
- [ ] CI/CD secrets configured in GitHub (Settings → Secrets) for required API keys
- [ ] Minimal disclosure: .env.example present with placeholders, not real values

## Contributing

Please read `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`. If you add features that require new environment variables, add them to the appropriate `.env.example` file and document them in this README.

## License
See the `LICENSE` file at the repository root.

---

If you'd like, I can:
- 1) Remove or replace the hard-coded Gemini API key found in `frontend/src/components/ChatbotPopup.jsx` (I will not add any real key to the repo). — I already changed the file to use an env var.
- 2) Add or extend `.env.example` files and expand this README further with step-by-step run commands for each microservice.
- 3) Provide exact commands to purge the git history and a suggested rotation plan for any leaked key (I'll show both `git filter-repo` and `bfg` examples).

Tell me which of the above you'd like me to do next (I can proceed to purge history or prepare a pull request with the README and env changes). 