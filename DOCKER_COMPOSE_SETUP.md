# Docker Compose Setup for Jenkins

This setup automatically fixes Docker socket permissions on both Windows (Docker Desktop) and Ubuntu servers.

## Files

- `docker-compose.yml` - For Windows Docker Desktop (local development)
- `docker-compose.ubuntu.yml` - For Ubuntu/Linux servers
- `jenkins-entrypoint.sh` - Entrypoint script that fixes Docker permissions on startup

## Quick Start

### On Windows (Local Development)

```bash
# Make entrypoint script executable (if using Git Bash)
chmod +x jenkins-entrypoint.sh

# Start Jenkins
docker-compose up -d

# Check logs
docker-compose logs -f jenkins
```

### On Ubuntu Server

```bash
# Make entrypoint script executable
chmod +x jenkins-entrypoint.sh

# Start Jenkins using Ubuntu-specific compose file
docker-compose -f docker-compose.ubuntu.yml up -d

# Check logs
docker-compose -f docker-compose.ubuntu.yml logs -f jenkins
```

## Copying to Another Project

To use this setup in another project:

1. **Copy these files:**
   ```bash
   cp docker-compose.yml /path/to/other/project/
   cp docker-compose.ubuntu.yml /path/to/other/project/
   cp jenkins-entrypoint.sh /path/to/other/project/
   ```

2. **Make entrypoint script executable:**
   ```bash
   chmod +x /path/to/other/project/jenkins-entrypoint.sh
   ```

3. **Start Jenkins:**
   - Windows: `docker-compose up -d`
   - Ubuntu: `docker-compose -f docker-compose.ubuntu.yml up -d`

## How It Works

The `jenkins-entrypoint.sh` script:
1. Runs as root on container startup
2. Fixes Docker socket permissions (`chmod 666`)
3. Calls the original Jenkins entrypoint which switches to the `jenkins` user

This ensures Docker is accessible from Jenkins pipelines without manual intervention.

## Troubleshooting

### Permission Denied Errors

If you still get permission errors:

1. **Check entrypoint script is executable:**
   ```bash
   ls -la jenkins-entrypoint.sh
   # Should show: -rwxr-xr-x
   ```

2. **Check Docker socket permissions inside container:**
   ```bash
   docker exec jenkins ls -la /var/run/docker.sock
   # Should show: srw-rw-rw- (666 permissions)
   ```

3. **Manually fix permissions (temporary):**
   ```bash
   docker exec -u root jenkins chmod 666 /var/run/docker.sock
   ```

### Windows Docker Desktop Issues

If the Docker binary mount causes issues on Windows, the `docker-compose.yml` already has it commented out. Windows Docker Desktop handles Docker differently.

### Ubuntu Server Issues

Make sure:
- Docker is installed: `docker --version`
- Docker socket exists: `ls -la /var/run/docker.sock`
- User has access: `groups` (should include docker group)

## Stopping Jenkins

```bash
# Windows
docker-compose down

# Ubuntu
docker-compose -f docker-compose.ubuntu.yml down
```

## Accessing Jenkins

After starting, access Jenkins at:
- URL: `http://localhost:8080` (or `http://your-server-ip:8080`)
- Get initial admin password:
  ```bash
  # Windows
  docker-compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  
  # Ubuntu
  docker-compose -f docker-compose.ubuntu.yml exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  ```

