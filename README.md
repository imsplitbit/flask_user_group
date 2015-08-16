# Flask User / Group App

This is just a simple flask app to keep track of users.

There is a many to many relationship between Users and
Groups.  This helps look at the way flask/SQLAlchemy can
maintain those relationships.

## Installation

There are 2 ways you can run this app, the simplest being
directly from the commandline on a *nix box.

## Simple Shell Method
### Requirements
You will need python and the development sources for python to build
some of the dependencies for this project.  On debian variants this 
can be done by simply installing the `python-dev` package.

    sudo apt-get install python-dev
    

### Steps
1. Download this repository
    
    git clone git@github.com:imsplitbit/flask_user_group.git
    
2. Change to the repository's directory.
    
    cd flask_user_group
    
3. Install the python modules necessary for the app to function.
    
    sudo pip install -r requirements-test.txt
    
4. Run the unittests to prove out the functionality.
    
    nosetests .
    
5.  You should at this point have a service you can run locally, just start the service with the commnad:
    
    ./app.py
    
6.  Using curl or other HTTP clients you can then use the API to test functionality.

## Docker Method
### Requirements
The only requirement here is that you've installed docker on your local machine.  
This can be done by following the links here:

Mac OSX: https://docs.docker.com/installation/mac/
Ubuntu: https://docs.docker.com/installation/ubuntulinux/

There are other links if you prefer a different distribution of linux but the basic gist of the install is the same.

### Steps
1. Download this repository
    
    git clone git@github.com:imsplitbit/flask_user_group.git
    
2. Change to the repository's directory.
    
    cd flask_user_group
    
3. Build the docker image
    
    sudo docker build -t demo_app .
    
4. When the image has completed building you can run the unittests with:
    
    sudo docker run --rm -t demo_app nosetests .
    
5. To run the app as a daemon using docker you can use the following (substitute whatever local port you want to test on for the `80` in the command below:
    
    sudo docker run -d --name demo_app -p 80:5000 demo_app
    
6.  You can now use curl or other HTTP clients to test the API's functionality.  Pay careful attention to the local port number you chose in the previous step.
