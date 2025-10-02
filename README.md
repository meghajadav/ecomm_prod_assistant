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



# -------------------##########################----------------------------
1. Elastic Container Service:
    - It is AWS own property container orchestration server
    - Docker image we have can be simply executed on ECS and ECS will manage it automatically.
    - manage automatically means scheduling, scaling, healthcheck etc will be managed by ECS.
    - ECS can be run in 2 mode:
        1. EC2
        2. Fargate
    - In EC2 mode we manage the cluster
    - In fargate aws will manage the server
    - ECS is AWS specific orchestration service
    - we have app which we create image and deploy it in docker container


# ------------------------------------------------------------------------------------------------
## For Deployment
In this project we have:
- infra folder containing eks_with_ecr.yaml
- k8 folder has deployment.yaml and service.yaml
- workflows has deploy.yaml and infra.yaml

Now the first file called here will be infra.yaml in workflows which in turn will call eks_with_ecr.yaml in infra which in turn will call deploy.yaml in workflows which in turn will call deployment.yaml and service.yaml in k8.

infra.yaml->eks_with_ecr.yaml->deloy.yaml-> deployment.yaml and service.yaml


To start with deployment first set all the secret keys in github secrets that is goto repo -> settings->secrets on left pane->secrets and variables->actions->new repository secret-> give key as an for example OPENAI_API_KEY that is name and the secret is the key generated from openai.

# KEYS SETUP IN GITHUB SECRETS:
    1. ASTRA_DB_API_ENDPOINT
    2. ASTRA_DB_APPLICATION_TOKEN
    3. ASTRA_DB_KEYSPACE
    4. GOOGLE_API_KEY
    5. OPENAI_API_KEY
    6. AWS_ACCESS_KEY
    7. AWS_SECRET_ACCESS_KEY
    8. AWS_REGION

Now in AWS IAM we will create the user:
    - step1:  user name-> prod-assistant-deploy->on next attach policy-for POC purpose i attached administrator access policy->next->create user and now the user gets created

    - step2: Now click on user we created to get the keys->security credentials->Create Access keys->check CLI->click create secret access key

    - step3: Now copy this access key and secret access key and save it somewhere. It is required to connect to the aws.

    - step4: copy the aws region we are working on and save it somehere.

    - step5: Copy Access key and Secret Access key in github secrets

    - Step6: Copy EKS cluster name from eks-with-ecr.yaml and ECRRepositoryName from eks-with-ecr.yaml. Also copy ECRRegistryName from eks-with-ecr.yaml

    - Step7: Create Key value in github secrets for ECRRepositoryName and ECRRegistryName.yaml.

    - Step8: Go to Rpository in github click on actions and from there click on provision infra EKS+ECR and there click on Run workflow and the infra for our project will be created.
