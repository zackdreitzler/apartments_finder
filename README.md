# Apartments Finder
This is an application for web scrapping apartments.com for housing information.

# Additional Requirements
 * Docker

# Setup
* Clone this repo to your machine.
* Be in the main directory with the Dockerfile.
* Run command `docker build -t apartments_finder .` to build the docker image. 

# Usage
* Run command `docker container run --name apartments_finder -p 5000:80 apartments_finder` to build the docker container and run it.
* Navigate to to the address of the server. Typically `http://172.17.0.2:5000/`.
