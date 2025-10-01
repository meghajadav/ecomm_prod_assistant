## Deployment
  1) Docker:
    a. .dockerignore
    b. Docker

  2) K8(folder for EKR- Kubernetes)
     a. deployment.yaml(all the config related to kubernetes)
     b. service.yaml(to expose the port. It is to handle the issue like whenevr we run the image under the container it changes the IP frequently under the port so such issues need to be tackled)
     c. EKS-with-ECR.yaml

  3) infra-> AWS->cloudformation(AWS native service)    
  
  4) .github/wotkflow
      a. infra.yaml(This we are going to create manually, it means it is not going to be created on every push but once we trigger the job it will be created, only admin can do that)
      b. deploy.yaml 

infra.yaml -> will execute EKS-with-ECR.yaml and infra will be created over the aws
deploy.yaml -> will be responsible for main CICD means docker image will be created and deployed in EKS

### ------------------------- Docker-----------------------------------------------------

To check if docker is running at the left corner should see engine is running

## docker -v -> gives the version of the docker installed  
## docker images -> list all the images  created
docker ps-> the running container is listed
docker ps -a -> list all the containers
docker rmi <image_id> -> it will remove that particular image created
docker build -t prod-assistant .   ->  (-t is for tag, . here indicates that my dockerfile is in the current directory) -> to build the image 
docker stop <container_id> -> stops the container with that container id
docker rm <container_id> -> it will remove the container with that particular id
docker run -d -p 8000:8000 --name <container_custom_name> <image_name_created_using_dockerfile>->Run the docker container
-d (detached mode)

Runs the container in the background (detached).

Without -d, the container runs in the foreground, and you see its logs directly in your terminal.

-p (publish a port)

Maps a container port to a host port, allowing you to access the container’s service from outside.
docker run -d -p 8080:80 nginx
Runs an Nginx container in the background and maps:

Container’s port 80 (default Nginx HTTP port)

To Host’s port 8080



docker run -d -p 8000:8000 --name prod-assistant prod-assistant

## --------------------------------------------------------

in Dockerfile:

WOKDIR /app ->  we create app directory in docker image
COPY . . -> copy everything from the current directory to the above app directory we created




