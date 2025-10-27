# Git Merge Workflow - Quick Reference

## Overview

Demonstrates merging changes from an older commit into current master branch.

## Process Steps

### 1. Create Development Branch

```bash
git checkout -b development <commit-hash>
```

### 2. Make Changes

- Add new files (e.g., `purchase_entry.html`)
- Modify existing files (e.g., change "Date" to "From Date")

### 3. Commit Changes

```bash
git add .
git commit -m "Descriptive commit message"
```

### 4. Merge to Master

```bash
git checkout master
git merge development --no-ff
```

### 5. Cleanup

```bash
git branch -d development
```

## Key Points

- **New files**: Automatically added during merge
- **Modified files**: Merged if no conflicts exist
- **Conflicts**: Resolved manually if they occur
- **--no-ff flag**: Creates clear merge history

## Result

All changes from the development branch are successfully integrated into master while maintaining a clean Git history.

okay
