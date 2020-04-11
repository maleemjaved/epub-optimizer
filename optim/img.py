import os
import pathlib
import tempfile
import zipfile
import subprocess
import shutil


class ImgOptim():
    def __init__(self, bpath, fpath, spath, pngexe, jpgexe):
        self.base_path = bpath
        self.epub_path = fpath
        self.script_path = spath
        self.pngexe = pngexe
        self.jpgexe = jpgexe

        self.zip_tempdir_obj, self.zip_tempdir = self.funzip()
        self.jpg_arr, self.png_arr = self.get_imgs()
        self.png_optim()
        self.jpg_optim()
        self.zip_back()

    def funzip(self):
        self.epub_dir, self.epub_fname = os.path.split(self.epub_path)
        epub_name, epub_ext = os.path.splitext(self.epub_fname)

        print(f'{self.epub_fname} Under Processing . . . ')

        """
        Need to create temporary directory because the 3rd party script used here is unable to do in
        memory compression.
        """
        TEMP_DIR = tempfile.TemporaryDirectory()
        TEMP_DIR_PATH = pathlib.Path(TEMP_DIR.name)

        with zipfile.ZipFile(self.epub_path, 'r') as zip_ref:
            zip_ref.extractall(TEMP_DIR_PATH)

        return TEMP_DIR , TEMP_DIR_PATH

    def get_imgs(self):
        # list of paths in files
        jpg_files = []
        png_files = []

        for r, d, f in os.walk(self.zip_tempdir):
            for file in f:
                if file.endswith(".jpg"):
                    jpg_files.append(pathlib.Path(os.path.join(r, file)))
                if file.endswith(".png"):
                    png_files.append(pathlib.Path(os.path.join(r, file)))

        return jpg_files, png_files

    def png_stats(self):
        png_tsize = 0
        for i in (self.png_arr):
            png_tsize += i.stat().st_size
        kbs = png_tsize / 1024
        mbs = kbs / 1024
        return (kbs, mbs)

    def jpg_stats(self):
        jpg_tsize = 0
        for i in (self.jpg_arr):
            jpg_tsize += i.stat().st_size
        kbs = jpg_tsize / 1024
        mbs = kbs / 1024
        return (kbs, mbs)

    def png_optim(self):
        # size before (before_kilobytes -> b_kbs) compression
        b_kbs, b_mbs = self.png_stats()

        yes_c = 0
        no_c = 0

        for indx, i in enumerate(self.png_arr):
            file_path_str = str(i)
            final_cmnd = f'{str(self.pngexe)} --ext=.png --force {file_path_str}'
            # a = subprocess.run([str(pngquant), file_path_str])
            a = subprocess.run(final_cmnd, shell=True)
            if a.returncode != 0:
                no_c += 1
            if a.returncode == 0:
                yes_c += 1

        # size after (after_kilobytes -> a_kbs) compression
        a_kbs, a_mbs = self.png_stats()

        t_png_images = len(self.png_arr)
        print(f'+===+< PNG COMPRESSION >+===+')
        print(f'Success: {t_png_images}/{yes_c} || Failed: {t_png_images}/{no_c}')
        print(f'Before: {b_mbs} Mb || After: {a_mbs}')

    def jpg_optim(self):
        yes_c = 0
        no_c = 0

        # size before (before_kilobytes -> b_kbs) compression
        b_kbs, b_mbs = self.jpg_stats()

        """
        Temporary directory is requried for lossy jpeg file is not overwritable so i have to save
        these images to temporary directory
        """
        TEMP_DIR_JPEG = tempfile.TemporaryDirectory()
        TEMP_DIR_JPEG_PATH = pathlib.Path(TEMP_DIR_JPEG.name)
        self.jpg_tempdir = TEMP_DIR_JPEG_PATH

        # this array will help us later for replacing images from temporary to actual folder
        jpg_rep_arr = []

        # JPG parameters for optimizations
        quality = f'-quality 25'
        smooth = f'-smooth 2'

        # Jpg optimization using cjpeg (mozjpeg)
        for indx, i in enumerate(self.jpg_arr):
            fpath, fname = os.path.split(i)
            output_fpath = pathlib.Path(os.path.join(TEMP_DIR_JPEG_PATH, fname))
            jpg_rep_arr.append((output_fpath, i))

            outfile = f' -outfile "{str(output_fpath)}"'
            full_cmnd = str(self.jpgexe) + " " + quality + " " + smooth + " " + outfile + " " + f'"{str(i)}"'

            a = subprocess.run(full_cmnd, shell=True)
            if a.returncode != 0:
                no_c += 1
            if a.returncode == 0:
                yes_c += 1

        t_jpg_images = len(self.jpg_arr)
        print(f'+===+< JPG COMPRESSION >+===+')
        print(f'Success: {t_jpg_images}/{yes_c} || Failed: {t_jpg_images}/{no_c}')

        # Replacing from temporary to actual temporary zip folder
        for i in jpg_rep_arr:
            remain = i[0]
            remove = i[1]
            shutil.move(remain, remove)

        # size after (after_kilobytes -> a_kbs) compression
        a_kbs, a_mbs = self.jpg_stats()
        print(f'Before: {b_mbs} Mb || After: {a_mbs}')

    def zip_back(self):
        optim_book_path = self.epub_dir
        optim_book_name = "optim_" + self.epub_fname

        shutil.make_archive(pathlib.Path(os.path.join(optim_book_path, optim_book_name)), 'zip', self.zip_tempdir)

        print(f'!!! NEW EPUB CREATED !!!')
