del /S /F /Q "build"
rmdir /s /q "build"
del /S /F /Q "dist"
rmdir /s /q "dist"

pyinstaller main.spec