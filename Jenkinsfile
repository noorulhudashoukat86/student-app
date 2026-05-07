pipeline {
    agent any

    environment {
        APP_REPO   = 'https://github.com/noorulhudashoukat86/student-app.git'
        TEST_REPO  = 'https://github.com/noorulhudashoukat86/selenium-tests.git'
        APP_URL    = 'http://localhost:5000'
        COMPOSE_FILE = 'docker-compose.yml'
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout Application') {
            steps {
                echo '📦 Cloning application repository...'
                dir('student-app') {
                    git branch: 'main', url: "${APP_REPO}"
                }
            }
        }

        stage('Checkout Tests') {
            steps {
                echo '🧪 Cloning test repository...'
                dir('selenium-tests') {
                    git branch: 'main', url: "${TEST_REPO}"
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Starting application with Docker Compose...'
                dir('student-app') {
                    sh '''
                        docker compose down --remove-orphans || true
                        docker compose build --no-cache
                        docker compose up -d
                    '''
                }
                echo '⏳ Waiting for application to be ready...'
                sh '''
                    for i in $(seq 1 30); do
                        if curl -sf http://localhost:5000/health > /dev/null 2>&1; then
                            echo "✅ Application is ready!"
                            break
                        fi
                        echo "Waiting... ($i/30)"
                        sleep 3
                    done
                '''
            }
        }

        stage('Run Selenium Tests') {
            steps {
                echo '🔬 Building test Docker image...'
                dir('selenium-tests') {
                    sh '''
                        mkdir -p results
                        docker build -t selenium-tests:latest .
                    '''
                }

                echo '▶️ Executing Selenium test cases...'
                sh '''
                    docker run --rm \
                        --network host \
                        -e APP_URL=http://localhost:5000 \
                        -v $(pwd)/selenium-tests/results:/tests/results \
                        selenium-tests:latest \
                        python tests.py 2>&1 | tee selenium-tests/results/test-output.txt
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true,
                          testResults: 'selenium-tests/results/test-results.xml'
                }
            }
        }

        stage('Tear Down') {
            steps {
                echo '🧹 Stopping application containers...'
                dir('student-app') {
                    sh 'docker compose down --remove-orphans || true'
                }
            }
        }
    }

    post {
        always {
            script {
                def pusherEmail = sh(
                    script: "git log -1 --pretty=format:'%ae' || echo 'unknown'",
                    returnStdout: true
                ).trim()

                def buildStatus = currentBuild.currentResult
                def emoji       = buildStatus == 'SUCCESS' ? '✅' : '❌'
                def testOutput  = ''

                try {
                    testOutput = readFile('selenium-tests/results/test-output.txt')
                } catch (e) {
                    testOutput = 'Test output not available.'
                }

                emailext(
                    to: "${pusherEmail}",
                    subject: "${emoji} Jenkins Build #${BUILD_NUMBER} – ${buildStatus} | Student SMS",
                    body: """
<html><body style="font-family:monospace;background:#0d0d0d;color:#e8e8e8;padding:2rem">
<h2 style="color:${buildStatus == 'SUCCESS' ? '#00e5ff' : '#ff4757'}">${emoji} Build ${buildStatus}</h2>
<table style="margin:1rem 0;border-collapse:collapse">
  <tr><td style="color:#888;padding:.3rem 1rem .3rem 0">Build #</td><td>${BUILD_NUMBER}</td></tr>
  <tr><td style="color:#888;padding:.3rem 1rem .3rem 0">Job</td><td>${JOB_NAME}</td></tr>
  <tr><td style="color:#888;padding:.3rem 1rem .3rem 0">Pusher</td><td>${pusherEmail}</td></tr>
  <tr><td style="color:#888;padding:.3rem 1rem .3rem 0">Duration</td><td>${currentBuild.durationString}</td></tr>
  <tr><td style="color:#888;padding:.3rem 1rem .3rem 0">URL</td><td><a href="${BUILD_URL}" style="color:#00e5ff">${BUILD_URL}</a></td></tr>
</table>
<h3 style="color:#888;margin-top:1.5rem">Test Output:</h3>
<pre style="background:#161616;padding:1rem;border-left:3px solid #2a2a2a;overflow:auto;max-height:400px">${testOutput}</pre>
</body></html>
                    """,
                    mimeType: 'text/html'
                )
            }
        }
        success {
            echo '🎉 Pipeline completed successfully!'
        }
        failure {
            echo '💥 Pipeline failed. Check logs above.'
        }
    }
}
