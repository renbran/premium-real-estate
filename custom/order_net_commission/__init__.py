# -*- coding: utf-8 -*-

from . import models
from . import controllers

def post_init_hook(cr, registry):  # pylint: disable=unused-argument
    """
    Post-initialization hook to enable workflow validation
    after successful module installation and database setup
    """
    import logging
    _logger = logging.getLogger(__name__)
    
    try:
        # Enable workflow validation now that installation is complete
        env = registry['account.payment']
        if hasattr(env, '_disable_workflow_validation'):
            env._disable_workflow_validation = False  # pylint: disable=protected-access
            _logger.info("Payment workflow validation enabled after successful module installation")
    except (AttributeError, KeyError) as e:
        _logger.warning("Could not enable workflow validation: %s", e)