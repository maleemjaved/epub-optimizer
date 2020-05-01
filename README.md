# epub-optimizer
python script to reduce size of epub file by compressing the images inside the epub.

## windows executable (dist/epub-optimizer.exe) usage
epub-optimizer.exe -f "path_to_epub_file"

epub-optimizer.exe -d "path_to_directory_with_epub_files"

## python (main.py) usage
python main.py -f "path_to_epub_file"

python main.py -d "path_to_directory_with_epub_files"

## usage instructions for macOS
Note: Requires Brew installed from https://brew.sh

```
brew install python3 pngquant mozjpeg
pip3 install pathlib
mkdir ~/dev/
git clone https://github.com/maleemjaved/epub-optimizer.git ~/dev/
cd ~/dev/epub-optimizer
ln -f /usr/local/bin/pngquant ./thirdparty/pngquant.exe
ln -f /usr/local/bin/cjpeg ./thirdparty/cjpeg.exe
python3 main.py -f "path_to_epub_file"
```

## state
alpha
