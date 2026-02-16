@echo off
echo ========================================
echo Smart Bus Dashboard - Deployment Script
echo ========================================
echo.

echo Step 1: Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo Git is installed!
echo.

echo Step 2: Initializing Git repository...
if not exist .git (
    git init
    echo Git repository initialized!
) else (
    echo Git repository already exists!
)
echo.

echo Step 3: Adding files to Git...
git add .
echo Files added!
echo.

echo Step 4: Creating commit...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=Update Smart Bus Dashboard

git commit -m "%commit_message%"
echo Commit created!
echo.

echo Step 5: Setting up GitHub remote...
set /p github_url="Enter your GitHub repository URL (e.g., https://github.com/username/smart-bus-dashboard.git): "

if "%github_url%"=="" (
    echo ERROR: GitHub URL is required!
    pause
    exit /b 1
)

git remote remove origin >nul 2>&1
git remote add origin %github_url%
echo Remote added!
echo.

echo Step 6: Pushing to GitHub...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Possible reasons:
    echo 1. Wrong repository URL
    echo 2. Authentication failed - use Personal Access Token
    echo 3. Repository doesn't exist on GitHub
    echo.
    echo Create a Personal Access Token at:
    echo https://github.com/settings/tokens
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Code pushed to GitHub!
echo ========================================
echo.
echo Next steps:
echo 1. Go to https://share.streamlit.io/
echo 2. Sign in with GitHub
echo 3. Click "New app"
echo 4. Select your repository
echo 5. Set main file: working_dashboard.py
echo 6. Click "Deploy"
echo.
echo Your dashboard will be live in 2-5 minutes!
echo.
pause
