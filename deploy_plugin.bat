@echo off
rem U:\.ssh\thomas.ppk in putty hinterlegt im gespeicherten Profil

rem ssh befehle ausfuehren:
rem plink.exe -batch -load "A_vsrv25-dinux4 NEU" ls -la /home/rduser/public_html/qgisplugins/plugins_v3/breitband/Multiclip/Plugin

set PATH=D:\Programme\putty;C:\Programme\7-Zip;%PATH%
set create_folders=1


set plugin_foldername=nan_checker
set plugin_zipfile=%plugin_foldername%.zip

rem source fuer Ordnerstruktur
set source=/home/rduser/public_html/qgisplugins/plugins_v3/folders_template/*

set target=/home/rduser/public_html/qgisplugins/plugins_v3/breitband/%plugin_foldername%


if %create_folders%==1 (plink.exe -batch -load "A_vsrv25-dinux4 NEU" rsync -av -f\"+ */\" -f\"- *\" %source% %target%
echo Ordnerstruktur erstellt oder ergaenzt)

rem alles in tempfolder kopieren vorm zippen, weil 7z sonst abbricht wenn bestimmte Dateien geoeffnet sind wie zb excel

echo "-------------------- XCOPY to temp ------------------------------------------"

set tempfolder=%plugin_foldername%%DATE:~6,4%_%DATE:~3,2%_%DATE:~0,2%_%time:~0,2%_%time:~3,2%

xcopy ..\%plugin_foldername% %temp%\%tempfolder%\%plugin_foldername%\* /e /i /y /s
rem %var:~10,5%  will extract 5 characters from position 10 in the environment variable %var%

echo "--------------------zip to zipfile ------------------------------------------"
7z.exe a %plugin_zipfile% %temp%\%tempfolder%\%plugin_foldername% -r -x!*.vscode  -x!*__pycache__ -x!*QGIS_Repository -x!*.bat -x!*.zip -x!.git* -aoa

echo "--------------------copy zipfile to dinux ------------------------------------------"

pscp.exe -scp -batch -load "A_vsrv25-dinux4 NEU" %plugin_zipfile% rduser@vsrv25-dinux4:%target%/Plugin/%plugin_zipfile%

echo "--------------------copy QGIS_Repository to dinux -----------------------------------" 
pscp.exe -scp -batch -load "A_vsrv25-dinux4 NEU" QGIS_Repository\* rduser@vsrv25-dinux4:%target%/QGIS_Repository/

echo "-------------------- merge_pyplugin_snippets.py ------------------------------------------" 

plink.exe -batch -load "A_vsrv25-dinux4 NEU" "python /home/rduser/public_html/qgisplugins/plugins_v3/merge_pyplugin_snippets.py /home/rduser/public_html/qgisplugins/plugins_v3/breitband /home/rduser/public_html/qgisplugins/plugins_v3/breitband.xml"

echo "-------------------- Ende  ------------------------------------------" 

pause
