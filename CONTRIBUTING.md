# 🤝 BillGuard — Team Contributing & Git Collaboration Guide

Welcome to the **BillGuard** development team! To maintain clean code and avoid merge conflicts across all 5 team members, follow these protocols.

---

## 1. Branching Strategy

- **`main`**: Production-ready code only. Direct pushes are disabled.
- **`develop`**: Integration branch for the ongoing sprint.
- **Feature Branches**: Created off `develop` using the format:
  ```bash
  feature/<member-id>-<short-description>
  ```
  *Examples*:
  - `feature/m1-scaffolding`
  - `feature/m2-dashboard-table`
  - `feature/m3-auth-api`
  - `feature/m4-gemini-ocr`
  - `feature/m5-email-alerts`

- **Bugfix Branches**:
  ```bash
  fix/<member-id>-<bug-description>
  ```

---

## 2. Daily Workflow for Each Member

### Starting a Task
1. Pull the latest code from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   ```
2. Create your feature branch:
   ```bash
   git checkout -b feature/m2-add-bill-modal
   ```

### Committing Changes
Use Conventional Commits:
- `feat: add new bill modal with validation`
- `fix: correct due date calculation`
- `style: format with prettier`
- `docs: update API documentation`

### Syncing Before Opening a PR
Always re-sync your branch with `develop` before submitting a Pull Request:
```bash
git checkout develop
git pull origin develop
git checkout feature/m2-add-bill-modal
git merge develop
```
Resolve any merge conflicts locally, test your code, and then push:
```bash
git push origin feature/m2-add-bill-modal
```

---

## 3. Pull Request (PR) Checklist

1. Target branch must always be **`develop`** (never `main`).
2. Fill out the PR template completely.
3. Verify all local tests and lint checks pass.
4. Request review from **Member 1 (Team Lead)** or the respective module owner.
5. After approval and green checks, merge via **"Squash and merge"** or standard merge.
