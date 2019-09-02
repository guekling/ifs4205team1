# IFS4205 Team 1

## Notes

+ After installing dependecies, use `pip3 freeze > requirements.txt` to update the file so others can download the new dependencies.

## 1. Running Django

### 1.1 Running Django for the First Time

#### 1.1.1 Installing Virtual Environment

1. Install the virtual environment, and `virtualenvwrapper` to manage the virtual environments

   ```
   ~$ pip3 install virtualenv
   ~$ pip3 install virtualenvwrapper
   ```

2. Create a file to store all virtual environments in the same place

   `~$ mkdir ~/.virtualenvs`

3. Add the following at the end of the `.bashrc` file:

   ```
   VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3
   export VIRTUALENVWRAPPER_PYTHON
   export WORKON_HOME=$HOME/.virtualenvs
   source /usr/local/bin/virtualenvwrapper.sh
   ```

   If paths above are incorrect, use `which python3` and `which virtualenvwrapper.sh` to find the correct paths.

4. Reload `.bashrc` file

   `~$ source ~/.bashrc`

5. Navigate to the Django project, and create a new virtual environment

   `~$ mkvirtualenv --python=/usr/local/bin/python3 ifsteam4205env`

6. Install dependencies

   `~$ pip3 install -r requirements.txt`

#### 1.1.2 Setting Up the Database

The database used is PostgreSQL v10.10.

1. Create a `.env` file in the same folder as the `settings.py` file.

2. Add the following into the `.env` file:

   ```
   export DB_NAME = 'YOUR_DB_NAME'
   export DB_USER = 'YOUR_DB_USER'
   export DB_PASS = 'YOUR_DB_PASS'
   ```

3. Make migrations

   ```
   ~$ python manage.py makemigrations
   ~$ python manage.py migrate
   ```

#### 1.1.3 Starting Django

1. Start Django

   `~$ python manage.py runserver`

### 1.2 Running Django for the Subsequent Times

1. Start the virtual environment before working on the project

   `~$ workon ifs4205team1`