# Dockerfile

# Use the python 3.11 install as the builder
FROM python:3.11-slim as builder

# Disable pip binary compiling and bytecode caching
# May cost performance, but it makes the image alot smaller
ENV PIP_NO_BINARY=:all
ENV PYTHON_DONT_WRITE_BYTECODE=1

# Create python venv
RUN pip install virtualenv
RUN virtualenv /venv
ENV PATH="/venv/bin:$PATH"

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache -r requirements.txt

# Pointless optimisation, but it saves a *tiny* bit of space
RUN pip cache purge
RUN pip uninstall pip setuptools -y

# Use a new, slim python 3.11 build as the base, to save space
FROM python:3.11-slim as base

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy project to it's new home
COPY stylometryproject /stylometryproject
WORKDIR /stylometryproject

# Expose Port 8000
EXPOSE 8000

# Run Server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

# Commands
# docker build -t stylometryproject:latest .
# docker run -p 8000:8000 --env-file [env file] stylometryproject:latest 

# docker login
# docker tag stylometryproject:latest itprojectauthorguard/it-project:latest
# docker push itprojectauthorguard/it-project:latest

