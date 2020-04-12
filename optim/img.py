import os
import pathlib
import tempfile
import zipfile
import subprocess
import shutil


class ImgOptim():
    def __init__(self, input_type, input_path, png_utility, jpg_utility):
        input_type = input_type
        input_path = input_path

        png_utility = png_utility
        jpg_utility = jpg_utility

        self.main_function(input_type, input_path, png_utility, jpg_utility)

    def main_function(self, input_type, input_path, png_utility, jpg_utility):
        epub_file_array = []

        if input_type == 1:
            epub_file_array = self.file_from_dir(input_path, ext='.epub')
        else:
            epub_file_array.append(input_path)

        for single_epub in epub_file_array:
            self.optimize_one(file_path=single_epub, png_utility=png_utility, jpg_utility=jpg_utility)

    def optimize_one(self, file_path, png_utility, jpg_utility):
        """
        This will produce new compressed .epub file after applying all the transformations

        :param filepath: path of file (.epub)
        :return: "Success or Fail"
        """
        # Book Under Processing

        # provide epub file path
        unzip_info = self.file_unzip(file_path)

        # get paths array of jpg and png file in the epub ( extracted in temporary directory)
        jpg_files = self.file_from_dir(dir_path=unzip_info['temp_dir_epub'], ext='.jpg')
        png_files = self.file_from_dir(dir_path=unzip_info['temp_dir_epub'], ext='.png')

        # compress files png and jpg
        self.png_compress(pngexe=png_utility, png_file_array=png_files)
        self.jpg_compress(jpgexe=jpg_utility, jpg_file_array=jpg_files)

        # temporary dir (where epub is extracted) will be zipped back to produce new compressed epub
        self.dir_to_zip(new_file_dir=unzip_info["file_dir_path"], old_file_name=unzip_info["file_full_name"],
                        dir_to_zip=unzip_info["temp_dir_epub"])

    def file_unzip(self, file_path):
        """
        This will unzip the file in temporary directory.

        :param file_path: path of file (.epub)
        :return: {file_path: PathObj, file_name: "", temporary_dir: PathObj}
        """

        file_dir_path, file_full_name = os.path.split(file_path)
        file_name, file_ext = os.path.splitext(file_full_name)

        # Printing book name to console
        print(f'Processing "{file_full_name}" . . . .')

        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir_path = pathlib.Path(temp_dir_obj.name)

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir_path)

        unzip_info = {
            "file_full_path": file_path,
            "file_dir_path": file_dir_path,
            "file_full_name": file_full_name,
            "temp_dir_epub": temp_dir_obj
        }
        return unzip_info

    def file_from_dir(self, dir_path, ext=None):
        """
        This function will return array of files from given directory path of specific extension.

        :param dir_path: directory path
        :param ext: extension of files
        :return: array of file paths of specific extension
        """
        file_arr = []

        for r, d, f in os.walk(dir_path.name):
            for file in f:
                if ext != None:
                    if file.endswith(ext):
                        file_arr.append(pathlib.Path(os.path.join(r, file)))
                else:
                    file_arr.append(pathlib.Path(os.path.join(r, file)))
        return file_arr

    def png_compress(self, pngexe, png_file_array):
        """
        this function will compress the .png images
        :param pngexe: executable file for .png file compression
        :param png_file_array: array of .png file paths
        :return: ""
        """
        yes_c = 0
        no_c = 0

        size_before_compression = self.file_size(file_array=png_file_array)

        for indx, i in enumerate(png_file_array):
            png_file_path = str(i)
            shell_command = f'{str(pngexe)} --ext=.png --force {png_file_path}'
            a = subprocess.run(shell_command, shell=True)
            if a.returncode != 0:
                no_c += 1
            if a.returncode == 0:
                yes_c += 1

        size_after_compression = self.file_size(file_array=png_file_array)
        total_png_file = len(png_file_array)
        print(f'+===+< PNG COMPRESSION SUMMARY >+===+')
        print(f'Success: {yes_c}/{total_png_file} || Failed: {no_c}/{total_png_file}')
        print(f'Before: {size_before_compression} Mb || After: {size_after_compression} Mb')

    def jpg_compress(self, jpgexe, jpg_file_array):
        """
        this will compress the jpg files
        :param jpgexe: third party commandline utility to compress jpg
        :param jpg_file_array: array containing path of jpg files
        :return:
        """
        yes_c = 0
        no_c = 0

        size_before_compression = self.file_size(file_array=jpg_file_array)

        tempdir_jpg_obj = tempfile.TemporaryDirectory()
        tempdir_jpg_path = pathlib.Path(tempdir_jpg_obj.name)

        # this array will help us later for replacing images from temporary to actual folder
        jpg_rep_array = []

        # JPG parameters for optimizations
        quality = f'-quality 25'
        smooth = f'-smooth 2'

        # Jpg optimization using cjpeg (mozjpeg)
        for indx, i in enumerate(jpg_file_array):
            jpg_file_path, jpg_file_name = os.path.split(i)
            output_file_path = pathlib.Path(os.path.join(tempdir_jpg_path, jpg_file_name))

            outfile = f' -outfile "{str(output_file_path)}"'
            shell_command = str(jpgexe) + " " + quality + " " + smooth + " " + outfile + " " + f'"{str(i)}"'

            a = subprocess.run(shell_command, shell=True)

            if a.returncode != 0:
                no_c += 1
            if a.returncode == 0:
                yes_c += 1

            jpg_rep_array.append((output_file_path, i))
        # for loop ends here

        # Replacing from temporary to actual temporary zip folder
        for i in jpg_rep_array:
            remain = i[0]
            remove = i[1]
            shutil.move(remain, remove)

        size_after_compression = self.file_size(file_array=jpg_file_array)
        total_jpg_file = len(jpg_file_array)

        print(f'+===+< JPG COMPRESSION SUMMARY >+===+')
        print(f'Success: {yes_c}/{total_jpg_file} || Failed: {no_c}/{total_jpg_file}')
        print(f'Before: {size_before_compression} Mb || After: {size_after_compression} Mb')

    def file_size(self, file_array):
        """
        given a array of file paths this will return the aggregated size in megabytes
        :param file_array: array object containing file paths
        :return: aggregated size in Mb
        """
        total_bytes = 0
        for i in (file_array):
            total_bytes += i.stat().st_size
        mbs = total_bytes / (1024 * 1024)
        return round(mbs, 2)

    def dir_to_zip(self, new_file_dir, old_file_name, dir_to_zip):
        new_file_name = 'OPTIMIZED_' + old_file_name
        shutil.make_archive(pathlib.Path(os.path.join(new_file_dir, new_file_name)), 'zip', dir_to_zip.name)
        print(f'File "{new_file_name}" Compressed Successfully\n')
        print(f'==================== ++ [^_^] ++ ====================\n\n')
