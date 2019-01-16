# django-chkp

Demo web interface created to demostrate the integration for Check Point R80 API and a web interface
the idea is shown to the customers how Checkpoint API Works.

This Web interface was created using Django a python framework for Web development

https://www.djangoproject.com/

And a basic Json Class to communicate between the web server and the Smart Center Server

What can I do

This Web interface can create:

1.- Layers and rules
2.- Create host objects with Nat Hide, Static Nat
3.- Create Networks objects with Nat Hide, Static Nat.

The app is divide in several files following the django development model

Vies.py - The backend and the way how the web server analyze the get and post requests, we call the Check Point API from this side.
Tasks.py - The R80 API is represented in this file.

# How to Start

This app is designet to run using docker, the first step to deploy it is using Docker.

1.- Install Docker following the instructions for your Linux Distro
2.- Download this repository using GIT.

git clone https://github.com/cadgo/django-chkp.git

3.- Use the Dockerfile inside the created folder 

sudo docker build -t chkpdjango .

This will generate a Docker image 

sudo docker image ls -a

REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
chkpdjango          latest              198d302b7fdc        5 minutes ago       994MB
python              3                   7c5fd2af3815        6 days ago          927MB

We can run the container in this way
sudo docker run -it --network=host chkpdjango /bin/bash

to Run the server we need to execute

#python3 manage.py runserver 0.0.0.0:8000

First steps using the web interface.

1.- Create an API user in our Smart Center Server
2.- Enable the API for all IPs

We need to add the smart center server inside our database using this URL http://IPADDRESS:8000/admin/
  
  By default the dockerfile create an user admin/zubur1

1.- Create a user for our web interface

![screenshot](https://github.com/cadgo/django-chkp/blob/assets/users1.PNG)

2 .- Add a User filling the form

3.- Add a Mgmt Server

![screenshot](https://github.com/cadgo/django-chkp/blob/assets/MgmtServerAdd.PNG)

We need to add the form

MgmtR80Name: A name for our MGMT Server in our web interface
ServerIP: IP address
Description: a brief description 
MgmtR80VersionsSupported: leave as default, there are future plans
MGMTR80IsAlive: leave as default
MgmtFingerPrintAPI: leave as default
MgmtPort: Port used by the API 
LastPublishSession: Leave as default this a version control for the database between the SMS and the DB

4.- Create a Mgmt server Objectss

![Screenshot](https://github.com/cadgo/django-chkp/blob/assets/MgmtServerObjects.PNG)

Add a Mgmt Server Objects

MGMTServerObjectsID: Select the Mgmt Server added

And just save by default, this is going to create a path to save the DB in a txt files inside our docker

5 .- Create a Mgmt Server User, this is the previous user created inside the Smart Center Server

![Screenshot](https://github.com/cadgo/django-chkp/blob/assets/MgmtServerUsers.PNG)

UsersID: Select the previous added Mgmt Server
R80User: the username for example api_user
R80password: The username password

Stop the web server inside our docker  just pressing cntr+c inside here

![Screeshot](https://github.com/cadgo/django-chkp/blob/assets/stopWebServer.PNG)

And run it again!

We are ready to use our web interface, we can follow the next link http://IPADDRESS:8000/r80api/extends
  
The new Server appears in the extends pages if the servers redirect to the login page, just login with the user created in step number 1.

The ansible section maybe comes later

![screenshot](https://github.com/cadgo/django-chkp/blob/assets/extendsRules.PNG)



