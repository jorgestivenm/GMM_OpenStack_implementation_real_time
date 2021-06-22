# -*- coding: utf-8 -*-
# !/usr/local/bin python3.8
import os
import sys
import threading

from shared import logger
from src.Classification import classificator
from src.FeatureExtaction import FeatureExtraction
from src.SniffAndSave import SniffAndSave

th1 = threading.Thread(target=SniffAndSave, args=(60, ))
# th2 = threading.Thread(target=FeatureExtraction)
th3 = threading.Thread(target=classificator)
logger.info('Initiating the Sniffer and feature extraction in a thread')
th1.start()
# logger.info('Initiating the Features in a second thread')
# th2.start()
logger.info('Initiating the classifier in a third thread')
th3.start()


logger.info('wating for the threads to avoid bugs')
th1.join()
# th2.join()
th3.join()
