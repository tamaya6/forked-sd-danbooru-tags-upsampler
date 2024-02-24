
import sys, os, shutil
import folder_paths

sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from .node import DanbooruTagUpsampler
module_root_directory = os.path.dirname(os.path.realpath(__file__))

NODE_CLASS_MAPPINGS = {
    "DanbooruTagUpsampler": DanbooruTagUpsampler,
                      }

__all__ = ["NODE_CLASS_MAPPINGS"]
