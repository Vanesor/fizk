@echo off
echo Building Rust ZKP Toolkit...

REM Option 1: Development build (faster, links directly)
REM maturin develop
REM echo Rust ZKP Toolkit built for development. Python can import it directly.

REM Option 2: Release build (optimized, creates a wheel)
echo Creating wheels directory if it doesn't exist...
if not exist "..\fl_system\wheels" mkdir "..\fl_system\wheels"
maturin build --release -o ..\fl_system\wheels
if %errorlevel% neq 0 (
    echo Rust build FAILED.
    exit /b 1
)
echo Rust ZKP Toolkit wheel built successfully in ..\fl_system\wheels
echo You may need to install it: pip install zkp_toolkit --no-index --find-links=../fl_system/wheels --force-reinstall