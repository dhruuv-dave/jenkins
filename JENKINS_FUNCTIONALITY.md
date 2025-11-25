# Jenkins Pipeline Functionality Guide

This document explains how the Jenkins pipeline works in simple, easy-to-understand language.

## What is This Pipeline?

Think of this Jenkins pipeline as an **automated assistant** that watches your code repository and automatically builds Docker images when you make changes. It's like having a robot that:
- Watches for code changes
- Checks if everything is set up correctly
- Builds your application into a Docker image
- Saves the image for later use

## How Does It Start?

The pipeline automatically starts in two ways:

1. **Automatic Checking**: Every 2 minutes, Jenkins checks your repository to see if there are any new changes
2. **Webhooks** (if configured): When you push code to GitHub/GitLab, it immediately tells Jenkins to start a build

## Pipeline Overview

The pipeline runs through several stages, one after another. If any stage fails, the pipeline stops and reports the error.

---

## Stage 1: Validate Environment

**What it does**: Before doing anything, Jenkins checks if Docker is available and working.

**Why it's important**: Just like you'd check if you have the right tools before starting a project, Jenkins makes sure Docker is installed and running.

**What happens**:
- Checks if Docker command is available
- Verifies Docker daemon (the Docker service) is running
- Makes sure Jenkins has permission to use Docker
- Shows Docker version information

**If something is wrong**: The pipeline stops and tells you exactly what needs to be fixed (like "Docker is not installed" or "Jenkins doesn't have permission to use Docker").

---

## Stage 2: Checkout

**What it does**: Jenkins downloads your code from the repository (like GitHub or GitLab).

**Why it's important**: Jenkins needs your code files to build the Docker image.

**What happens**:
- Downloads the latest code from your repository
- Figures out which branch you're working on (main, master, staging, etc.)
- Displays information about:
  - Which branch was checked out
  - The commit ID (a unique identifier for this version of code)
  - The build number

**Think of it like**: Downloading the latest version of a document before you start working on it.

---

## Stage 3: Build Docker Image

**What it does**: This is where Jenkins creates your Docker image from your code.

**Important Rule**: This stage **only runs on the `main` or `master` branch**. If you're on any other branch (like `staging` or `feature-branch`), this stage is skipped.

**Why only main/master?**: This ensures that only production-ready code gets built into Docker images, saving time and resources.

**What happens**:
1. Checks if you're on the main/master branch
2. If yes:
   - Creates a short version of your commit ID (first 7 characters)
   - Builds the Docker image with two tags:
     - `{image-name}:main-{commit-id}` - Specific to this commit
     - `{image-name}:main-latest` - Always points to the latest build
3. Uses your `Dockerfile` to build the image
4. Verifies the image was created successfully
5. Shows a list of related images

**If build fails**: The pipeline stops and shows you the error messages from Docker.

**Image naming**: 
- The image name comes from your Jenkins job name (automatically converted to lowercase)
- You can customize it by setting an `IMAGE_NAME` environment variable in Jenkins

---

## Stage 4: Save Docker Image

**What it does**: Saves your Docker image to a `.tar` file (like a zip file for Docker images).

**Why it's important**: This creates a backup copy of your image that you can:
- Store for later use
- Transfer to other servers
- Keep as a record of what was built

**Important Rule**: Like the build stage, this **only runs on main/master branch**.

**What happens**:
1. Checks if you're on main/master branch
2. If yes:
   - Creates a timestamp (date and time)
   - Saves the Docker image to a `.tar` file with a name like: `my-app-main-abc1234-20240115-143022.tar`
   - Verifies the file was created and has content (not empty)
   - Shows the file size
   - Archives it in Jenkins so you can download it later

**The saved file**: You can find it in Jenkins under "Build Artifacts" after the build completes.

---

## Stage 5: List Docker Images

**What it does**: Shows you a list of Docker images related to your project.

