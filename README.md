# IFS4205 Team 1

## Notes

+ After installing dependecies, use `pip3 freeze > requirements.txt` to update the file so others can download the new dependencies.

## Directory Structure

```
ifs4205team1
├── adminlogin
│   ├── anonymise.py
│   ├── anonymise_helper.py
│   ├── forms.py
│   ├── static
│   │   └── astyle.css
│   ├── templates
│   ├── urls.py
│   ├── views.py
├── adminusers
│   ├── templates
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
├── core
│   ├── fixtures
│   │   ├── initial_core.json
│   │   ├── initial_users.json
│   │   └── test_users.json
│   ├── management
│   │   ├── commands
│   │   │   ├── clear_users.py
│   │   │   ├── initusers.py
│   │   │   ├── load_csv.py
│   │   │   ├── load_users_csv.py
│   │   └── files
│   │       ├── images.csv
│   │       ├── test_users.csv
│   │       ├── test_users_less.csv
│   │       ├── time_series.csv
│   │       └── videos.csv
│   ├── models.py
├── healthcarelogin
│   ├── templates
│   │   ├── healthcare_change_password_complete.html
│   │   ├── healthcare_change_password.html
│   │   ├── healthcare_dashboard.html
│   │   ├── healthcare_edit_settings.html
│   │   ├── healthcare_login.html
│   │   ├── healthcare_qr.html
│   │   ├── healthcare_settings.html
│   │   └── healthcare_token_register.html
│   ├── urls.py
│   └── views.py
├── healthcarenotes
│   ├── forms.py
│   ├── templates
│   │   ├── create_healthcare_note_for_patient.html
│   │   ├── create_healthcare_note.html
│   │   ├── edit_healthcare_note.html
│   │   ├── edit_healthcare_note_permission.html
│   │   ├── show_all_healthcare_notes.html
│   │   └── show_healthcare_note.html
│   ├── urls.py
│   └── views.py
├── healthcarepatients
│   ├── forms.py
│   ├── templates
│   │   ├── new_patient_images_record.html
│   │   ├── new_patient_readings_record.html
│   │   ├── new_patient_record.html
│   │   ├── new_patient_timeseries_record.html
│   │   ├── new_patient_videos_record.html
│   │   ├── show_all_patients.html
│   │   ├── show_patient.html
│   │   ├── show_patient_record.html
│   │   ├── show_patient_records.html
│   │   └── transfer_patient.html
│   ├── urls.py
│   └── views.py
├── ifs4205team1
│   ├── config
│   │   └── settings
│   │       ├── base.py
│   │       ├── development.py
│   │       ├── production.py
│   │       └── testing.py
│   ├── templates
│   │   └── protected_record.html
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── manage.py
├── media
│   ├── images
│   ├── timeseries
│   └── videos
├── mobileregister
│   ├── forms.py
│   ├── templates
│   │   ├── repeat_register.html
│   │   ├── success_register.html
│   │   ├── user_login.html
│   │   └── user_register.html
│   ├── urls.py
│   └── views.py
├── patienthealthcare
│   ├── fixtures
│   │   └── initial_notes.json
│   ├── management
│   │   └── commands
│   │       └── initnotes.py
│   ├── templates
│   │   ├── show_all_notes.html
│   │   └── show_note.html
│   ├── urls.py
│   └── views.py
├── patientlogin
│   ├── forms.py
│   ├── templates
│   │   ├── patient_change_password_complete.html
│   │   ├── patient_change_password.html
│   │   ├── patient_dashboard.html
│   │   ├── patient_edit_settings.html
│   │   ├── patient_login.html
│   │   ├── patient_qr.html
│   │   ├── patient_settings.html
│   │   └── patient_token_register.html
│   ├── urls.py
│   └── views.py
├── patientrecords
│   ├── fixtures
│   │   ├── initial_data_readings.json
│   │   ├── initial_data_readingsperm.tar.xz
│   │   └── initial_records.json
│   ├── forms.py
│   ├── management
│   │   ├── commands
│   │   │   ├── clear_records.py
│   │   │   ├── generate_records.py
│   │   │   ├── initrecords.py
│   │   └── files
│   │       ├── diagnosis_random.csv
│   │       ├── diagnosis_random_less.csv
│   │       ├── readings.csv
│   │       └── readings_less.csv
│   ├── models.py
│   ├── templates
│   │   ├── edit_permission.html
│   │   ├── new_documents_record.html
│   │   ├── new_images_record.html
│   │   ├── new_readings_record.html
│   │   ├── new_record.html
│   │   ├── new_timeseries_record.html
│   │   ├── new_videos_record.html
│   │   ├── show_all_records.html
│   │   └── show_record.html
│   ├── templatetags
│   │   ├── app_filters.py
│   ├── tests
│   │   └── test_views.py
│   ├── urls.py
│   └── views.py
├── requirements.txt
├── researcherlogin
│   ├── forms.py
│   ├── templates
│   │   ├── researcher_change_password_complete.html
│   │   ├── researcher_change_password.html
│   │   ├── researcher_dashboard.html
│   │   ├── researcher_edit_settings.html
│   │   ├── researcher_login.html
│   │   ├── researcher_qr.html
│   │   ├── researcher_settings.html
│   │   └── researcher_token_register.html
│   ├── urls.py
│   └── views.py
├── researcherquery
│   ├── fixtures
│   │   └── initial_saferecords.json
│   ├── forms.py
│   ├── management
│   │   └── commands
│   │       ├── init_saferecords.py
│   ├── models.py
│   ├── router.py
│   ├── static
│   │   └── researcherstyle.css
│   ├── templates
│   │   └── search_records.html
│   ├── templatetags
│   │   ├── app_filters.py
│   ├── urls.py
│   └── views.py
├── templates
│   ├── admin_base.html
│   ├── base.html
│   ├── healthcare_base.html
│   ├── home.html
│   ├── patient_base.html
│   └── researcher_base.html
└── userlogs
    ├── models.py
    ├── router.py

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