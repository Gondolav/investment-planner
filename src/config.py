import os
from urllib import parse

host_server = os.environ.get("host_server", "localhost")
db_server_port = parse.quote_plus(str(os.environ.get("db_server_port", "5432")))
database_name = os.environ.get("database_name", "postgres")
db_username = parse.quote_plus(str(os.environ.get("db_username", "postgres")))
db_password = parse.quote_plus(str(os.environ.get("db_password", "secret")))
ssl_mode = parse.quote_plus(str(os.environ.get("ssl_mode", "prefer")))

DATABASE_URL = "postgresql://{}:{}@{}:{}/{}?sslmode={}".format(
    db_username, db_password, host_server, db_server_port, database_name, ssl_mode
)
