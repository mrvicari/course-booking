rm -rf db_repository app.db __pycache__
source venv/bin/activate
python db_create.py
python manage.py createAdmin
python run.py
