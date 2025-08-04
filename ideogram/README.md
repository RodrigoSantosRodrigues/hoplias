<h1 align="center">Hoplias</h1>


![Diagram](specs/NamekoDiagram.png)

## Installation
  - Install [Python](https://www.python.org/downloads/), [Pipenv](https://docs.pipenv.org/) 
  - Install RabbitMQ 
  ```docker run -d --hostname my-rabbit --name rabbit13 -p 8080:15672 -p 5672:5672 -p 25676:25676 rabbitmq:3-management```
  - Install Postgres

  - Activate the project virtual environment with `$ pipenv shell`
  - `pip install -r requirements.txt` to install dependencies
 


## Start nameko services
- Start the app with 
nameko run --config config.yml src.service



## Compatibility
* [Tested on Python >= 3.7]

Notes
=================
