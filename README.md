# IFS4205 Team 1

## Notes

+ After installing dependecies, use `pip3 freeze > requirements.txt` to update the file so others can download the new dependencies.

## Directory Structure

```
ifs4205team1
├── core
│   ├── fixtures
│   │   └── initial_users.json
│   ├── management
│   │   ├── commands
│   │   │   ├── initusers.py
│   │   │   ├── load_csv.py
│   │   └── files
│   │       └── test_users.csv
│   └── models.py
├── healthcarelogin
│   ├── models.py
│   ├── templates
│   ├── urls.py
│   └── views.py
├── healthcarepatients
│   ├── models.py
│   ├── templates
│   ├── urls.py
│   └── views.py
├── ifs4205team1
│   ├── config
│   │   └── settings
│   │       ├── base.py
│   │       ├── development.py
│   │       ├── production.py
│   │       └── testing.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── manage.py
├── media
│   ├── documents
│   ├── images
│   ├── timeseries
│   └── videos
├── patienthealthcare
│   ├── fixtures
│   │   └── initial_notes.json
│   ├── management
│   │   └── commands
│   │       └── initnotes.py
│   ├── models.py
│   ├── templates
│   │   ├── show_all_notes.html
│   │   └── show_note.html
│   ├── urls.py
│   └── views.py
├── patientlogin
│   ├── forms.py
│   ├── models.py
│   ├── templates
│   ├── urls.py
│   └── views.py
├── patientrecords
│   ├── fixtures
│   │   └── initial_records.json
│   ├── forms.py
│   ├── management
│   │   └── commands
│   │       └── initrecords.py
│   ├── models.py
│   ├── templates
│   ├── templatetags
│   ├── tests
│   ├── urls.py
│   └── views.py
├── requirements.txt
└── templates
```

### 0.1 `core`

- `commands`
  - `initusers`: Loads `inital_users.json` fixture into database
  - `load_csv`: Loads a csv file (`test_user.csv`) into database
- `models.py`: `User` (extended from `django.contrib.auth.models.AbstractUser`, `Patient`, `Healthcare`, `Researcher`, `Admin`

### 0.2 Patient Interface

#### 0.2.1 `patientlogin`

- `views.py`: Patients' Login, Settings -related views

#### 0.2.2 `patientrecords`

- `commands`
  - `initrecords`: Loads `initial_records.json` fixture into database
- `models.py`: `Readings`, `TimeSeries`, `Documents`, `Images`, `Videos`, `ReadingsPerm`, `TimeSeriesPerm`, `DocumentsPerm`, `ImagesPerm`, `VideosPerm`, `Diagnosis`, `DiagnosisPerm`
- `views.py`: Patients' Medical Records, Medical Records' Permissions -related views

#### 0.2.3 `patienthealthcare`

- `views.py`: Patients' Healthcare Professional Notes -related views

### 0.3 Healthcare Professional Interface

#### 0.3.1 `healthcarelogin`

- `views.py`: Healthcare Professionals' Login, Settings -related views

#### 0.3.2 `healthcarepatients`

- `commands`
  - `initnotes`: Loads `initial_notes.json` fixture into database
- `views.py`: Healthcare Professionals' Patients -related views

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

1. Create a `.env` file in the `ifs4205team1/config/settings` folder.

2. Add the following into the `.env` file:

   ```
   export DB_NAME = 'YOUR_DB_NAME'
   export DB_USER = 'YOUR_DB_USER'
   export DB_PASS = 'YOUR_DB_PASS'
   export DB_HOST = 'localhost'
   ```

3. Make migrations

   ```
   ~$ python manage.py makemigrations
   ~$ python manage.py migrate
   ```

#### 1.1.3 Adding Sample Data into Database   

##### 1.1.3.1 Loading Sample Data from Fixtures

1. Run the following commands

   ```
   $ python manage.py initusers
   $ python manage.py initrecords
   $ python manage.py initnotes
   ```

##### 1.1.3.2 Loading Sample Data from CSV File

1. Run the following commands

  ```
  $ python manage.py load_csv --csvpath="<PATH/TO/CSV>/ifs4205team1/core/management/files/test_users.csv"
  ```
  
  Note: A `test_users_less.csv` with only a few rows of data exists in the same directory for testing purposes.

#### 1.1.4 Populating `.env` File

1. Add on the following into the `.env` file:

   ```
   export MEDIA_URL = 'MEDIA_URL'
   ```

#### 1.1.5 Starting Django

1. Start Django

   `~$ python manage.py runserver`

### 1.2 Running Django for the Subsequent Times

1. Start the virtual environment before working on the project

   `~$ workon ifs4205team1env`