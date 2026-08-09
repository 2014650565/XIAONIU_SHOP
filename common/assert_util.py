import logging

log=logging.getLogger(__name__)

def assert_with_log(condition:bool,message:str):
    if not condition:
        log.error(message,stacklevel=2)
        assert condition,message