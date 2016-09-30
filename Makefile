
virtualenv:
	[ -d .env ] || virtualenv .env 
	.env/bin/pip install -r requirements.txt
	echo "Now type \"source .env/bin/activate\" to active python env"


installpostgres:
	sudo apt-get install postgresql
	sudo -u postgres psql -c "CREATE USER tfm LOGIN ENCRYPTED PASSWORD 'password';"
	sudo -u postgres createdb tfm -O tfm

resetdb:
	sudo -u postgres dropdb tfm
	sudo -u postgres createdb tfm -O tfm
	make setupdb

setupdb:
	.env/bin/python manage.py migrate
	.env/bin/python manage.py createsuperuser

runserver:
	.env/bin/python runserver_plus