**Why it's useful**: Helps you see what images have been built and verify everything worked correctly.

**Important Rule**: This **only runs on main/master branch**.

**What happens**:
- Displays the first 10 Docker images matching your image name
- This helps you see the build history

---

## Pipeline Settings

### Timeout
- **30 minutes**: If the pipeline runs longer than 30 minutes, it automatically stops
- **Why**: Prevents builds from running forever if something goes wrong

### Retry
- **1 retry**: If a build fails, Jenkins will try once more automatically
- **Why**: Sometimes failures are temporary (like network issues)

### Timestamps
- Every message in the build log shows the time it happened
- **Why**: Makes it easier to debug issues and see how long each step took

---

## What Happens After the Pipeline?

After all stages complete, Jenkins runs "post-actions" based on whether the pipeline succeeded or failed:

### If Successful ✅
- Shows a success message
- Displays the Docker image tags that were created
- Confirms the image was saved

### If Failed ❌
- Shows a failure message
- Tells you to check the console output for error details

### Always (Success or Failure)
- Reminds you to check the artifacts (saved files) for the Docker image tar file

---

## How It All Works Together

Here's a simple example of what happens:

1. **You push code** to the `main` branch on GitHub
2. **Jenkins detects** the change (either automatically or via webhook)
3. **Pipeline starts**:
   - ✅ Validates Docker is working
   - ✅ Downloads your code
   - ✅ Builds Docker image (because you're on main branch)
   - ✅ Saves image to tar file
   - ✅ Lists images to confirm
4. **Pipeline completes** successfully
5. **You can download** the saved Docker image from Jenkins

---

## Branch Behavior

The pipeline behaves differently based on which branch you're on:

### Main/Master Branch
- ✅ All stages run
- ✅ Docker image is built
- ✅ Image is saved to tar file
- ✅ Images are listed

### Other Branches (staging, feature-branch, etc.)
- ✅ Environment validation runs
- ✅ Code is checked out
- ⏭️ Build stage is **skipped**
- ⏭️ Save stage is **skipped**
- ⏭️ List stage is **skipped**

**Why?**: This saves time and resources. You only build Docker images for production-ready code on the main branch.

---

## Environment Variables

The pipeline uses some automatic settings:

- **IMAGE_NAME**: Automatically set to your Jenkins job name (converted to lowercase, with spaces replaced by dashes)
- **DOCKER_BUILDKIT**: Set to "1" to enable faster Docker builds
- **BRANCH_NAME**: Automatically detected from your repository
- **GIT_COMMIT**: The commit ID of the code being built

You can override `IMAGE_NAME` by setting it in Jenkins job configuration if you want a custom name.

---

## Common Scenarios

### Scenario 1: First Time Setup
1. Create Jenkins job pointing to your repository
2. Pipeline runs automatically
3. If Docker isn't set up, validation stage fails with clear error message
4. Fix Docker setup and try again

### Scenario 2: Normal Development
1. You work on a `feature-branch`
2. Push code to repository
3. Pipeline runs but skips Docker build (not on main branch)
4. Merge to main branch
5. Pipeline runs again, this time builds Docker image

### Scenario 3: Production Build
1. Code is on `main` branch
2. Pipeline automatically builds Docker image
3. Image is saved as tar file
4. You can download and deploy the image

---

## Summary

This Jenkins pipeline is like an automated factory that:
- **Watches** your code repository for changes
- **Validates** everything is set up correctly
- **Builds** Docker images only for production code (main/master branch)
- **Saves** images as backup files
- **Reports** success or failure clearly

It's designed to be **automatic**, **safe** (only builds production code), and **helpful** (clear error messages and saved artifacts).

The pipeline is smart enough to:
- Skip unnecessary builds on non-production branches
- Validate prerequisites before starting
- Save your work automatically
- Retry on temporary failures
- Stop if something goes wrong

All you need to do is push your code, and Jenkins handles the rest! 🚀

