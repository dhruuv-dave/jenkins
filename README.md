# my-sample-app

This is a minimal sample repository to test a Jenkins pipeline that builds a Docker image locally.

Files:
- index.html — static page served by nginx
- Dockerfile — builds an nginx image containing index.html
- Jenkinsfile — Declarative Jenkins pipeline that builds the Docker image and lists local images

Quick usage:
1. Initialize git: `git init && git add . && git commit -m "initial"`
2. (Optional) Create branch `staging` and push to remote if using remote repo.
3. Run Jenkins with access to the Docker daemon (see docker-compose.yml included).
4. Create a Multibranch Pipeline in Jenkins or a Pipeline job that uses this repo.
5. Trigger a build on the `staging` branch and verify the image appears on the host with `docker images`.

Notes:
- Mounting `/var/run/docker.sock` into the Jenkins container allows builds to create images on the host.
- For local testing you can also run a Pipeline job and build manually.
