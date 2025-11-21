pipeline {
  agent any
  environment {
    IMAGE_NAME = "my-sample-app"
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'echo "Checked out $(git rev-parse --abbrev-ref HEAD) at commit $GIT_COMMIT"'
      }
    }
    stage('Build Docker image') {
      steps {
        sh '''
          SHORT_COMMIT=$(echo ${GIT_COMMIT} | cut -c1-7)
          docker build -t ${IMAGE_NAME}:${SHORT_COMMIT} -t ${IMAGE_NAME}:latest .
        '''
      }
    }
    stage('List local images') {
      steps {
        sh 'docker images | grep ${IMAGE_NAME} || true'
      }
    }
  }
  post {
    always {
      script {
        echo "Pipeline finished. Local image(s) named ${IMAGE_NAME} should be present on the host Docker."
      }
    }
  }
}
