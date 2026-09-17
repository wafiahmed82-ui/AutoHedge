# AutoHedge Development Environment Plan

## Purpose

Create a reproducible Windows + GitHub + Codex development workflow for AutoHedge so local development, testing, branches, commits, and pull requests do not depend on ad-hoc setup.

## Current repository observations

- Core project is a Python package managed with Poetry.
- `pyproject.toml` currently targets Python `^3.10`.
- Runtime dependencies include `swarms`, `pydantic`, `loguru`, `httpx`, `solders`, `yfinance`, and `python-dotenv`.
- Ruff and Black are already configured.
- The repository contains tests and GitHub configuration.
- The README describes a multi-agent trading pipeline: Director -> Quant -> Risk Manager -> Execution.
- The README documents sensitive environment variables including API keys and a wallet private key. These must remain local/secrets and must never be committed.

## Important architecture decision

Panda CSS is not part of the Python core. Panda should only be introduced if/when AutoHedge has a JavaScript/TypeScript web UI. The web UI should be a separate frontend layer communicating with the Python core through a deliberate API boundary.

## Target development workflow

Windows PC -> Git repository -> GitHub -> feature branch -> tests/lint -> Pull Request -> review -> merge -> local update.

GitHub Codespaces/dev containers may be used as a reproducible secondary environment. A custom dev container should include the exact Python/runtime and tooling requirements once the final stack is audited.

## Required setup to audit/standardize

1. Python 3.10 compatibility and exact package-manager workflow.
2. Poetry installation and lockfile strategy.
3. `.env.example` versus actual secret storage.
4. Ruff and Black commands and configuration consistency.
5. Test command and minimum CI checks.
6. GitHub Actions workflow configuration.
7. Pre-commit hooks if useful after verifying they do not duplicate CI unnecessarily.
8. GitHub CLI availability for local PR workflows.
9. Node.js/npm only if a frontend is confirmed or added.
10. Optional `.devcontainer/devcontainer.json` for reproducible Codespaces/local-container development.

## Safety rules

- Never commit `.env`, API keys, wallet private keys, seed phrases, credentials, or production secrets.
- Never run autonomous trading against live funds as part of setup validation.
- Use mock/testnet/simulation paths for development and CI.
- Do not modify `main` directly for setup work; use feature branches and PRs.

## Proposed implementation sequence

### Phase 1 - Audit

Inspect repository structure, tests, workflows, dependencies, runtime assumptions, and existing development instructions.

### Phase 2 - Reproducible tooling

Add only the configuration that is actually required: development instructions, CI checks, and optionally a dev container. Keep the Python core unchanged unless a defect is discovered.

### Phase 3 - PR workflow

Validate branch creation, local checks, push, PR creation, CI, review, and merge/update workflow.

### Phase 4 - Frontend decision

If a web dashboard is required, define a separate frontend architecture first. Only then evaluate React/Vite/Next.js plus Panda CSS. Panda generates atomic CSS at build time and is intended for JavaScript/TypeScript applications, not the Python trading core.

## Status

Initial plan saved on branch `chore/dev-environment-audit`. This document is a planning artifact; it does not claim that the setup has been fully implemented or tested yet.
