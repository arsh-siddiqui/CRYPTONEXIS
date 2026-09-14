import logging
from utils.config import load_config
from utils.logger import setup_logger
from database.schema import initialize_database
from gui.main_window import launch_gui

def main():
    # Initialize logger
    logger = setup_logger()
    logger.info("Starting Cryptonexis...")

    # Load configuration
    config = load_config()
    logger.info(f"Loaded config. APP_ENV: {config['APP_ENV']}, DATA_MODE: {config['DATA_MODE']}")

    # Initialize database
    initialize_database()

    # Launch GUI
    try:
        logger.info("Launching GUI...")
        launch_gui(config)
    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
    finally:
        logger.info("Shutting down Cryptonexis.")

if __name__ == "__main__":
    main()
