import os
import sys
import pathlib

from optim.img import ImgOptim

SCRIPT_PATH = pathlib.Path(sys.argv[0])
FILE_PATH = pathlib.Path(sys.argv[1])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pngquant = pathlib.Path(r'./thirdparty/pngquant.exe')
cjpeg = pathlib.Path(r'./thirdparty/cjpeg.exe')

optim_obj = ImgOptim(bpath=BASE_DIR, fpath=FILE_PATH, spath=SCRIPT_PATH, pngexe=pngquant, jpgexe=cjpeg)