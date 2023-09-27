# Dockerfile

# Python Version
FROM python:3.11

# Copy and Install Requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project to Docker
COPY . src
WORKDIR /src/stylometryproject

# Expose Port 8000
EXPOSE 8000

# Run Server
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000", "--noreload"]


# Commands
# docker build -t stylometryproject .
# docker run -p 8000:8000 stylometryproject