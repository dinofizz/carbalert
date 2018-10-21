# CarbAlert

CarbAlert is a web application which scrapes a local (South African) second-hand computer parts forum for new posts offering laptops featuring keywords of interest. I'm using Django for the admin console and database/ORM integration, Scrapy for web-scraping, Celery for task management and Mailgun for sending out alert emails. The application is hosted on a VPS and is deployed using Docker.

![Django admin console showing results](images/dell_results.png "Django admin console showing results")

![Email results](images/emails.png "Email results")

## Pre-requisites

For both local and production deployments you will need to register and obtain the relevant keys for access to the Mailgun API.

GitHub OAuth registration is required for production deployments where the Flower front-end is accessible over the internet.

There are Python pre-requisites for running CarbAlert on your local machine for development and testing, and there are the Docker and Nginx pre-requisites for deploying and running CarbAlert on a server. These will be explained in detail in the sections below.

### Mailgun registration

The email alerts are sent using the [Mailgun](https://www.mailgun.com) API. Mailgun will allow you to send up to 10000 emails a month before charging you - fine for development and testing.

To get started with Mailgun take a look at their docs. [Quick-start guide here](https://documentation.mailgun.com/en/latest/quickstart-sending.html#how-to-start-sending-email).

Once you have registered and set up your Mailgun "domain" you should be able to see and save the following values:

- Mailgun domain. I'm using "mg.dinofizzotti.com"
- Mailgun API key. I'm using "key-88bf..." :P

Keep these values on-hand, you will need them later during deployment (local and production).

### Flower / GitHub OAuth registration

**You can skip this if you will only be working with CarbAlert on your local machine and not deploying to "production" for public access.**

CarbAlert uses [Flower](https://flower.readthedocs.io) as a front-end for inspectin the Celery tasks. I went with GitHub OAuth as an authentication mechanism (I don't want just anybody inspecting my Celery tasks). To get set up with GitHub OAuth start reading [here](https://flower.readthedocs.io/en/latest/auth.html#github-oauth).

Once you have completed the necessary steps to register an app you should note down the following values:

- OAuth2 key
- OAuth2 secret
- OAuth2 redirect URI

You will need these values later.

## Local Development

### Make sure you have Python 3.6

*I have only tested this on Linux (Arch/Ubuntu)*

CarbAlert has been tested running on Python 3.6. It is recommended to create a [virtual environment](https://docs.python.org/3/tutorial/venv.html) in which the dependencies should be installed and from which the project should be launched. So technically the only requirement is Python 3.6.

To see if you are running Python 3.6 issue the following command in the terminal:

``` Bash
$ python --version
Python 3.6.6
```

**Depending on which distribution of Linux you use you can also try see if you Python 3.x by substituting "python3" in the command above for "python".**

### Install the required dependencies

**This is only necessary for local development.**

To create a virtual environment and install the required dependencies issue the following commands in the terminal:

``` Bash
# Clone the repository
$ git clone <carbalert github url>

# Change directory to the newly cloned repository
$ cd carbalert

# Create a virtual environment in the repository directory
$ python -m venv carbalert-venv

# Activate the virtual environment
$ source carbalert-venv/bin/activate

# Make sure you have the latest version of pip installed in your virtual environment
(carbalert-venv) $ pip install --upgrade pip

# Install the required dependencies
(carbalert-venv) $ pip install -r requirements.txt
```

### Running CarbAlert on your local machine

Once all the dependencies have been installed you will need to issue the following commands to run the various CarbAlert components.

**For each of the commands below make sure that you are running them after having activated the virtual environment as described above** You may need to open a few terminal tabs/windows to get everything running at the same time.

#### Django 

To run the Django app we go through the typical Django `manage.py` commands, but use an additional parameter to point to a Django settings file that contains configuration for local development. Run the commands from the top level repository directory. 

``` Bash
# Prepare the database migrations
(carbalert-venv) $ python carbalert/manage.py makemigrations --settings=carbalert.settings.development

# Make the database migrations
(carbalert-venv) $ python carbalert/manage.py migrate --settings=carbalert.settings.development

# Run the Django application on the development web server
(carbalert-venv) $ python carbalert/manage.py runserver --settings=carbalert.settings.development
```

#### Celery Worker

To run the celery worker you will need to store some of the values from the Mailgun registration into environment variables:

``` Bash
# Set the email address which Mailgun will use as a "from" address in the emails it will be sending.
(carbelert-venv) $ MAILGUN_EMAIL=you@yourdomain.com

# Set the Mailgun API key
(carbelert-venv) $ MAILGUN_API_KEY=<your key here>

# Set your Mailgun domain
(carbelert-venv) $ MAILGUN_DOMAIN=mg.yourdomain.com

```

In the same shell session you can then launch the Celery worker process with the following command *issued from the parent repo directory*:

``` Bash
(carbelrt-venv) $ celery -A carbalert.carbalert_scrapy.carbalert_scrapy.tasks worker --loglevel=info -f celery_worker.log --max-tasks-per-child 1 --email "${MAILGUN_EMAIL}" --key ${MAILGUN_API_KEY} --domain ${MAILGUN_DOMAIN}
```

#### Celery Beat

To run the Celery Beat process which will manage the periodic Celery tasks you will need to issue the following command *from the parent repo directory*:

``` Bash
(carbalert-venv) $ celery -A carbalert.carbalert_scrapy.carbalert_scrapy.tasks beat --loglevel=info -f celery_beat.log

```

#### Flower

To run the Flower process you will need to issue the following command *from the parent repo directory*:

``` Bash
(carbalert-venv) $ celery -A carbalert.carbalert_scrapy.carbalert_scrapy.tasks flower --loglevel=debug --auth_provider=flower.views.auth.GithubLoginHandler --auth=${FLOWER_OAUTH2_EMAIL} --oauth2_key=${FLOWER_OAUTH2_KEY} --oauth2_secret=${FLOWER_OAUTH2_SECRET} --oauth2_redirect_uri=${FLOWER_OAUTH2_REDIRECT_URI} --url_prefix=flower
```
