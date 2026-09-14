import logging
import os
import sys

def setup_logger():
    """Configures centralized logging."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "cryptonexis.log")),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("cryptonexis")
