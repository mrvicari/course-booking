rm -rf db_repository app.db __pycache__
source flask/bin/activate
python db_create.py
python manage.py populateDb
python run.py
