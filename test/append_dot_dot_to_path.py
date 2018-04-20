"""Trick to get ../ of a script added on the path. Just add this to your script
import append_dot_dot_to_path

See: https://github.com/jupyter/notebook/issues/2341
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
