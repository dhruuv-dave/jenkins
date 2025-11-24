# Jenkins Docker Build Setup - Reusable Guide

This guide explains how to use the Jenkins setup files in other projects.

## Files Overview

### 1. `Dockerfile.jenkins` - Jenkins Container Setup
**Purpose**: Custom Jenkins Docker image with Docker CLI pre-installed  
**Reusability**: ✅ **YES - Use this ONCE for your entire Jenkins setup**  
**Location**: Can be in any repository or a separate infrastructure repo

This file is **NOT project-specific**. Build it once and use the same Jenkins container for all your projects.

### 2. `Jenkinsfile` - Project Pipeline Configuration
**Purpose**: Defines the CI/CD pipeline for building Docker images  
**Reusability**: ✅ **YES - Copy to any project, works automatically**  
**Location**: Must be in the root of each project repository

## Quick Start - Using in Other Projects

### Step 1: Copy Jenkinsfile to Your Project

```bash
# In your new project directory
cp /path/to/Jenkinsfile .
```

The Jenkinsfile will automatically:
- ✅ Detect the project name from Jenkins job name
- ✅ Build Docker images only on `main` or `master` branch
- ✅ Save Docker images as `.tar` files
- ✅ Validate Docker is available before building

### Step 2: Ensure Your Project Has a Dockerfile

The Jenkinsfile expects a `Dockerfile` in the project root:

```
your-project/
├── Dockerfile          # Required
├── Jenkinsfile         # Copy from template
└── ... (your code)
```

### Step 3: Configure Jenkins Job

1. **Create Multibranch Pipeline** in Jenkins
2. **Point to your repository** (GitHub/GitLab/etc.)
3. **Add GitHub credentials** (if using private repos)
4. **Configure Scan Repository Triggers**:
   - Check "Periodically if not otherwise run"
   - Set interval: `* * * * *` (every minute) or `H/2 * * * *` (every 2 minutes)

### Step 4: Customize Image Name (Optional)

The image name is automatically set to your Jenkins job name. To override:

1. Go to Jenkins → Your Job → Configure
2. Under "Environment variables", add:
   - Name: `IMAGE_NAME`
   - Value: `your-custom-image-name`

## What Works Automatically

✅ **Automatic branch detection** - Only builds on `main`/`master`  
✅ **Automatic Docker image naming** - Uses job name or custom `IMAGE_NAME`  
✅ **Automatic artifact saving** - Saves `.tar` files automatically  
✅ **Error handling** - Validates Docker before building  
✅ **Timeout protection** - 30-minute timeout per build  

## Requirements

### For Each Project:
- ✅ `Dockerfile` in project root
- ✅ `Jenkinsfile` in project root (copy from template)
- ✅ Git repository (GitHub/GitLab/etc.)

### For Jenkins Setup (One-time):
- ✅ Jenkins running with Docker access
- ✅ `Dockerfile.jenkins` built into `jenkins-with-docker:lts` image
- ✅ Jenkins container with Docker socket mounted

## Example: Setting Up a New Project

```bash
# 1. Clone your new project
git clone https://github.com/your-org/new-project.git
cd new-project

# 2. Copy Jenkinsfile
cp /path/to/template/Jenkinsfile .

# 3. Ensure Dockerfile exists
ls Dockerfile  # Should exist

# 4. Commit and push
git add Jenkinsfile
git commit -m "Add Jenkins CI/CD pipeline"
git push origin main

# 5. In Jenkins: Create new Multibranch Pipeline job
#    - Point to: https://github.com/your-org/new-project
#    - Jenkinsfile path: Jenkinsfile (default)
#    - Configure scan triggers
#    - Save and scan repository
```

## Docker Image Naming

Images are automatically named as:
- `{IMAGE_NAME}:main-{commit-hash}` - Specific commit
- `{IMAGE_NAME}:main-latest` - Latest main branch build

Where `IMAGE_NAME` is:
1. Custom value from Jenkins job environment variables (if set)
2. Jenkins job name (auto-detected)

## Troubleshooting

### "Docker permission denied"
- Ensure Jenkins container has Docker socket mounted
- Check `Dockerfile.jenkins` was used to build Jenkins image

### "No changes detected"
- Click "Scan Repository Now" in Jenkins
- Check scan log for errors
- Verify GitHub credentials are configured

### "Dockerfile not found"
- Ensure `Dockerfile` exists in project root
- Check Jenkinsfile is also in project root

## Summary

- **Dockerfile.jenkins**: Build once, use for all projects ✅
- **Jenkinsfile**: Copy to each project, works automatically ✅
- **Requirements**: Just need a `Dockerfile` in each project ✅

The setup is **production-ready** and **fully reusable**! 🚀

