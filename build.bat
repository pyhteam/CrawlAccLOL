@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔══════════════════════════════════════════════════════════╗
echo ║         CrawlAccLOL - Build Tool                        ║
echo ║         Build EXE with PyInstaller                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Đọc version hiện tại
set "VERSION_FILE=src\__init__.py"
for /f "tokens=2 delims==" %%a in ('findstr "__version__" %VERSION_FILE%') do (
    set "CURRENT_VERSION=%%~a"
)
:: Trim spaces and quotes
set "CURRENT_VERSION=%CURRENT_VERSION: =%"
set "CURRENT_VERSION=%CURRENT_VERSION:"=%"

echo [INFO] Version hiện tại: v%CURRENT_VERSION%
echo.

:: Hỏi nâng version
set /p "UPGRADE_VERSION=Bạn có muốn nâng version không? (y/n): "

if /i "%UPGRADE_VERSION%"=="y" (
    echo.
    echo  Chọn kiểu nâng version:
    echo    1. Patch  (x.x.X) - Bug fixes
    echo    2. Minor  (x.X.0) - New features  
    echo    3. Major  (X.0.0) - Breaking changes
    echo    4. Nhập thủ công
    echo.
    set /p "VERSION_TYPE=Chọn (1-4): "
    
    if "!VERSION_TYPE!"=="4" (
        set /p "NEW_VERSION=Nhập version mới (vd: 2.1.0): "
    ) else (
        :: Parse current version
        for /f "tokens=1,2,3 delims=." %%a in ("%CURRENT_VERSION%") do (
            set "MAJOR=%%a"
            set "MINOR=%%b"
            set "PATCH=%%c"
        )
        
        if "!VERSION_TYPE!"=="1" (
            set /a "PATCH=!PATCH!+1"
        ) else if "!VERSION_TYPE!"=="2" (
            set /a "MINOR=!MINOR!+1"
            set "PATCH=0"
        ) else if "!VERSION_TYPE!"=="3" (
            set /a "MAJOR=!MAJOR!+1"
            set "MINOR=0"
            set "PATCH=0"
        )
        
        set "NEW_VERSION=!MAJOR!.!MINOR!.!PATCH!"
    )
    
    echo.
    echo [INFO] Nâng version: v%CURRENT_VERSION% → v!NEW_VERSION!
    
    :: Cập nhật file __init__.py
    powershell -Command "(Get-Content '%VERSION_FILE%') -replace '__version__ = \".*\"', '__version__ = \"!NEW_VERSION!\"' | Set-Content '%VERSION_FILE%'"
    
    set "CURRENT_VERSION=!NEW_VERSION!"
    echo [OK] Đã cập nhật version thành v!NEW_VERSION!
)

echo.
echo ══════════════════════════════════════════════════════════
echo [BUILD] Đang build CrawlAccLOL v%CURRENT_VERSION%...
echo ══════════════════════════════════════════════════════════
echo.

:: Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python không được tìm thấy! Vui lòng cài đặt Python.
    pause
    exit /b 1
)

:: Kiểm tra và cài đặt dependencies
echo [STEP 1/3] Kiểm tra dependencies...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Đang cài đặt dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Không thể cài đặt dependencies!
        pause
        exit /b 1
    )
)

:: Clean build cũ
echo [STEP 2/3] Dọn dẹp build cũ...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

:: Build với PyInstaller
echo [STEP 3/3] Đang build EXE...
echo.

pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "CrawlAccLOL_v%CURRENT_VERSION%" ^
    --add-data "src;src" ^
    --hidden-import "PyQt5" ^
    --hidden-import "qfluentwidgets" ^
    --hidden-import "requests" ^
    --hidden-import "bs4" ^
    --collect-all "qfluentwidgets" ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build thất bại!
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  ✅ BUILD THÀNH CÔNG!                                   ║
echo ║                                                          ║
echo ║  File: dist\CrawlAccLOL_v%CURRENT_VERSION%.exe          ║
echo ║  Version: v%CURRENT_VERSION%                             ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Mở thư mục dist
explorer dist

pause
