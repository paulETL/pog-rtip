SQLALCHEMY_DATABASE_URI = (
    "postgresql+psycopg2://superset:superset@superset-db:5432/superset"
)

SECRET_KEY = "pogrtip_superset_secret"

ENABLE_PROXY_FIX = True
PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1, "x_prefix": 1}

WTF_CSRF_ENABLED = False