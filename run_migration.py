import os
os.environ.setdefault("MIGRATIONS_ONLY", "1")
from app import app, db
import logging
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _load_migration(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load migration module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

if __name__ == '__main__':
    try:
        with app.app_context():
            logger.info("Running database migrations...")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            mig1_path = os.path.join(base_dir, 'migrations', '001_add_education_field.py')
            mig2_path = os.path.join(base_dir, 'migrations', '002_add_embeddings.py')

            mig1 = _load_migration('migration_001', mig1_path)
            mig1.upgrade()
            logger.info("001_add_education_field applied")

            mig2 = _load_migration('migration_002', mig2_path)
            mig2.upgrade()
            logger.info("002_add_embeddings applied")

            logger.info("Migrations completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise