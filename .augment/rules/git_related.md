---
type: "agent_requested"
description: "Git repository corruption cleanup, specifically for desktop.ini file issues. Apply when encountering git push failures, remote repository corruption, or Windows system file contamination in git repositories."
---
# Git Desktop.ini Corruption Cleanup Rule

## **Problem Identification**
When you see this error during `git push`:
```
remote: fatal: bad object refs/desktop.ini
fatal: bad object refs/desktop.ini
! [remote rejected] master -> master (missing necessary objects)
```

## **Diagnostic Commands**

### 1. **Identify All Desktop.ini Files in Remote Repository**
```powershell
Get-ChildItem "G:\My Drive\Git\[REPO_NAME].git" -Name "*desktop.ini*" -Recurse -Force
```

### 2. **Check Local Repository for Desktop.ini**
```powershell
Get-ChildItem . -Name "*desktop.ini*" -Recurse -Force
```

### 3. **Check Git Tracked Files**
```bash
git ls-files | findstr desktop.ini
```

## **Cleanup Commands**

### 1. **Remove All Desktop.ini from Remote Repository**
```powershell
Get-ChildItem "G:\My Drive\Git\[REPO_NAME].git" -Name "*desktop.ini*" -Recurse -Force | ForEach-Object { Remove-Item "G:\My Drive\Git\[REPO_NAME].git\$_" -Force }
```

### 2. **Remove Desktop.ini from Git History (if needed)**
```bash
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch desktop.ini" --prune-empty --tag-name-filter cat -- --all
```

### 3. **Clean Local Git Repository**
```bash
git gc --prune=now
```

## **Prevention Commands**

### 1. **Add to .gitignore**
```bash
echo "desktop.ini" >> .gitignore
echo "Desktop.ini" >> .gitignore
echo "**/desktop.ini" >> .gitignore
```

### 2. **Remove from Index if Already Tracked**
```bash
git rm --cached desktop.ini
git rm --cached Desktop.ini
```

## **Recovery Workflow**
1. **Diagnose**: Run diagnostic commands to locate all desktop.ini files
2. **Clean Remote**: Remove all desktop.ini files from remote repository
3. **Clean Local**: Run git filter-branch and gc if needed
4. **Test Push**: Try pushing again
5. **Prevent**: Add desktop.ini to .gitignore

## **Common Locations for Desktop.ini in Git Repos**
- `refs/desktop.ini`
- `refs/heads/desktop.ini`
- `refs/tags/desktop.ini`
- `hooks/desktop.ini`
- `info/desktop.ini`
- `objects/desktop.ini`
- `objects/pack/desktop.ini`
- `objects/info/desktop.ini`

## **Quick Fix Command Sequence**
```powershell
# 1. Remove all desktop.ini from remote
Get-ChildItem "G:\My Drive\Git\[REPO_NAME].git" -Name "*desktop.ini*" -Recurse -Force | ForEach-Object { Remove-Item "G:\My Drive\Git\[REPO_NAME].git\$_" -Force }

# 2. Try push again
git push origin [branch-name]

# 3. If still failing, clean local history
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch desktop.ini" --prune-empty --tag-name-filter cat -- --all
git gc --prune=now

# 4. Add to gitignore
echo "desktop.ini" >> .gitignore
git add .gitignore
git commit -m "Add desktop.ini to gitignore"
```

## **Remember**
- Desktop.ini files are Windows system files that get created automatically
- They corrupt Git repositories when accidentally committed
- Always clean both local and remote repositories
- Prevention is better than cure - add to .gitignore immediately
