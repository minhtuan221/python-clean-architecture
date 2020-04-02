# Docker Command line

## Build and run
docker build -t python-docker-dev .
docker run --rm -it -p 8080:8080 python-docker-dev
docker run -it --rm --name single-python-script -v "$PWD":/app -w /app python:3 python your-daemon-or-script.py
docker run –d –p 8000:80 –name my-running-site-new aspnet-site-new 

### Get the machine ip
docker-machine ip => for getting ip of the virtual machine if you using toolbox

### Remove none images
docker rmi $(docker images -f "dangling=true" -q)

### Docker composer
docker-compose up/down/pause/restart/unpause
docker-compose up -d --scale web=4 

## Docker ssh to container

https://phase2.github.io/devtools/common-tasks/ssh-into-a-container/

## Docker Composer

https://docs.docker.com/compose/gettingstarted/

## Kompose to convert Docker-compose file to kubernetes

# Linux
curl -L https://github.com/kubernetes/kompose/releases/download/v1.21.0/kompose-linux-amd64 -o kompose

# macOS
curl -L https://github.com/kubernetes/kompose/releases/download/v1.21.0/kompose-darwin-amd64 -o kompose

# Windows
curl -L https://github.com/kubernetes/kompose/releases/download/v1.21.0/kompose-windows-amd64.exe -o kompose.exe

chmod +x kompose
sudo mv ./kompose /usr/local/bin/kompose

## Nginx error with window 10

https://stackoverflow.com/questions/45972812/are-you-trying-to-mount-a-directory-onto-a-file-or-vice-versa

Answer for people using Docker Toolbox

There have been at least 3 answers here touching on the problem, but not explaining it properly and not giving a full solution. This is just a folder mounting problem.

Description of the problem:

Docker Toolbox bypasses the Hyper-V requirement of Docker by creating a virtual machine (in VirtualBox, which comes bundled). Docker is installed and ran inside the VM. In order for Docker to function properly, it needs to have access to the from the host machine. Which here it doesn't.

After I installed Docker Toolbox it created the VirtualBox VM and only mounted C:\Users to the machine, as \c\Users\. My project was in C:\projects so nowhere on the mounted volume. When I was sending the path to the VM, it would not exist, as C:\projects isn't mounted. Hence, the error above.

Let's say I had my project containing my ngnix config in C:/projects/project_name/

Fixing it:

1. Go to VirtualBox, right click on Default (the VM from Docker) > Settings > Shared Folders
2. Clicking the small icon with the plus on the right side, Add a new share. I used the following settings: Auto-mount, Make Permanent
3. The above will map C:\projects to /projects (ROOT/projects) in the VM, meaning that now you can reference any path in projects like this: /projects/project_name - because project_name from C:\projects\project_name is now mounted.
To use relative paths, please consider naming the path c/projects not projects
4. Restart everything and it should now work properly. I manually stopped the virtual machine in VirtualBox and restarted the Docker Toolbox CLI.
In my docker file, I now reference the nginx.conf like this:
volumes:
    - /projects/project_name/docker_config/nginx/nginx.conf:/etc/nginx/conf.d/default.conf