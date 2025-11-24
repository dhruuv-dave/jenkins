pipeline {
  agent any
  environment {
    IMAGE_NAME = "my-sample-app"
    DOCKER_REGISTRY = credentials('docker-registry-url') ?: ''
    DOCKER_CREDENTIALS = credentials('docker-credentials') ?: ''
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
    stage('Checkout') {
      steps {
        checkout scm
        script {
          // For multibranch pipelines, BRANCH_NAME is automatically set
          // If not set, get it from git
          def branchName = env.BRANCH_NAME ?: sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
          
          // Normalize branch name (remove origin/ prefix if present)
          branchName = branchName.replaceAll('origin/', '').replaceAll('remotes/', '').replaceAll('^.*/', '')
          env.BRANCH_NAME = branchName
          
          echo "=========================================="
          echo "Checked out branch: ${branchName}"
          echo "Commit: ${GIT_COMMIT}"
          echo "Build Number: ${env.BUILD_NUMBER}"
          echo "=========================================="
        }
      }
    }
    
    stage('Build Docker image') {
      steps {
        script {
          // For multibranch pipelines, BRANCH_NAME is set by Jenkins
          def branchName = (env.BRANCH_NAME ?: '').toLowerCase().replaceAll('origin/', '').replaceAll('remotes/', '')
          def isMainBranch = branchName == 'main' || branchName == 'master' || 
                            branchName.endsWith('/main') || branchName.endsWith('/master')
          
          echo "Branch detected: ${branchName}"
          echo "Is main branch: ${isMainBranch}"
          
          if (!isMainBranch) {
            echo "⚠️ Skipping Docker build - not on main/master branch"
            echo "Current branch: '${branchName}'"
            return
          }
          
          echo "✅ Building Docker image for main branch..."
          def shortCommit = sh(script: "echo ${GIT_COMMIT} | cut -c1-7", returnStdout: true).trim()
          def imageTag = "${IMAGE_NAME}:main-${shortCommit}"
          def imageTagLatest = "${IMAGE_NAME}:main-latest"
          
          echo "Building Docker image for main branch (after staging merge)..."
          echo "Image tags: ${imageTag}, ${imageTagLatest}"
          
          sh """
            docker build -t ${imageTag} -t ${imageTagLatest} .
          """
          
          // Save image metadata
          env.DOCKER_IMAGE_TAG = imageTag
          env.DOCKER_IMAGE_LATEST = imageTagLatest
          
          echo "Docker image built successfully!"
        }
      }
    }
    
    stage('Save Docker image') {
      steps {
        script {
          def branchName = env.BRANCH_NAME.toLowerCase()
          def isMainBranch = branchName == 'main' || branchName == 'master' || 
                            branchName.contains('main') || branchName.contains('master')
          
          if (!isMainBranch) {
            echo "Skipping Docker save - not on main/master branch"
            return
          }
          def shortCommit = sh(script: "echo ${GIT_COMMIT} | cut -c1-7", returnStdout: true).trim()
          def imageTag = "${IMAGE_NAME}:main-${shortCommit}"
          def imageTagLatest = "${IMAGE_NAME}:main-latest"
          
          // Save image to tar file as backup
          def timestamp = sh(script: 'date +%Y%m%d-%H%M%S', returnStdout: true).trim()
          def tarFileName = "${IMAGE_NAME}-main-${shortCommit}-${timestamp}.tar"
          
          echo "Saving Docker image to tar file: ${tarFileName}"
          sh """
            docker save -o ${tarFileName} ${imageTag}
            ls -lh ${tarFileName}
          """
          
          // Archive the tar file
          archiveArtifacts artifacts: "${tarFileName}", allowEmptyArchive: false
          
          echo "Docker image saved successfully: ${tarFileName}"
          echo "Image tags: ${imageTag}, ${imageTagLatest}"
          
          // Optional: Push to Docker registry if configured
          if (env.DOCKER_REGISTRY && env.DOCKER_CREDENTIALS) {
            echo "Pushing image to registry..."
            sh """
              docker tag ${imageTag} ${DOCKER_REGISTRY}/${imageTag}
              docker tag ${imageTagLatest} ${DOCKER_REGISTRY}/${imageTagLatest}
              docker push ${DOCKER_REGISTRY}/${imageTag}
              docker push ${DOCKER_REGISTRY}/${imageTagLatest}
            """
          }
        }
      }
    }
    
    stage('List Docker images') {
      steps {
        script {
          def branchName = env.BRANCH_NAME.toLowerCase()
          def isMainBranch = branchName == 'main' || branchName == 'master' || 
                            branchName.contains('main') || branchName.contains('master')
          
          if (!isMainBranch) {
            echo "Skipping image listing - not on main/master branch"
            return
          }
          sh 'docker images | grep ${IMAGE_NAME} || true'
        }
      }
    }
  }
  
  post {
    success {
      script {
        echo "Pipeline succeeded. Docker image saved for main branch (after staging merge)."
        echo "Image: ${env.DOCKER_IMAGE_TAG}"
      }
    }
    always {
      script {
        echo "Pipeline finished. Check artifacts for saved Docker image tar file."
      }
    }
  }
}
