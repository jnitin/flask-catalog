# See: https://github.com/jupyter/notebook/issues/2341
# to get access to instance/config.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
