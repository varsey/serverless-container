import os
import sys
import logging
import traceback
from .Mailer import Mailer
from docx.opc import exceptions


class Worker:
    LOG_FORMAT='%(asctime)-15s %(name)s %(levelname)-8s %(message)s'

    def __init__(self, logs_filename: str = 'logs.txt'):
        logger_name = os.uname().nodename
        logger = logging.getLogger(logger_name)
        logging.basicConfig(filename=logs_filename, encoding='utf-8', level=logging.INFO, format=self.LOG_FORMAT)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        logger.addHandler(handler)
        self.logs_filename = logs_filename
        self.logger = logger

    def error_processor(self, ex: Exception) -> None:
        """обработчик сообщений об ошибке"""
        self.logger.error("An exception of type {0} occurred. Arguments:\n{1!r}\n".format(type(ex).__name__, ex.args))
        if type(ex) == exceptions.PackageNotFoundError:
            self.logger.info('CANT PROCESS ATTACHMENT FILE')
        else:
            [self.logger.info(f'{item}') for item in traceback.format_exception(type(ex), ex, ex.__traceback__)]
        return None

    def msg_from_req(self, req):
        message = ''
        try:
            message = req.json['message']
        except Exception as ex:
            self.error_processor(ex)
        return message

    def run(self, processor, mailer: Mailer):
        result = []
        try:
            result = processor.process_email()
        except Exception as ex:
            self.error_processor(ex)
            self.logger.warning('Email processing failed')
            mailer.send_email('Email processing failed')

        return result
