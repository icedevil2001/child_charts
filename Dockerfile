FROM python:3.7
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app
CMD [ "executable" ]
# Copy the current directory contents into the container at /app
ADD . /app
