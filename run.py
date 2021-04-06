import os
import sys
import threading

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

from src.FeatureExtaction import FeatureExtraction
from src.SniffAndSave import SniffAndSave

th1 = threading.Thread(target=SniffAndSave, args=(60, ))
th2 = threading.Thread(target=FeatureExtraction)

print('Initiating the Sniffer in a thread')
th1.start()
print('Initiating the Features in a second thread')
th2.start()


print('wating for the threads to avoid bugs')
th1.join()
th2.join()
