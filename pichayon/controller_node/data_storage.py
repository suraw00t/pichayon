import asyncio
import logging
from tinydb import TinyDB, Query

logger = logging.getLogger(__name__)

class DataStorage:
    def __init__(self, settings):
        self.settings = settings
        self.db = TinyDB(self.settings['TINYDB_STORAGE_PATH']) 

    def initial_data_after_restart(self, data):
        logger.debug(f'>>>>>>>{data}')
