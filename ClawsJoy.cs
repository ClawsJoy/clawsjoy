using System;
using System.Diagnostics;
using System.Windows.Forms;

namespace ClawsJoy
{
    static class Program
    {
        static Process backendProcess;

        [STAThread]
        static void Main()
        {
            // 启动后端
            backendProcess = new Process();
            backendProcess.StartInfo.FileName = "wsl.exe";
            backendProcess.StartInfo.Arguments = "-d Ubuntu -- cd /mnt/d/clawsjoy && ./start.sh";
            backendProcess.StartInfo.CreateNoWindow = true;
            backendProcess.StartInfo.UseShellExecute = false;
            backendProcess.Start();

            // 等待后端启动
            System.Threading.Thread.Sleep(3000);

            // 打开浏览器
            Process.Start("explorer", "http://localhost:5002");

            // 退出时关闭后端
            Application.ApplicationExit += (s, e) => {
                try { backendProcess.Kill(); } catch { }
            };
        }
    }
}
