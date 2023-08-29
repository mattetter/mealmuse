# MealMuse quickstart


## Setup

1. Clone this repository.


2. Navigate into the project directory and create a new virtual environment:

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

3. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

4. Create a environment variables file:

   ```bash
   $ touch .env
   ```

5. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file in the following format:
   OPENAI_API_KEY= [API key]


6. Set up databases:

   ```bash
   $    sudo -u postgres psql
   postgres=# CREATE DATABASE development_database;
   postgres=# CREATE USER matt WITH ENCRYPTED PASSWORD 'echo';
   postgres=# GRANT ALL PRIVILEGES ON DATABASE mydatabase TO matt;
   postgres=# \q
   ```

7. start the redis server:

   ```bash
   $ sudo service redis-server start
   ```


8. Open another terminal, navigate to the root directory again and run celery:

   ```bash
   $ celery -A mealmuse.celery worker --loglevel=info
   ```


9. Run the app:

   ```bash
   $ flask run
   ```