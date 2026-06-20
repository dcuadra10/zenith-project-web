@echo off
echo ==============================================
echo 1. Pushing Zenith Project (Portal)
echo ==============================================
git add -A
git commit -m "Update portal website"
git push origin main

echo.
echo ==============================================
echo 2. Pushing Zenith Community
echo ==============================================
cd zenith-community
git add -A
git commit -m "Update community website"
git push origin main
cd ..

echo.
echo ==============================================
echo Both repositories successfully pushed!
echo ==============================================
pause
