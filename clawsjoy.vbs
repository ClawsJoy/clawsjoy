CreateObject("WScript.Shell").Run "wsl -d Ubuntu -- bash -c 'cd /mnt/d/clawsjoy && ./start.sh'", 0, False
WScript.Sleep 3000
CreateObject("WScript.Shell").Run "explorer http://localhost:5002", 1, False
