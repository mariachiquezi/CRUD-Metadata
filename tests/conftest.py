import os

os.environ["JWT_SECRET_KEY"] = "test-only-secret-key-at-least-32-bytes-long"
os.environ["MONGODB_DB_NAME"] = "metadata_catalog_test"
