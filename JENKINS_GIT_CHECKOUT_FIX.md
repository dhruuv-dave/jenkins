# Fixing Git Checkout Issues in Jenkins

## Problem
Jenkins pipeline fails with error:
```
ERROR: Error fetching remote repo 'origin'
fatal: not in a git directory
```

This happens when the Jenkins workspace directory is corrupted or not properly initialized as a git repository.

## Quick Fixes

### Solution 1: Clean Workspace (Recommended)

**In Jenkins UI:**
1. Go to your Jenkins job
2. Click on the failed build
3. Click **"Wipe Out Current Workspace"** (if available)
4. Or go to: **Job → Workspace → "Wipe Out Current Workspace"**
5. Run the build again

**Via Docker/Command Line:**
```bash
# Find your workspace path (usually: /var/jenkins_home/workspace/{job-name}_{branch-name})
docker exec jenkins rm -rf /var/jenkins_home/workspace/my-sample-app_main

# Or if you know the exact path:
docker exec jenkins ls -la /var/jenkins_home/workspace/
# Then remove the specific workspace directory
```

### Solution 2: Verify Jenkins Job Configuration

1. **Go to Jenkins → Your Job → Configure**
2. **Check "Source Code Management" section:**
   - Repository URL should be: `https://github.com/dhruuv-dave/jenkins.git` (or your actual repo)
   - Branch should be: `*/main` or `*/master` (or your branch pattern)
   - Credentials should be set correctly (git-token2 in your case)

3. **Verify Credentials:**
   - Go to: **Jenkins → Manage Jenkins → Credentials**
   - Find your credential (git-token2)
   - Verify it has the correct GitHub token with proper permissions

### Solution 3: Fix GitHub Token Permissions

The error also shows:
```
Could not update commit status. Message: {"message":"Resource not accessible by personal access token","status":"403"}
```

This means your GitHub token doesn't have the right permissions.

**Fix:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Edit your token (or create a new one)
3. Ensure these scopes are checked:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `admin:repo_hook` (if using webhooks)
   - ✅ `workflow` (if using GitHub Actions)
4. Update the credential in Jenkins with the new token

### Solution 4: Manual Git Checkout (Temporary)

If the automatic checkout keeps failing, you can manually fix it:

```bash
# Enter Jenkins container
docker exec -u root -it jenkins bash

# Navigate to workspace
cd /var/jenkins_home/workspace/my-sample-app_main

# Remove corrupted workspace
rm -rf .git .gitignore * .*

# Initialize fresh git repo
git init
git remote add origin https://github.com/dhruuv-dave/jenkins.git
git fetch origin
git checkout -b main origin/main

# Exit container
exit
```

**Note:** This is temporary - the next build will recreate the workspace. Use this only to verify the fix works.

## Updated Jenkinsfile

The Jenkinsfile has been updated to:
- ✅ Automatically detect corrupted workspace
- ✅ Clean workspace before checkout
- ✅ Retry checkout up to 3 times
- ✅ Provide detailed error messages with troubleshooting steps

## Prevention

To prevent this issue in the future:

1. **Use Multibranch Pipeline** instead of regular Pipeline:
   - Multibranch pipelines handle workspace management better
   - Each branch gets its own workspace

2. **Enable Workspace Cleanup Plugin:**
   - Go to: **Jenkins → Manage Jenkins → Plugins**
   - Install "Workspace Cleanup Plugin"
   - Configure it to clean workspace before build

3. **Use Pipeline Cleanup:**
   Add to your Jenkinsfile `post` section:
   ```groovy
   post {
     always {
       cleanWs()  // Requires Workspace Cleanup Plugin
     }
   }
   ```

## Verification

After applying fixes, verify:

1. **Check workspace is clean:**
   ```bash
   docker exec jenkins ls -la /var/jenkins_home/workspace/my-sample-app_main
   ```

2. **Run pipeline again** - it should checkout successfully

3. **Check git status:**
   ```bash
   docker exec jenkins bash -c "cd /var/jenkins_home/workspace/my-sample-app_main && git status"
   ```

## Common Causes

1. **Interrupted build** - Build was stopped mid-checkout
2. **Disk space issues** - Workspace couldn't be fully created
3. **Permission issues** - Jenkins user couldn't write to workspace
4. **Corrupted filesystem** - Docker volume issues
5. **Network issues** - Git fetch was interrupted

## Additional Troubleshooting

### Check Jenkins Logs
```bash
docker logs jenkins | tail -100
```

### Check Disk Space
```bash
docker exec jenkins df -h
```

### Check Permissions
```bash
docker exec jenkins ls -la /var/jenkins_home/workspace/
```

### Verify Git is Available
```bash
docker exec jenkins git --version
```

### Test Repository Access
```bash
docker exec jenkins git ls-remote https://github.com/dhruuv-dave/jenkins.git
```

If this fails, check your network/firewall settings.

## Still Having Issues?

If none of the above solutions work:

1. **Check Jenkins job type:**
   - Are you using a Multibranch Pipeline or regular Pipeline?
   - Multibranch is recommended for better workspace management

2. **Check Jenkins configuration:**
   - Go to: **Jenkins → Manage Jenkins → System Configuration**
   - Verify Git plugin is installed and configured

3. **Restart Jenkins:**
   ```bash
   docker-compose restart jenkins
   ```

4. **Check for plugin conflicts:**
   - Update all plugins to latest versions
   - Check for known issues with Git plugin

