# diffFiles
Simple program to recursive compare 2 directories and find differences between files.
# diffFiles

Simple program to recursive compare 2 directories and find differences between files.
If files can't be read, the program will try to compare MD5 hashes.

## Run
GUI version:
- on Linux-based system run `diffFiles.desktop` file
- on Windows run `diffFiles.bat` file
Console version:
- `python diffFiles.py "path/to/folder/1" "path/to/folder/2"`

## Ignored extensions
By default I ignore several file extensions:
`jpg`, `jpeg`, `png`, `ttf`, `mo`, `so`, `bin`, `cgi`, `ico`

You can change them by editing global variable `IGNORE_FILES_EXTS` in selected scripts.
