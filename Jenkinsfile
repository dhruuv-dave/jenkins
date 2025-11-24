pipeline {
  agent any
  environment {
    IMAGE_NAME = "my-sample-app"
    DOCKER_REGISTRY = credentials('docker-registry-url') ?: ''
    DOCKER_CREDENTIALS = credentials('docker-credentials') ?: ''
  }
  
  // Trigger when changes are pushed to main branch (e.g., when staging is merged to main)
  triggers {
    // Poll SCM every minute (adjust as needed)
    pollSCM('H/5 * * * *')
  }
  
  stages {
    stage('Checkout') {
      steps {
        checkout scm
        script {
          def branchName = env.BRANCH_NAME ?: sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
          env.BRANCH_NAME = branchName
          echo "Checked out branch: ${branchName} at commit ${GIT_COMMIT}"
        }
      }
    }
    
    stage('Build Docker image') {
      when {
        anyOf {
          branch 'main'
          branch 'master'
          branch 'origin/main'
          branch 'origin/master'
        }
      }
      steps {
        script {
          def shortCommit = sh(script: "echo ${GIT_COMMIT} | cut -c1-7", returnStdout: true).trim()
          def branchName = env.BRANCH_NAME.replaceAll('/', '-')
          def imageTag = "${IMAGE_NAME}:main-${shortCommit}"
          def imageTagLatest = "${IMAGE_NAME}:main-latest"
          
          echo "Building Docker image for main branch (after staging merge)..."
          sh """
            docker build -t ${imageTag} -t ${imageTagLatest} .
          """
          
          // Save image metadata
          env.DOCKER_IMAGE_TAG = imageTag
          env.DOCKER_IMAGE_LATEST = imageTagLatest
        }
      }
    }
    
    stage('Save Docker image') {
      when {
        anyOf {
          branch 'main'
          branch 'master'
          branch 'origin/main'
          branch 'origin/master'
        }
      }
      steps {
        script {
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
      when {
        anyOf {
          branch 'main'
          branch 'master'
          branch 'origin/main'
          branch 'origin/master'
        }
      }
      steps {
        sh 'docker images | grep ${IMAGE_NAME} || true'
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
