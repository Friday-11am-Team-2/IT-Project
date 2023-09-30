# AuthorGuard - IT Project

### Project Overview
This project is a web-based interface to allow non-technical users to use stylographic technologies to detect plagiarism in academic writing. This usable interface, branded with the name “AuthorGuard” is a full-stack web application that leverages powerful modern day machine learning techniques to detect with a high level of accuracy the likelihood that a given piece of writing was written by a particular individual. 

The development team aims to deliver a functional, efficient and easy to use web-application to allow for the usage of these machine learning algorithms by a non-technical academic audience to help protect authorial integrity in an era of Large Language Models & Contract Cheating.

#### Why is this needed?
Universities and other institutions have always had the need to check for the orginality of works of students and researchers. There are tools like Turnitin that checks for plagiarism in work done by students or researchers. However, with the rise of AI technologies such as ChatGPT which is able to generate essays and other work, tools that checks for plagiarism are unable to provide authorship verification. 
               
This is where Authorguard hopes to help. 
By detecting stylistic feature unique to each person, AuthorGuard is able to distinguish work 
written by the author in quesiton from work potentially written by AI or others.

#### Features
- Create profiles to store documents written by the same author.
- Simple document storage system through profile management.
- Leverage AI to compare to known and unknown documents.
- Quickly perform verification checking between documents.
- Recieve easy to interpret results from powerful machine learning algorithms.

#### Team Members
- Product Owner: Ayush Tyagi -  ayusht@student.unimelb.edu.au
- Scrum Master: Ke Liao - keliao@student.unimelb.edu.au
- Developer: Jack Perry - perryja@student.unimelb.edu.au
- Developer: Josh Costa - jncosta@student.unimelb.edu.au
- Developer: Bryce Copeland- bacopeland@student.unimelb.edu.au

#### Tech-Stack
- Front-End: *Javascript/HTML/CSS*
- Back-End: *Django (Python)*
- Database: *PostegreSQL*
- Deployment: *Docker + AWS*

<br>

### Repository Directories
#### ```/.github```
This directory contains github workflows for the project, including automated testing and the CI/CD pipeline for building and deployment. The automated testing workflow occurs whenever a pull request is made to either the ```main``` or ```development``` branches, which ensures that untested code will never reach production.

#### ```/PAN14_Code_Model_Code```
This directory contains adapted jupyter notebooks from the original machine learning algorithm provided to the team by the client near the inception of the project. It is also contains a depersonalised dataset for both training and testing the machine learning algorithm. The directory also contains the model weight files that was trained using Google Colab hardware, allowing the model to be easily loaded by the web application.

#### ```/confluence```
This directory contains the state of the confluence documentation as a single PDF for each of the sprints. This document is useful for the client in order to record the working process as well as the documentation pertaining to key topics such as requirements, design, UX/UI design, system architecture, test cases, code reviews, etc.

#### ```/stylometryproject```
This directory contains the web application itself. It is a Django web application and hence uses many of the default frameworks and code from Django applications. The following are the key subdirectories of this directory.

- ##### ```/model_storage```
This directory contains the model weights and model files for both the word2vec and main verification machine learning model. These files are loaded by the web app through the custom-made ```stylometry``` library and the ```StyloNet``` class within that library.

- ##### ```/stylometryapp```
This directory contains all files relating to the core functionality of the web application specifically, including django files such as ```models.py```, ```views.py``` and other critical functionality. It also contains template files for the HTML of the web page in ```/templates``` as well as static files, such as CSS stylesheets and JavaScript code for the front-end of the application in ```/static```.

- ##### ```/stylometryproject```
This direcotry contains more project related django files such as ```urls.py``` and ```settings.py```, which more involves how the web application runs in terms of architecture and settings as opposed to core functionality. The database settings need to be setup in this directory.

<br>

### Technical Information

#### Local Installation Guide
For those that wish to run the application locally, follow the following instructions:
1. Clone the repository (or download the .zip).
2. Open the root folder in your IDE of choice.
3. Setup [Python Virtual Environment](https://docs.python.org/3/library/venv.html).
4. Ensure [```pip```](https://pip.pypa.io/en/stable/installation/) is installed.
5. Run ```pip install -r requirements.txt``` to install the required libraries and modules.
6. Run ```cd stylometryproject``` to change to the Django app directory
7. Alter the ```DATABASES``` dictionary in ```/stylometryproject/settings.py``` to either a local db.sqlite3 or an external database of your ownership. [Django Database Documentation](https://docs.djangoproject.com/en/4.2/ref/databases/)
8. Run ```python manage.py runserver``` to run the web application on local host.

#### Deployment (Incomplete)
The app uses Docker to easily create a highly flexible and easy to deploy web server, follow these simple steps to deploy this appication.
1. Ensure ```settings.py``` is connected to your external database of choice.
2. Build the docker for the web application.
3. Deploy to any hosting service that supports docker containers. (AWS, Heroku, etc.)


#### Docker Usage
A docker image can be build with the command: `docker build -t stylometryproject .` from the repository root

The environment for the application can be configured via the file `stylometryproject/.env` or files under `secrets/`
Configurable ENV variables:
	DATABASE_TYPE = postgresql or sqlite (for testing purposes only)
	For postgresql: (all have generic default values)
		RDS_DB_NAME
		RDS_USERNAME
		RDS_PASSWORD
		RDS_HOSTNAME
		RDS_PORT
	
	Required by Django:
	SECRET_KEY (generate with `django.core.management.utils.get_random_secret_key()`)

There is also a docker `compose.yaml` file included.
It contains two services `authorguard` and `authorguard-sqlite`, the latter being for local testing purposes only.
Services can be run with `docker compose run [service name]` or `docker compose up` to run the default.

Environment variables can be configured via the `env_file` or `environment` attributes in the `compose.yaml`
By default it takes a file called `secrets.env` in the main folder.
NOTE: syntax for docker env files is slightly more restrictive than normal, make sure there are no spaces either side of the '=' and remove quotation marks from around the variables.