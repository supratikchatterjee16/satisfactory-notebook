import os
import logging
import appdirs

from .objects import RecipeData, ResourceData, TierData, ProjectData
__all__ = ['RecipeData', 'ResourceData', 'TierData', 'ProjectData']

logging.basicConfig(format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger(__name__)
try:
    os.makedirs(appdirs.user_log_dir('satisfactory_planner', 'conceivilize'))
except:
    pass
handler = logging.handlers.RotatingFileHandler(
    os.path.join(appdirs.user_log_dir('satisfactory_planner', 'conceivilize'), "satisfactory_analysis.log"), 'w', maxBytes=2000, backupCount=10)
logger.addHandler(handler)
