# 📚 Branch and Commit Standards – Hoplias

## 🧩 Acronyms & Conventions

- **FHP-XXX** → Feature code in the `Features Hoplias` pattern (e.g., `FHP-001`)
- **v1.0.x.x** → Target release version (major.minor.patch.build)

---

## 🌿 Branch Creation

> Branches must follow the pattern:  
> `feature/<FHP-ID>-<name-slug>`  
> `fix/<FHP-ID>-<name-slug>`  
> `docs/<FHP-ID>-<name-slug>`

### ✅ Example

```bash
git checkout -b feature/FHP-001-sync-modules
```

---

## 📝 Commits

> The standard follows the [Conventional Commits](https://www.conventionalcommits.org/) model, including the FHP ID.

```bash
<type>(scope)?: FHP-XXX short description
```

### ✅ Examples

```bash
git commit -m "feat(sync): FHP-001 add real-time data sync between modules"
git commit -m "fix(api): FHP-002 fix null check in sync handler"
git commit -m "refactor(core): FHP-003 improve state management logic"
git commit -m "docs(readme): FHP-004 add usage documentation for API"
git commit -m "fix(auth): FHP-007 fix password token validation"
```

---

## 📦 Commit Types (Conventional Commits)

| Type      | Description                                               |
|-----------|-----------------------------------------------------------|
| `feat`    | New feature                                               |
| `fix`     | Bug fix                                                   |
| `docs`    | Documentation changes                                     |
| `style`   | Formatting, indentation, etc. (no logic change)           |
| `refactor`| Code refactoring (no new feature or fix)                  |
| `perf`    | Performance improvements                                  |
| `test`    | Adding or adjusting tests                                 |
| `chore`   | Build tasks, CI/CD, dependencies, configs, etc.           |

---

## 🔗 Relationship between FHP and Version

Each `FHP-XXX` represents a feature or improvement planned for a specific version `v1.0.x.x`.

> **Example:**  
> `FHP-001` will be delivered in version `v1.0.1.0`.

---

## ✅ Pull Request Checklist

- [ ] Branch name follows the pattern `feature/FHP-XXX-description`
- [ ] Commits follow the Conventional Commits format
- [ ] The PR references the corresponding FHP in the body or title
- [ ] CI/CD is passing
- [ ] Documentation has been updated (if necessary)

---

**Template v1.0.0 – Hoplias**  
*Last update: DD/MM/YYYY*
