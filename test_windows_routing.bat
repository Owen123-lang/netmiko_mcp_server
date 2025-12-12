@echo off
echo ============================================================
echo Windows Routing Diagnostic
echo ============================================================
echo.

echo [1] Checking current routes...
echo ============================================================
route print | findstr "10.1.1"
echo.

echo [2] Checking route to 192.168.242.0 network...
echo ============================================================
route print | findstr "192.168.242"
echo.

echo [3] Testing ping to R1 (192.168.242.129)...
echo ============================================================
ping -n 2 192.168.242.129
echo.

echo [4] Testing ping to R2 via R1 (10.1.1.2)...
echo ============================================================
ping -n 2 10.1.1.2
echo.

echo [5] Traceroute to 10.1.1.2...
echo ============================================================
tracert -d -h 5 10.1.1.2
echo.

echo [6] Checking Windows Firewall status...
echo ============================================================
netsh advfirewall show allprofiles state
echo.

echo ============================================================
echo Diagnostic Complete!
echo ============================================================
echo.
echo ANALYSIS:
echo - If ping to R1 works but ping to R2 fails
echo   Problem: R1 needs to have IP forwarding enabled (FIXED)
echo.
echo - If tracert shows packets reaching R1 but not R2
echo   Problem: R1 firewall or routing issue
echo.
echo - If tracert shows no response at all
echo   Problem: Windows routing or firewall blocking
echo.
pause