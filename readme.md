# Challenge Development Process: Hosted Challenges

## Purpose

Challenges must be organized in a standard format in order to:
- Automate deployment to CTFd
- Facilitate the creation of a development -> testing -> production pipeline
- Make it easier to modify challenge state over time and on game day

This repository is strictly for **Hosted Challenges**. File-based Challenges are maintained in a different repository.

## Kubernetes

Hosted challenges are deployed on a Google Kubernetes Engine (GKE) cluster. Kubernetes affords CTF organizers several benefits:
- Challenges are self-healing. If a challenge goes down, the CTF administrator can instruct Kubernetes to automatically restart it.
- Challenges are replicated. The CTF administrator can specify a number of replicas for pods in a Deployment or StatefulSet. Replication ensures that challenges are scalable and always available.
- Challenges are easy to deploy and their state is easy to update in-place.
- Challenges can have resource limits. Resource limits protect against user overuse and inefficient code by ensuring one resource-hungry challenge pod does not compromise the entire cluster.

## HAProxy

## Assumptions
This repository is associated with the Chik-p project and as such makes several assumptions: 
- You have a private multi-node GKE cluster behind a public HAProxy load balancer
- You wish to deploy challenges that players connect to using netcat, ssh, or their web browser.
- You wish to expose challenges to the outside world either using a **NodePort Service** (for netcat and SSH challenges) or **ingress-nginx** (for web-based challenges).
- Hosted challenges are packaged as Docker images.

## Single-Connection vs. Multi-Connection Challenges

In Kubernetes, challenge pods are often replicated. Replication can cause unwanted side effects. For example, consider a web-based challenge where you must obtain a base64-encoded string from a web server, decode the string, and reply with the decoded string to get the flag. Throughout the course of this challenge, you must create and maintain a session with the destination web server. Solving this challenge requires two HTTP requests, one request to retrieve the base64-encoded string and another to reply with the decoded string. Now, imagine that this challenge has 2 replicas on Kubernetes. Since HTTP is a connectionless protocol,it does not guarantee that your two requests will be sent over the same connection. Therefore it is possible that your first request is sent to one replica and your second request to another replica, due to Kubernetes' internal load balancing. The second replica of course has no session information about you (only the first replica does) therefore it will not send back the flag but will likely ignore your request. We must ensure that both requests go to the same replica when using a connectionless protocol like HTTP.

A **single-connection challenge** can be solved using a single web request or over the course of a single TCP connection. We do not care which challenge replica the user connects to in a single-connection challenge since the whole challenge can be solved over one connection.

A **multi-connection challenge** requires two or more web requests or multiple TCP connections to solve. We must ensure that the player connects back to the same replica in a multi-connection challenge.

For example, a web-based challenge that does not keep session information is likely a single-connection challenge. But a web-based challenge that sets a cookie in the user's browser is likely a multi-connection challenge. Similarly, a challenge that requires the player to SSH into a Debian box once is a single-connection challenge but if the player MUST exit and reconnect to solve challenge, perhaps as another user, then this is a multi-connection challenge.

Challenge developers must identify their challenges as either single-connection or multi-connection as this will determine what Kubernetes resources are required.

## Example #1: Provisioning Kubernetes Resources for a Single-Connection Challenge

The Kubernetes resources below belong to a challenge called **Read Me a Fortune**. The player can solve the entire challenge over the course of a single SSH connection, therefore we classify it as a **Single-Connection Challenge**. 

We define two Kubernetes objects: a **Deployment** object and a **Service** object. 

We give the **Deployment** object a name and label it with the challenge category, the service name, and the challenge name, (since a challenge may have multiple deployments with different services). We specify the address of the Docker image belonging to the challenge in the **image** key. We set maximum CPU to 300m, maximum memory to 800Mi, and the number of replicas to 3. We expose the SSH port in the pod as this is how the player will connect. Finally, we set imagePullPolicy to always to ensure that the latest image is pulled with every update using the **kubectl** utility.

Alone, a deployment cannot expose a challenge to the outside world. To do this, we need a **Service** or **Ingress** object. In this case, we use a **Service** of type **NodePort** to expose this challenge on port 30907 on all Kubernetes cluster nodes. More specifically, we map the node port, 30907, to port 22 in the challenge pod, the SSH port we exposed in the deployment. 

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: readmeafortune
  labels:
    category: sysadmin
    challenge: readmeafortune
    service: debian
spec:
  replicas: 3 
  selector:
    matchLabels:
      category: sysadmin
      challenge: readmeafortune
      service: debian
  template:
    metadata:
      labels:
        category: sysadmin
        challenge: readmeafortune
        service: debian
    spec:
      containers:
      - name: readmeafortune-debian-sysadmin
        image: gcr.io/ctf-demo-project/0x00readmeafortune-debian-sysadmin:1.0
        imagePullPolicy: Always
        resources: 
          limits:
            cpu: 300m
            memory: 800Mi
          requests:
            cpu: 20m
            memory: 30Mi
        ports:
        - containerPort: 22
          name: ssh-port
       
