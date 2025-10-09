"""
Custom storage classes for handling static files
"""
from whitenoise.storage import CompressedStaticFilesStorage
import logging

logger = logging.getLogger(__name__)


class ForgivingStaticFilesStorage(CompressedStaticFilesStorage):
    """
    A forgiving version of CompressedStaticFilesStorage that handles missing files gracefully.
    This avoids the strict manifest processing that causes build failures.
    """
    
    def url(self, name, force=False):
        """
        Override URL method to handle missing files gracefully.
        """
        try:
            return super().url(name, force)
        except Exception as e:
            logger.warning(f"Static file issue (using fallback): {name} - {e}")
            # Fall back to the original name with base URL
            return self.base_url + name