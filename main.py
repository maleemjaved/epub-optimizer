import os
import sys
import pathlib
from optim.img import ImgOptim

base_path = os.path.dirname(os.path.abspath(__file__))
script_path = pathlib.Path(sys.argv[0])
cmd_arguments = sys.argv[1:]

pngquant = pathlib.Path(r'./thirdparty/pngquant.exe')
cjpeg = pathlib.Path(r'./thirdparty/cjpeg.exe')

# 0 for file , 1 for directory
input_type = None
input_path = None

if len(cmd_arguments) == 2:
    if cmd_arguments[0] == '-d':
        input_path = pathlib.Path(cmd_arguments[1])
        input_type = 1
    if cmd_arguments[0] == '-f':
        input_path = pathlib.Path(cmd_arguments[1])
        input_type = 0
else:
    print("Arugments not provided as per required")
    print('Single epub file compression:~ python main.py -f "path_to_file.epub"')
    print('Compressing epub multiple files in directory:~ python main.py -d "path_to_directory"')

optim_obj = ImgOptim(input_type=input_type, input_path=input_path, png_utility=pngquant, jpg_utility=cjpeg)

print("Thank You For Using EPUB-OPTIMIZER")
