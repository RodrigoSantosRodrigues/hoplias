# Api Service Hoplias
Service to serve data to the platform Hoplias




## Installation
  - Rename  env.example for .env
  1. [Install docker-compose](https://docs.docker.com/compose/install/#install-compose).

    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose

  2. docker-compose build --no-cache
  3. Run the server:
    docker-compose up




  ## To start locally without using docker

  Here’s the formatted version of your content in Markdown:

  ```markdown
  ## To Start Locally Without Using Docker

  Follow the steps below to set up the development environment:

  ### 1. Install MongoDB
  Make sure MongoDB is installed and running on your machine. You can install it by following the official instructions:
  - [Install on Ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
  - [Install on Windows](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)
  - [Install on macOS](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/)

  After installation, start the MongoDB service:
  ```bash
  sudo systemctl start mongod  # For Linux
  mongod                      # For macOS/Windows
  ```

  ### 2. Install Pipenv
  Pipenv is a tool for managing dependencies and virtual environments. Install it using pip:
  ```bash
  pip install pipenv
  ```

  ### 3. Activate the Virtual Environment
  Navigate to the project directory and activate the virtual environment with Pipenv:
  ```bash
  pipenv shell
  ```

  ### 4. Configure Environment Variables
  Rename the `.env.example` file to `.env` and fill in the environment variables with the appropriate values for your environment (e.g., database credentials, API keys, etc.).

  ### 5. Install Dependencies
  Install the project dependencies using the `requirements.txt` file:
  ```bash
  pipenv install -r requirements.txt
  ```
  ```

  - Start the app with `python run.py`

## Link DOC
  - http://localhost:5000/documentation or
  - http://localhost:5000/doc


## Compatibility
* [Developed on Python >= 3.7]


Notes
=================

URLs: https://fastapi.tiangolo.com/
      https://requests.readthedocs.io/en/master/user/advanced/#prepared-requests
      https://linuxhint.com/show-path-environment-variables/
     