# Jenkins Pipeline Issues - Fixed

This document summarizes the issues encountered and their fixes.

## Issue 1: Docker Command Not Found (Exit Code 127) ✅ FIXED

### Problem
Pipeline failed with:
```
ERROR: script returned exit code 127
```
Docker CLI was not available inside the Jenkins container.

### Solution Applied
- ✅ Updated `Dockerfile.jenkins` to install Docker CLI during image build
- ✅ Updated `docker-compose.yml` and `docker-compose.ubuntu.yml` to use custom Jenkins image
- ✅ Enhanced error messages in Jenkinsfile for better diagnostics

### How to Apply Fix
```bash
# Rebuild Jenkins with Docker CLI
docker-compose build jenkins
docker-compose up -d
```

**See:** `JENKINS_DOCKER_FIX.md` for detailed troubleshooting

---

## Issue 2: Git Checkout Failure ✅ FIXED

### Problem
Pipeline failed with:
```
ERROR: Error fetching remote repo 'origin'
fatal: not in a git directory
```
Workspace directory was corrupted or not properly initialized as a git repository.

### Solution Applied
- ✅ Added automatic workspace cleanup in Jenkinsfile
- ✅ Added retry logic for git checkout (up to 3 attempts)
- ✅ Enhanced error messages with troubleshooting steps
- ✅ Added workspace validation before checkout

### How to Apply Fix

**Option 1: Clean Workspace (Quick Fix)**
1. In Jenkins UI: Go to your job → Click "Wipe Out Current Workspace"
2. Or via command: `docker exec jenkins rm -rf /var/jenkins_home/workspace/my-sample-app_main`
3. Run the build again

**Option 2: Fix GitHub Token Permissions**
The error also shows:
```
Could not update commit status. Message: {"message":"Resource not accessible by personal access token","status":"403"}
```

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Edit your token and ensure these scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `admin:repo_hook` (if using webhooks)
3. Update the credential in Jenkins

**See:** `JENKINS_GIT_CHECKOUT_FIX.md` for detailed troubleshooting

---

## Files Updated

### Core Files
1. **Dockerfile.jenkins** - Installs Docker CLI
2. **docker-compose.yml** - Uses custom Jenkins image
3. **docker-compose.ubuntu.yml** - Uses custom Jenkins image
4. **Jenkinsfile** - Enhanced error handling and retry logic

### Documentation
1. **JENKINS_DOCKER_FIX.md** - Docker troubleshooting guide
2. **JENKINS_GIT_CHECKOUT_FIX.md** - Git checkout troubleshooting guide
3. **JENKINS_ISSUES_FIXED.md** - This summary document
4. **DOCKER_COMPOSE_SETUP.md** - Updated with Docker CLI installation info

---

## Next Steps

1. **Rebuild Jenkins container:**
   ```bash
   docker-compose down
   docker-compose build jenkins
   docker-compose up -d
   ```

2. **Clean workspace (if needed):**
   ```bash
   docker exec jenkins rm -rf /var/jenkins_home/workspace/my-sample-app_main
   ```

3. **Fix GitHub token permissions** (if needed):
   - Update token with `repo` scope
   - Update credential in Jenkins

4. **Run pipeline again** - Both issues should now be resolved!

---

## Verification

After applying fixes, verify:

1. **Docker works:**
   ```bash
   docker exec jenkins docker --version
   docker exec jenkins docker info
   ```

2. **Git checkout works:**
   - Run the pipeline
   - Check that "Checkout" stage passes
   - Verify files are checked out: `docker exec jenkins ls -la /var/jenkins_home/workspace/my-sample-app_main`

3. **Pipeline completes:**
   - All stages should run successfully
   - Docker image should be built (if on main branch)
   - Artifacts should be saved

---

## Prevention

To prevent these issues in the future:

1. **Use Multibranch Pipeline** - Better workspace management
2. **Install Workspace Cleanup Plugin** - Automatic cleanup
3. **Regular Jenkins maintenance** - Clean old workspaces periodically
4. **Monitor disk space** - Ensure adequate storage
5. **Keep plugins updated** - Latest versions have bug fixes

---

## Support

If issues persist after applying these fixes:

1. Check Jenkins logs: `docker logs jenkins | tail -100`
2. Check workspace: `docker exec jenkins ls -la /var/jenkins_home/workspace/`
3. Check disk space: `docker exec jenkins df -h`
4. Review detailed troubleshooting guides:
   - `JENKINS_DOCKER_FIX.md`
   - `JENKINS_GIT_CHECKOUT_FIX.md`

