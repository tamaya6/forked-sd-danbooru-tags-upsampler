
import sys, os, shutil
import folder_paths

sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from .example_node import DanbooruTagUpsampler
module_root_directory = os.path.dirname(os.path.realpath(__file__))

NODE_CLASS_MAPPINGS = {
    "Danbooru Tag Upsampler": DanbooruTagUpsampler,
                      }

__all__ = ["NODE_CLASS_MAPPINGS"]