---


apiVersion: v1
kind: Service
metadata: 
  name: readmeafortune-debian-sysadmin
  labels:
    category: sysadmin 
    challenge: readmeafortune
    service: debian
spec:
  type: NodePort
  selector:
    category: sysadmin 
    challenge: readmeafortune
    service: debian
  ports:
    - port: 22 # The port exposed by the service
      name: ssh-port
      targetPort: 22 # The port exposed by the pod
      nodePort: 30907 # The port that is exposed on each Node on the cluster     
```

Since the GKE cluster is a private cluster, this challenge is not yet live on the internet. To allow connections from the internet to this challenge, we create a `frontend` block in the HAProxy configuration file. This frontend block proxies all incoming connections to HAProxy on port 30907 to port 30907 on the internal cluster nodes. HAProxy load balances incoming connections between cluster nodes so that no one cluster node is overwhelmed.

```
frontend readmeafortune-sysadmin 
        tcp-request connection reject if { src_conn_rate(Abuse) ge 50 }
        tcp-request connection reject if { src_conn_cur(Abuse) ge 50 }
        tcp-request connection track-sc1 src table Abuse
        bind *:30907   
```


## Example #2: Provisioning Kubernetes Resources for a Multi-Connection Challenge

The Kubernetes resouces below belong to a Programming challenge called **Base64**. The challenge maintains session information through cookies and require more than a single HTTP request to solve where current requests are dependent on previous requests, therefore we classify it as a **Multi-Connection Challenge**.

```
```


## General Organization

At the root of this git repository, a directory is created for each **Challenge Category**. Each category folder contains a set of challenge folders representing individual challenges. 

For example, you might create a **Category folder** called “01-WEB”. Inside “01-WEB”, you can have a number of **challenge directories** such as “0x00-SQLInjection1” and “0x01-TreeTraversal”. 

Each challenge directory can have up to **three subdirectories**, each of which contains a number of files. 
- **player_files (Optional)**: contains any files the challenge developer wishes to share with the players.
	- Anything like a JSON dump, a binary, etc. 
- **documentation (Required)**: contains the challenge's documentation files including:
	- **manifest.yml (Required)**: contains challenge metadata including challenge name, author, category, point value, flags, dependencies, tags, as well as deployment information such as the GCP project, container registry address, and destination kubernetes namespace.
	- **instructions.txt (Required)**: contains the challege's instructions or in other words, what students see on CTFd when they click a particular challenge.
	- **hint.txt (Optional)**: contains a hint that can aid the player in solving the challenge. The hint can be free or may have a cost associated with it. The cost is deducted from the team's total points. The hint_cost is not specified in hint.txt, only the hint itself. The hint_cost is specified using the "hint_cost" key in manifest.yml
	- **solution.txt (Required)**: contains a detailed walkthrough of the challenge solution for mentors and/or students. Should contain the flags BUT CTFd will verify flag submissions based on what is in the “flags” keys in manifest.yml.
- **docker_images (Required)**: contains 1 directory per docker image associated with the challenge. For example, if a web challenge requires two services, a PHP application and a PostgreSQL database, the docker_images folder would contain a "php" directory and a "postgresql" directory. Each of these would contain a Dockerfile that pulls a PHP image and a PostreSQL image, respectively.
- **resources.yml**: contains the Kubernetes objects associated with the challenge such as Deployment, Service, and Ingress objects.

Here is an example CTF with three categories and three hosted challenges, one in each category:

![Repository Structure](https://github.com/abboudl/ISSessionsCTF2022-File-Based-Challenges/blob/main/readme-images/repo-structure.png)

## Deployment Order

Note the number at the beginning of each category and challenge folder. This number is used to force deployment scripts to deploy challenges in a specific order. 

This is important because CTFd requires a challenge to be present before another challenge marks it as a dependency. For example, SQLInjection2 cannot refer to SQLInjection1 as dependency until SQLInjection1 is has been deployed to CTFd.   

## Challenge Documentation

### The `manifest.yml` File

The manifest.yml file has two parent keys: a **challenge** key and a **k8s** key.

The **challenge** key is used to set challenge metadata. Its has subkeys such as **type** which determines if a challenge's point value is static or dynamic based on the number of solves. Another subkey **tags** can be used to assign keywords to a challenge that indicate the challenge’s difficulty level, a particular theme, or perhaps a useful tool that may aid in solving the challenge.

The **k8s** key is used to set deployment information. It has subkeys such as **gcp_project_id** which indicates the CTF's GCP project and **port** players will use to the challenge if it is exposed via a NodePort service.    

Here is an example of a manifest.yml file for a cryptography challenge exposed via a NodePort service on port 30000. 

**Example Cryptography Challenge: Exposed via a NodePort service**
```
#####################################
# CTFd PARAMETERS
#####################################
challenge:
  # challenge name as it should appear to the players - required - 20 characters max
  name: "0x00: All Your Bases"

  # challenge author - required
  author: Brandon West

  # challenge category as it should appear to the players - required - 20 characters max
  category: CRYPTOGRAPHY

  # standard or dynamic
  type: dynamic

  # initial challenge value
  value: 100

  # This is the lowest that the challenge can be worth
  minimum: 50

  # The amount of solves before the challenge reaches its minimum value
  decay: 30

  # hint_cost if a hint is provided for the challenge - if not remove key
  hint_cost: 0

  # All viable solutions to a challenge (i.e. what the student enters in 
  # CTFd) - in depth explanations of the solution should be placed in 
  # documentation/solution.txt. Flags are case-sensitive but can be 
  # made case-insensitive through the CTFd GUI.
  flags:
    - FLAG{545f274804}

  # helpful tags to focus the player's attention
  tags:
    - difficult

  # hidden or visible - better to keep hidden by default
  state: hidden

  # don't change
  version: 1.0

  # dependencies on other challenges - dependencies must be deployed before current challenge.
  # requirements:                       
  #  - '0x00: CoC'

  # Number of attempts - 0 attempts = infinite attempts
  attempts: 0
  
