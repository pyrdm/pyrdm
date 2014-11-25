import logging

LOG = logging.getLogger(__name__)
_HANDLER = logging.StreamHandler()
LOG.addHandler(_HANDLER)
_HANDLER.setFormatter(logging.Formatter(
    '%(name)s %(levelname)s: %(message)s'))
del(_HANDLER)
LOG.setLevel(logging.DEBUG)
