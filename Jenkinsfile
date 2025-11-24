pipeline {
  agent any
  
  environment {
    // Docker image name - automatically uses Jenkins job name
    // To customize, set IMAGE_NAME in Jenkins job configuration -> Environment variables
    IMAGE_NAME = "${env.JOB_NAME.split('/').last().toLowerCase().replaceAll(' ', '-')}"
    DOCKER_BUILDKIT = "1"
  }
  
  options {
    timeout(time: 30, unit: 'MINUTES')
    retry(1)
    timestamps()
  }
  
  // Automatic triggers when code is merged to main branch
  triggers {
    // Poll SCM every 2 minutes to automatically detect changes (fallback if webhooks not configured)
    pollSCM('H/2 * * * *')
    
    // For GitHub/GitLab webhooks, configure in Jenkins job settings:
    // Jenkins -> Your Job -> Configure -> Build Triggers -> 
    // Check "GitHub hook trigger for GITScm polling" or "Build when a change is pushed to GitLab"
  }
  
  stages {
    stage('Validate Environment') {
      steps {
        script {
          // Validate Docker is available and accessible
          def dockerAvailable = sh(script: 'command -v docker', returnStdout: true).trim()
          if (!dockerAvailable) {
            error("Docker is not installed or not in PATH. Please install Docker on the Jenkins agent.")
          }
          
          // Check Docker daemon is running and accessible
          def dockerInfo = sh(script: 'docker info', returnStdout: true, returnStatus: true)
          if (dockerInfo != 0) {
            error("Docker daemon is not accessible. Please ensure:\n" +
                  "1. Docker is installed and running\n" +
                  "2. Jenkins user is added to docker group: sudo usermod -aG docker jenkins\n" +
                  "3. Jenkins service is restarted after adding user to docker group")
          }
          
          echo "✅ Docker validation passed"
          sh 'docker --version'
          sh 'docker info | head -5'
        }
      }
    }
    
    stage('Checkout') {
      steps {
        checkout scm
        script {
          // For multibranch pipelines, BRANCH_NAME is automatically set by Jenkins
          // Also check GIT_BRANCH which might be set
          def branchName = env.BRANCH_NAME ?: env.GIT_BRANCH ?: sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
          
          // Normalize branch name (remove origin/, remotes/, and any path prefixes)
          branchName = branchName.replaceAll('origin/', '').replaceAll('remotes/', '').replaceAll('^.*/', '').trim()
          env.BRANCH_NAME = branchName
          
          echo "=========================================="
          echo "Checked out branch: ${branchName}"
          echo "Commit: ${GIT_COMMIT}"
          echo "Build Number: ${env.BUILD_NUMBER}"
          echo "Original BRANCH_NAME: ${env.BRANCH_NAME ?: 'not set'}"
          echo "Original GIT_BRANCH: ${env.GIT_BRANCH ?: 'not set'}"
          echo "=========================================="
        }
      }
    }
    
    stage('Build Docker image') {
      steps {
        script {
          // Get branch name from environment (set in Checkout stage)
          def branchName = (env.BRANCH_NAME ?: '').toLowerCase().trim()
          
          // Debug: Print all environment variables related to branch
          echo "DEBUG INFO:"
          echo "  BRANCH_NAME: ${env.BRANCH_NAME}"
          echo "  Normalized branch: ${branchName}"
          echo "  GIT_BRANCH: ${env.GIT_BRANCH ?: 'not set'}"
          
          // Check if this is the main branch (exact match after normalization)
          def isMainBranch = branchName == 'main' || branchName == 'master'
          
          echo "Branch detected: '${branchName}'"
          echo "Is main branch: ${isMainBranch}"
          
          if (!isMainBranch) {
            echo "⚠️ SKIPPING Docker build - not on main/master branch"
            echo "Current branch: '${branchName}'"
            echo "Expected: 'main' or 'master'"
            return
          }
          
          echo "✅ Building Docker image for main branch..."
          def shortCommit = sh(script: "echo ${GIT_COMMIT} | cut -c1-7", returnStdout: true).trim()
          def imageTag = "${IMAGE_NAME}:main-${shortCommit}"
          def imageTagLatest = "${IMAGE_NAME}:main-latest"
          
          echo "Building Docker image for main branch (after staging merge)..."
          echo "Image tags: ${imageTag}, ${imageTagLatest}"
          
          // Build Docker image with proper error handling
          def buildResult = sh(
            script: """
              docker build \
                --tag ${imageTag} \
                --tag ${imageTagLatest} \
                --progress=plain \
                .
            """,
            returnStatus: true
          )
          
          if (buildResult != 0) {
            error("Docker build failed with exit code ${buildResult}. Check the build logs above for details.")
          }
          
          // Verify image was created
          def imageExists = sh(
            script: "docker images -q ${imageTag}",
            returnStdout: true
          ).trim()
          
          if (!imageExists) {
            error("Docker image ${imageTag} was not created after build. Build may have failed silently.")
          }
          
          // Save image metadata
          env.DOCKER_IMAGE_TAG = imageTag
          env.DOCKER_IMAGE_LATEST = imageTagLatest
          
          echo "✅ Docker image built successfully!"
          sh "docker images ${IMAGE_NAME} | head -3"
        }
      }
    }
    
    stage('Save Docker image') {
      steps {
        script {
          def branchName = (env.BRANCH_NAME ?: '').toLowerCase().replaceAll('origin/', '').replaceAll('remotes/', '').replaceAll('^.*/', '')
          def isMainBranch = branchName == 'main' || branchName == 'master'
          
          if (!isMainBranch) {
            echo "⚠️ Skipping Docker save - not on main/master branch"
            echo "Current branch: '${branchName}'"
            return
          }
          def shortCommit = sh(script: "echo ${GIT_COMMIT} | cut -c1-7", returnStdout: true).trim()
          def imageTag = "${IMAGE_NAME}:main-${shortCommit}"
          def imageTagLatest = "${IMAGE_NAME}:main-latest"
          
          // Save image to tar file as backup
          def timestamp = sh(script: 'date +%Y%m%d-%H%M%S', returnStdout: true).trim()
          def tarFileName = "${IMAGE_NAME}-main-${shortCommit}-${timestamp}.tar"
          
          echo "Saving Docker image to tar file: ${tarFileName}"
          def saveResult = sh(
            script: "docker save -o ${tarFileName} ${imageTag}",
            returnStatus: true
          )
          
          if (saveResult != 0) {
            error("Failed to save Docker image to ${tarFileName}")
          }
          
          // Verify tar file was created and has content
          def tarSize = sh(
            script: "ls -lh ${tarFileName} | awk '{print \$5}'",
            returnStdout: true
          ).trim()
          
          if (!tarSize || tarSize == "0") {
            error("Docker image tar file ${tarFileName} is empty or was not created")
          }
          
          echo "Image tar file size: ${tarSize}"
          
          // Archive the tar file
          archiveArtifacts artifacts: "${tarFileName}", allowEmptyArchive: false
          
          echo "✅ Docker image saved successfully: ${tarFileName}"
          echo "Image tags: ${imageTag}, ${imageTagLatest}"
        }
      }
    }
    
    stage('List Docker images') {
      steps {
        script {
          def branchName = (env.BRANCH_NAME ?: '').toLowerCase().replaceAll('origin/', '').replaceAll('remotes/', '').replaceAll('^.*/', '')
          def isMainBranch = branchName == 'main' || branchName == 'master'
          
          if (!isMainBranch) {
            echo "⚠️ Skipping image listing - not on main/master branch"
            return
          }
          sh "docker images ${IMAGE_NAME} | head -10"
        }
      }
    }
  }
  
  post {
    success {
      script {
        echo "=========================================="
        echo "✅ Pipeline succeeded!"
        echo "Docker image saved for main branch (after staging merge)."
        echo "Image: ${env.DOCKER_IMAGE_TAG}"
        echo "Latest: ${env.DOCKER_IMAGE_LATEST}"
        echo "=========================================="
      }
    }
    failure {
      script {
        echo "=========================================="
        echo "❌ Pipeline failed!"
        echo "Check the console output above for error details."
        echo "=========================================="
      }
    }
    always {
      script {
        echo "Pipeline finished. Check artifacts for saved Docker image tar file."
      }
    }
  }
}