#############################################
# HOSTED CHALLENGE PARAMETERS
#############################################
k8s:
  # Google Cloud Platform CTF project identifier
  gcp_project_id: ctf-demo-project

  # Google Cloud Platform Virtual Private Network (VPC)
  gcp_vpc: issessions-ctf-vpc

  # Google Container Registry address
  gcr_address: gcr.io

  # Kubernetes namespace for hosted challenges
  gke_namespace: hosted-challenges

  # If the challenge is exposed on Kubernetes using a NodePort service, provide a
  # unique port between 30000 and 32500. Port must be unique across all challenges. 
  # Otherwise, if challenge is web-based and is to be exposed on Kubernetes using
  # a name-based virtual hosting scheme on ingress-nginx, fill in a challenge port 
  # of 0. 
  port: 30000

  # List all docker images with your challenge (must match directory names in 
  # docker_images directory). Each list item represents one of the docker 
  # images to build for our challenge.
  # 20 character per service (max)          
  services:
  - pythontcpserver
```

### The `instructions.txt` File
Use the following guidelines when creating the instructions.txt file. Make sure to include the following items.
- How does the player connect to the challenge (url, ip, port, etc.)? Or do they download a zip file?
- What do you want the player to do?
- Are there any steps to convert the challenge solution to a standardized flag format?

### The `hint.txt` File
Provide a helpful hint here. Hints can be free or paid. If paid, the hint is deducted from the team’s score. The **hint_cost** key in manifest.yml specifies the cost of the hint.

### The `solution.txt` File
Provide an in-depth explanation of the challenge! Mentors will refer to this solution when helping students during the CTF.

A in-depth explanation should include:
- Recommended tools and resources.
- Setup steps that the players need to go through.
- A detailed step by step solution including rationale, explanations, and specific commands.
- All possible challenge flags.
- Steps to convert the challenge solution to a standard flag format.

Remember, ISSessionsCTF is an ultra-beginner CTF. Getting this file right is the difference between a good and a bad CTF.

## Development Process

### Setup
1. **Create a dedicated challenge development VM.** You will have to install some tools and it’s better not to install them on your personal machine. A **Ubuntu Linux VM** is strongly recommended.
2. Clone `https://github.com/csivitu/ctfcli/`, change directories into the repository’s root, and run the setup.py script to install `ctfcli`. ctfcli allows for the automated deployment of CTF challenges to CTFd from the commandline and is key to automated deployment.

Command:
```
git clone https://github.com/csivitu/ctfcli/ && cd ctfcli && sudo python3 setup.py install --record files.txt
```

3. Add an SSH key to your github account. Here’s a guide: https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account 
4. Get a CTFd access token.
	1. Create an admin account on CTFd.
	2. Click **Settings**
	3. Click **Access Tokens**
	4. Click **Generate** and note down the resulting access token. 
5. On your VM, run the following command. You will get two prompts, one for **CTFd’s URL** and another for your **personal admin access token to CTFd**. Enter these and press Enter. This will create a **.ctf/config** file in the repository.
```
ctf init
```

![ctf init](https://github.com/abboudl/ISSessionsCTF2022-File-Based-Challenges/blob/main/readme-images/ctf-init.png)

6. Next, clone this repository.
```
git clone <repo url>
```
7. Create your own branch. You can name it after yourself for example.
```
git branch louai
git checkout louai
```

From now on, use this branch for all challenge development activities. It will be merged into main at a later date.

**Important Note:** 
We are using **a fork of the original ctfd/ctfcli** because the original does not yet support dynamic challenges. In the future, this may:
1. Become unnecessary as the original CTFd ctfcli (https://github.com/CTFd/ctfcli ) implements support for dynamic challenges. This would be great!
2. The fork may break because CTFd has implemented a change at odds with the forked implementation. In this case, you may have to modify ctfcli yourself to support dynamic challenges. (Don’t worry it’s not that complicated of a tool).
