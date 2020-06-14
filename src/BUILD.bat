rmdir /s /q __pycache__
pyinstaller -F DirectoryCleaner.pyw
cd dist
move DirectoryCleaner.exe ../../DirectoryCleaner.exe
cd ..
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q __pycache__
del DirectoryCleaner.spec