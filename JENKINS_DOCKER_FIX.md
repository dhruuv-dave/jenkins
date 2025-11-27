# Fixing Docker Access Issue in Jenkins

## Problem
Jenkins pipeline fails with error:
```
ERROR: script returned exit code 127
```
This happens because Docker CLI is not available inside the Jenkins container.

## Solution

### Option 1: Rebuild Jenkins with Docker CLI (Recommended)

This is the **easiest and most reliable** solution. The custom Dockerfile installs Docker CLI inside the Jenkins container.

#### Steps:

1. **Stop the current Jenkins container:**
   ```bash
   # On Windows
   docker-compose down
   
   # On Ubuntu/Linux
   docker-compose -f docker-compose.ubuntu.yml down
   ```

2. **Rebuild the Jenkins image with Docker CLI:**
   ```bash
   # On Windows
   docker-compose build jenkins
   
   # On Ubuntu/Linux
   docker-compose -f docker-compose.ubuntu.yml build jenkins
   ```

3. **Start Jenkins:**
   ```bash
   # On Windows
   docker-compose up -d
   
   # On Ubuntu/Linux
   docker-compose -f docker-compose.ubuntu.yml up -d
   ```

4. **Verify Docker is working:**
   ```bash
   # Check Docker is available inside Jenkins container
   docker exec jenkins docker --version
   
   # Check Docker daemon connectivity
   docker exec jenkins docker info
   ```

5. **Run your Jenkins pipeline again** - it should now work!

### Option 2: Manual Docker Installation (If Option 1 doesn't work)

If rebuilding doesn't work, you can manually install Docker inside the running container:

1. **Enter the Jenkins container as root:**
   ```bash
   docker exec -u root -it jenkins bash
   ```

2. **Install Docker CLI:**
   ```bash
   apt-get update
   apt-get install -y docker.io
   # OR use official Docker repository:
   apt-get install -y ca-certificates curl gnupg lsb-release
   install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   chmod a+r /etc/apt/keyrings/docker.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
   apt-get update
   apt-get install -y docker-ce-cli
   ```

3. **Verify installation:**
   ```bash
   docker --version
   docker info
   ```

4. **Exit the container:**
   ```bash
   exit
   ```

**Note:** This manual installation will be lost if you recreate the container. Use Option 1 for a permanent solution.

### Option 3: Mount Docker Binary from Host (Alternative)

If you prefer to use the host's Docker binary instead of installing it in the container:

1. **Edit docker-compose.yml or docker-compose.ubuntu.yml:**
   ```yaml
   volumes:
     - jenkins_home:/var/jenkins_home
     - /var/run/docker.sock:/var/run/docker.sock
     # Add this line (for Linux only):
     - /usr/bin/docker:/usr/bin/docker:ro
   ```

2. **Restart Jenkins:**
   ```bash
   docker-compose restart jenkins
   ```

**Note:** This only works on Linux. Windows Docker Desktop doesn't need this.

## Verification

After applying the fix, verify everything works:

1. **Check Docker command:**
   ```bash
   docker exec jenkins command -v docker
   # Should output: /usr/bin/docker (or similar path)
   ```

2. **Check Docker version:**
   ```bash
   docker exec jenkins docker --version
   # Should show Docker version
   ```

3. **Check Docker daemon access:**
   ```bash
   docker exec jenkins docker info
   # Should show Docker system information
   ```

4. **Run your Jenkins pipeline** - the "Validate Environment" stage should now pass!

## Troubleshooting

### Issue: "Permission denied" when accessing Docker socket

**Solution:**
```bash
# Fix Docker socket permissions
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

### Issue: Docker command still not found after rebuild

**Solution:**
1. Check if the build succeeded:
   ```bash
   docker images | grep jenkins-custom
   ```

2. Verify Docker is installed in the image:
   ```bash
   docker run --rm jenkins-custom:latest docker --version
   ```

3. If it fails, check the Dockerfile.jenkins build logs:
   ```bash
   docker-compose build --no-cache jenkins
   ```

### Issue: "Cannot connect to the Docker daemon"

**Solution:**
1. Ensure Docker socket is mounted:
   ```bash
   docker exec jenkins ls -la /var/run/docker.sock
   ```

2. Check Docker is running on the host:
   ```bash
   docker info
   ```

3. Restart Jenkins container:
   ```bash
   docker-compose restart jenkins
   ```

## What Changed

The following files were updated to fix this issue:

1. **Dockerfile.jenkins** - Now installs Docker CLI inside the container
2. **docker-compose.yml** - Uses the custom Jenkins image with Docker CLI
3. **docker-compose.ubuntu.yml** - Uses the custom Jenkins image with Docker CLI
4. **Jenkinsfile** - Enhanced error messages to help diagnose Docker issues

## Additional Notes

- The custom Jenkins image includes Docker CLI, so you don't need to mount the Docker binary from the host
- The entrypoint script automatically fixes Docker socket permissions on startup
- This solution works on both Windows (Docker Desktop) and Linux servers
- The Docker socket (`/var/run/docker.sock`) is still mounted to allow Jenkins to communicate with the host Docker daemon

