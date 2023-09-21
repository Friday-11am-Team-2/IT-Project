# AuthorGuard - IT Project

### Project Overview
This project is a web-based interface to allow non-technical users to use stylographic technologies to detect plagiarism in academic writing. This usable interface, branded with the name “AuthorGuard” is a full-stack web application that leverages powerful modern day machine learning techniques to detect with a high level of accuracy the likelihood that a given piece of writing was written by a particular individual. 

The development team aims to deliver a functional, efficient and easy to use web-application to allow for the usage of these machine learning algorithms by a non-technical academic audience to help protect authorial integrity in an era of Large Language Models & Contract Cheating.

#### Why is this needed?
Universities and other institutions have always had the need to check for the orginality of works of students and researchers. There are tools like Turnitin that checks for plagerism in work done by students or researchers. However, with the rise of AI technologies such as ChatGPT which is able to generate essays and other work, tools that checks for plagerism are unable to provide authorship verification. 
               
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

<br>

### Technical Details
#### Tech-Stack
- Front-End: *Javascript/HTML/CSS*
- Back-End: *Django (Python)*
- Database: *PostegreSQL*
- Deployment: *Docker + AWS*

#### Deployment
The app uses Docker to easily create a highly flexible and easy to deploy web server, follow these simple steps to deploy this appication.
1. Ensure ```settings.py``` is connected to your external database of choice.
2. Build the docker for the web application.
3. Deploy to any hosting service that supports docker containers. (AWS, Heroku, etc.)

<br>

### Repository Directories
#### ```/.github```
This directory contains github workflows for the project, including automated testing and the CI/CD pipeline for building and deployment. The automated testing workflow occurs whenever a pull request is made to either the ```main``` or ```development``` branches, which ensures that untested code will never reach production.

#### ```/PAN14_Code_Model_Code```
Contains the original project source code with some modifications
and a WIP library for interfacing the model with our site

#### ```/confluence```

#### ```/stylometryproject```

<br>

