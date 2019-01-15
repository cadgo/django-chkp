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
