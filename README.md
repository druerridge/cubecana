This codebase now includes the code for the website [www.cubecana.com](https://www.cubecana.com/). I recommend you start there, and come back if you feel you need more. There is also a CLI provided which offers some of the same functionality and in some cases a bit more.

# Env / Dependencies

It is meant to run on python3 and requires a few packages: Flask, PyMySQL, SQLAlchemy at least. 

Here's my full local if it helps. I'll make a pyenv at some point... or you could, that'd be a great contribution ;) 
```
PS C:\workspace\python\dreamborn_to_draftmancer> pip3 list

Package            Version
------------------ --------
blinker            1.8.2
certifi            2024.7.4
charset-normalizer 3.3.2
click              8.1.7
colorama           0.4.6
Flask              3.0.3
greenlet           3.1.1
idna               3.8
itsdangerous       2.2.0
Jinja2             3.1.4
MarkupSafe         2.1.5
mysqlclient        2.2.6
pip                25.0.1
PyMySQL            1.1.1
requests           2.32.3
SQLAlchemy         2.0.36
typing_extensions  4.12.2
urllib3            2.2.2
Werkzeug           3.0.4
```

# Database
You'll need a local mysql. You should be able to run the database_migrations/ folder in numerical order to get the schema set up correctly.

# Running
I just run

> python3 ./run.py
