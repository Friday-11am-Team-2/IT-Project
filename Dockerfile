# Dockerfile

# Python Version
FROM python:3.11

# Copy and Install Requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project to Docker
COPY stylometryproject /stylometryproject
WORKDIR /stylometryproject

# Expose Port 8000
EXPOSE 8000

# Run Server
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000", "--noreload"]


# Commands
# docker build -t stylometryproject:latest .
# docker run -p 8000:8000 --env-file [env file] stylometryproject:latest 

# docker login
# docker tag stylometryproject:latest itprojectauthorguard/it-project:latest
# docker push itprojectauthorguard/it-project:latest

