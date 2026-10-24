# Repository Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Create the requested independent local Group 04 repo and prepare only the common starting point.

**Architecture:** Preserve upstream Lab 03 in `lab03/`; put the new package at repo root using a `src` layout.
Add deterministic tests of the existing script before the students implement the new service.

**Tech Stack:** Python >=3.10, Pydantic 2, python-dotenv, pytest, Ruff, Git.

**Spec:** User request and Lab 03 PDF; target interfaces in `docs/architecture.md`.

## Global Constraints

- Exact target: `D:/APCS/year 2/cs252 Computational Thinking/assistant-core-lab-group04`.
- Keep all 5 upstream Lab 03 files byte-identical at the recorded upstream commit.
- Pin pydantic==2.9.2, python-dotenv==1.0.1, pytest==8.3.3, ruff==0.6.9 as in the tutorial.
- Do not implement student modules, publish a remote, or tag the incomplete service as finished.
- Preserve the distinction between each member's full refactor and later module ownership.

## Review Focus

- Existing target directory must not be overwritten.
- Original file hashes must match upstream, including after Git import.
- Original AI failures must not make characterisation tests flaky; inject deterministic stubs.
- Ruff exclusion applies only to the teaching monolith, not the new package or tests.
- `.venv` and `.env` must remain ignored and untracked.

## Task 1: Import baseline

- [x] Create the exact new directory only if absent; initialise a separate repo on main.
- [x] Copy the 5 source files, verify their Git blob hashes, and commit the unchanged snapshot.

## Task 2: Prepare the common skeleton

- [x] Copy project config, package skeleton, data, tests, provenance and team documents.
- [x] Create `.venv` at its final path and install the pinned dependencies and editable package.

## Task 3: Verify and hand off

- [x] Run pytest, Ruff check and Ruff format --check; all must exit 0.
- [x] Import the installed package outside the repository and verify original file/data hashes.
- [x] Check ignored files, inspect staged changes, record verification and commit the bootstrap.
- [x] Verify clean Git status, two commits, main branch and no remote; report remaining work.
