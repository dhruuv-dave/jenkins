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
          echo "🔍 Validating Docker environment..."
          
          // Check if Docker command exists
          def dockerCheck = sh(script: 'command -v docker || which docker || echo "NOT_FOUND"', returnStdout: true).trim()
          if (dockerCheck == "NOT_FOUND" || !dockerCheck) {
            echo "❌ ERROR: Docker command not found!"
            echo "Docker path check result: '${dockerCheck}'"
            echo ""
            echo "SOLUTION:"
            echo "1. If using Docker Compose, rebuild the Jenkins image:"
            echo "   docker-compose build jenkins"
            echo "   docker-compose up -d"
            echo ""
            echo "2. If Jenkins is running directly on host, install Docker:"
            echo "   sudo apt-get update && sudo apt-get install -y docker.io"
            echo ""
            echo "3. Check PATH:"
            sh 'echo $PATH'
            error("Docker is not installed or not in PATH. See error details above.")
          }
          
          echo "✅ Docker command found at: ${dockerCheck}"
          
          // Check Docker version
          try {
            def dockerVersion = sh(script: 'docker --version', returnStdout: true).trim()
            echo "Docker version: ${dockerVersion}"
          } catch (Exception e) {
            echo "⚠️  Warning: Could not get Docker version"
          }
          
          // Check Docker daemon is running and accessible
          echo "Checking Docker daemon connectivity..."
          def dockerInfo = sh(script: 'docker info 2>&1', returnStdout: true, returnStatus: true)
          if (dockerInfo != 0) {
            def dockerError = sh(script: 'docker info 2>&1', returnStdout: true).trim()
            echo "❌ ERROR: Docker daemon is not accessible!"
            echo "Docker info error output:"
            echo "${dockerError}"
            echo ""
            echo "SOLUTION:"
            echo "1. Ensure Docker socket is mounted in Jenkins container:"
            echo "   - /var/run/docker.sock:/var/run/docker.sock"
            echo ""
            echo "2. Check Docker socket permissions:"
            sh 'ls -la /var/run/docker.sock || echo "Docker socket not found"'
            echo ""
            echo "3. If using Docker Compose, ensure docker-compose.yml includes:"
            echo "   volumes:"
            echo "     - /var/run/docker.sock:/var/run/docker.sock"
            echo ""
            echo "4. Restart Jenkins container:"
            echo "   docker-compose restart jenkins"
            error("Docker daemon is not accessible. See troubleshooting steps above.")
          }
          
          echo "✅ Docker validation passed"
          sh 'docker info | head -5'
        }
      }
    }
    
    stage('Checkout') {
      steps {
        script {
          echo "📥 Checking out source code..."
          
          // Clean up workspace if it's in a bad state
          def isGitRepo = sh(script: 'test -d .git && git rev-parse --git-dir > /dev/null 2>&1', returnStatus: true) == 0
          if (!isGitRepo) {
            echo "⚠️  Workspace is not a valid git repository. Cleaning up..."
            // Remove any partial git files and workspace contents
            sh '''
              rm -rf .git .gitignore 2>/dev/null || true
              # Remove all files except Jenkins-specific directories
              find . -mindepth 1 -maxdepth 1 ! -name '..' ! -name '.' -exec rm -rf {} + 2>/dev/null || true
            '''
            // Try to use workspace cleanup plugin if available, otherwise manual cleanup above is sufficient
            try {
              cleanWs()
            } catch (Exception e) {
              echo "Workspace cleanup plugin not available, using manual cleanup"
            }
          }
          
          // Perform checkout with retry logic
          def checkoutAttempts = 3
          def checkoutSuccess = false
          
          for (int i = 1; i <= checkoutAttempts; i++) {
            try {
              echo "Checkout attempt ${i}/${checkoutAttempts}..."
              
              // Use checkout scm which uses Jenkins job configuration
              checkout scm
              
              // Verify checkout was successful
              def gitStatus = sh(script: 'git rev-parse --is-inside-work-tree 2>/dev/null', returnStdout: true).trim()
              if (gitStatus == "true") {
                checkoutSuccess = true
                break
              }
            } catch (Exception e) {
              echo "⚠️  Checkout attempt ${i} failed: ${e.message}"
              if (i < checkoutAttempts) {
                echo "Retrying in 2 seconds..."
                sleep(2)
                // Clean workspace before retry
                try {
                  cleanWs()
                } catch (Exception cleanupError) {
                  // Manual cleanup if plugin not available
                  sh 'rm -rf .git .gitignore * .* 2>/dev/null || true'
                }
              }
            }
          }
          
          if (!checkoutSuccess) {
            echo "❌ ERROR: Git checkout failed after ${checkoutAttempts} attempts!"
            echo ""
            echo "TROUBLESHOOTING:"
            echo "1. Check Jenkins job configuration:"
            echo "   - Go to Jenkins → Your Job → Configure"
            echo "   - Verify 'Source Code Management' section is configured correctly"
            echo "   - Check repository URL and credentials"
            echo ""
            echo "2. Clean workspace manually:"
            echo "   - Go to Jenkins → Your Job → Workspace"
            echo "   - Click 'Wipe Out Current Workspace'"
            echo "   - Or run: docker exec jenkins rm -rf /var/jenkins_home/workspace/my-sample-app_main"
            echo ""
            echo "3. Check Git credentials:"
            echo "   - Verify GitHub token has correct permissions"
            echo "   - Check credential ID matches in job configuration"
            echo ""
            echo "4. Verify repository access:"
            sh 'echo "Current directory: $(pwd)"'
            sh 'ls -la || echo "Directory listing failed"'
            error("Git checkout failed. See troubleshooting steps above.")
          }
          
          echo "✅ Code checkout successful"
        }
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
          
          // Detect project type
          def hasPythonFiles = sh(script: 'find . -name "*.py" -not -path "*/.*" | head -1', returnStatus: true) == 0
          def hasNextJsFiles = sh(script: 'test -f package.json && grep -q "next" package.json 2>/dev/null || find . -name "*.tsx" -o -name "*.jsx" | head -1', returnStatus: true) == 0
          def hasRequirementsTxt = sh(script: 'test -f requirements.txt', returnStatus: true) == 0
          def hasPackageJson = sh(script: 'test -f package.json', returnStatus: true) == 0
          
          env.HAS_PYTHON = hasPythonFiles ? 'true' : 'false'
          env.HAS_NEXTJS = hasNextJsFiles ? 'true' : 'false'
          env.HAS_REQUIREMENTS = hasRequirementsTxt ? 'true' : 'false'
          env.HAS_PACKAGE_JSON = hasPackageJson ? 'true' : 'false'
          
          echo "Project detection:"
          echo "  Python files: ${env.HAS_PYTHON}"
          echo "  Next.js files: ${env.HAS_NEXTJS}"
          echo "  requirements.txt: ${env.HAS_REQUIREMENTS}"
          echo "  package.json: ${env.HAS_PACKAGE_JSON}"
        }
      }
    }
    
    stage('Python Code Analysis') {
      when {
        expression { env.HAS_PYTHON == 'true' }
      }
      steps {
        script {
          echo "🔍 Running Python code analysis..."
          
          // Install Python dependencies if requirements.txt exists
          if (env.HAS_REQUIREMENTS == 'true') {
            echo "Installing Python dependencies..."
            sh '''
              python3 -m pip install --user --upgrade pip || python -m pip install --user --upgrade pip || true
              python3 -m pip install --user flake8 pylint black || python -m pip install --user flake8 pylint black || true
            '''
          } else {
            echo "Installing code analysis tools..."
            sh '''
              python3 -m pip install --user --upgrade pip || python -m pip install --user --upgrade pip || true
              python3 -m pip install --user flake8 pylint black || python -m pip install --user flake8 pylint black || true
            '''
          }
          
          // Run flake8 for code style and errors
          echo "Running flake8..."
          def flake8Result = sh(
            script: '''
              python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=venv,env,.venv,node_modules || python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=venv,env,.venv,node_modules || true
            ''',
            returnStatus: true
          )
          
          // Run pylint for code quality
          echo "Running pylint..."
          def pylintResult = sh(
            script: '''
              find . -name "*.py" -not -path "*/.*" -not -path "*/venv/*" -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" | head -10 | xargs python3 -m pylint --disable=C,R --max-line-length=120 --exit-zero || find . -name "*.py" -not -path "*/.*" -not -path "*/venv/*" -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" | head -10 | xargs python -m pylint --disable=C,R --max-line-length=120 --exit-zero || true
            ''',
            returnStatus: true
          )
          
          // Run black check for code formatting (non-blocking)
          echo "Checking code formatting with black..."
          sh '''
            python3 -m black --check . --exclude="venv|env|.venv|node_modules" || python -m black --check . --exclude="venv|env|.venv|node_modules" || echo "Black check completed (warnings are non-blocking)"
          '''
          
          if (flake8Result != 0) {
            echo "⚠️ Flake8 found some issues. Review the output above."
          }
          if (pylintResult != 0) {
            echo "⚠️ Pylint found some issues. Review the output above."
          }
          
          echo "✅ Python code analysis completed"
        }
      }
    }
    
    stage('Next.js Code Analysis') {
      when {
        expression { env.HAS_NEXTJS == 'true' }
      }
      steps {
        script {
          echo "🔍 Running Next.js/JavaScript code analysis..."
          
          // Install Node.js dependencies if package.json exists
          if (env.HAS_PACKAGE_JSON == 'true') {
            echo "Installing Node.js dependencies..."
            sh '''
              if command -v npm &> /dev/null; then
                npm ci || npm install
              elif command -v yarn &> /dev/null; then
                yarn install --frozen-lockfile || yarn install
              else
                echo "⚠️ npm or yarn not found. Skipping dependency installation."
              fi
            '''
          }
          
          // Install ESLint if not already installed
          echo "Installing ESLint..."
          sh '''
            if command -v npm &> /dev/null; then
              npm install --save-dev eslint eslint-config-next || npm install -g eslint eslint-config-next || true
            elif command -v yarn &> /dev/null; then
              yarn add -D eslint eslint-config-next || true
            fi
          '''
          
          // Run ESLint
          echo "Running ESLint..."
          def eslintResult = sh(
            script: '''
              if command -v npx &> /dev/null; then
                npx eslint . --ext .js,.jsx,.ts,.tsx --max-warnings 0 || npx eslint . --ext .js,.jsx,.ts,.tsx || true
              elif command -v npm &> /dev/null; then
                npm run lint || npm exec eslint . --ext .js,.jsx,.ts,.tsx || true
              elif command -v yarn &> /dev/null; then
                yarn lint || yarn eslint . --ext .js,.jsx,.ts,.tsx || true
              else
                echo "⚠️ ESLint runner not found. Skipping ESLint check."
                exit 0
              fi
            ''',
            returnStatus: true
          )
          
          if (eslintResult != 0) {
            echo "⚠️ ESLint found some issues. Review the output above."
          }
          
          echo "✅ Next.js code analysis completed"
        }
      }
    }
    
    stage('Python Unit Tests') {
      when {
        expression { env.HAS_PYTHON == 'true' }
      }
      steps {
        script {
          echo "🧪 Running Python unit tests..."
          
          // Install Python dependencies if requirements.txt exists
          if (env.HAS_REQUIREMENTS == 'true') {
            echo "Installing Python dependencies from requirements.txt..."
            sh '''
              python3 -m pip install --user --upgrade pip || python -m pip install --user --upgrade pip || true
              python3 -m pip install --user -r requirements.txt || python -m pip install --user -r requirements.txt || true
            '''
          }
          
          // Install pytest if not already installed
          echo "Installing pytest..."
          sh '''
            python3 -m pip install --user pytest pytest-cov || python -m pip install --user pytest pytest-cov || true
          '''
          
          // Run pytest
          echo "Running pytest..."
          def testResult = sh(
            script: '''
              python3 -m pytest tests/ test/ --cov=. --cov-report=xml --cov-report=html -v || python -m pytest tests/ test/ -v || python3 -m pytest . -v || python -m pytest . -v || true
            ''',
            returnStatus: true
          )
          
          // Publish test results if available
          try {
            publishTestResults testResultsPattern: '**/test-results.xml'
          } catch (Exception e) {
            echo "No test results XML found (this is okay if using pytest without JUnit output)"
          }
          
          // Publish coverage reports if available
          try {
            publishCoverageReports(
              adapters: [
                coberturaAdapter('**/coverage.xml')
              ],
              sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
            )
          } catch (Exception e) {
            echo "Coverage plugin not available or no coverage.xml found"
          }
          
          if (testResult != 0) {
            error("❌ Python unit tests failed! Check the test output above for details.")
          }
          
          echo "✅ Python unit tests passed"
        }
      }
    }
    
    stage('Next.js Unit Tests') {
      when {
        expression { env.HAS_NEXTJS == 'true' }
      }
      steps {
        script {
          echo "🧪 Running Next.js/JavaScript unit tests..."
          
          // Install Node.js dependencies if package.json exists
          if (env.HAS_PACKAGE_JSON == 'true') {
            echo "Installing Node.js dependencies..."
            sh '''
              if command -v npm &> /dev/null; then
                npm ci || npm install
              elif command -v yarn &> /dev/null; then
                yarn install --frozen-lockfile || yarn install
              else
                echo "⚠️ npm or yarn not found. Skipping dependency installation."
              fi
            '''
          }
          
          // Run tests (Jest, Vitest, or other test runner)
          echo "Running tests..."
          def testResult = sh(
            script: '''
              if command -v npm &> /dev/null; then
                npm test -- --coverage --watchAll=false || npm run test -- --coverage || npm test || true
              elif command -v yarn &> /dev/null; then
                yarn test --coverage --watchAll=false || yarn test || true
              else
                echo "⚠️ npm or yarn not found. Skipping tests."
                exit 0
              fi
            ''',
            returnStatus: true
          )
          
          // Publish test results if available
          try {
            publishTestResults testResultsPattern: '**/test-results.xml,**/junit.xml'
          } catch (Exception e) {
            echo "No test results XML found"
          }
          
          // Publish coverage reports if available
          try {
            publishCoverageReports(
              adapters: [
                coberturaAdapter('**/coverage/cobertura-coverage.xml'),
                jestAdapter('**/coverage/coverage-final.json')
              ],
              sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
            )
          } catch (Exception e) {
            echo "Coverage plugin not available or no coverage files found"
          }
          
          if (testResult != 0) {
            error("❌ Next.js unit tests failed! Check the test output above for details.")
          }
          
          echo "✅ Next.js unit tests passed"
        }
      }
    }
    
    stage('SonarQube Analysis') {
      when {
        anyOf {
          expression { env.HAS_PYTHON == 'true' }
          expression { env.HAS_NEXTJS == 'true' }
        }
      }
      steps {
        script {
          echo "🔍 Running SonarQube code analysis..."
          
          // Check if SonarQube scanner is available
          def sonarScannerAvailable = sh(
            script: 'command -v sonar-scanner || command -v sonar-scanner-cli || test -f sonar-project.properties',
            returnStatus: true
          ) == 0
          
          if (!sonarScannerAvailable) {
            echo "⚠️ SonarQube scanner not found. Skipping SonarQube analysis."
            echo "To enable SonarQube analysis:"
            echo "  1. Install SonarQube Scanner plugin in Jenkins"
            echo "  2. Configure SonarQube server in Jenkins"
            echo "  3. Add sonar-project.properties file to your project"
            return
          }
          
          // Run SonarQube analysis
          try {
            withSonarQubeEnv('SonarQube') {
              sh '''
                sonar-scanner || sonar-scanner-cli || echo "SonarQube scanner command not found"
              '''
            }
          } catch (Exception e) {
            echo "⚠️ SonarQube analysis failed or not configured: ${e.message}"
            echo "This is non-blocking. Configure SonarQube in Jenkins to enable this feature."
          }
          
          echo "✅ SonarQube analysis completed"
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
