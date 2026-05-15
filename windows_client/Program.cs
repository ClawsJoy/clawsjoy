using System;
using System.Diagnostics;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Web.WebView2.WinForms;

namespace ClawsJoy
{
    public partial class MainForm : Form
    {
        private WebView2 webView;
        private Process backendProcess;
        private NotifyIcon trayIcon;
        private ContextMenuStrip trayMenu;

        public MainForm()
        {
            InitializeComponent();
            StartBackend();
            InitializeWebView();
            InitializeTray();
        }

        private void InitializeComponent()
        {
            this.Text = "ClawsJoy AI 助手";
            this.Size = new System.Drawing.Size(1280, 800);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.Icon = System.Drawing.Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            this.FormClosing += MainForm_FormClosing;
        }

        private async void InitializeWebView()
        {
            webView = new WebView2();
            webView.Dock = DockStyle.Fill;
            this.Controls.Add(webView);
            await webView.EnsureCoreWebView2Async(null);
            
            // 等待后端启动
            await Task.Delay(3000);
            webView.CoreWebView2.Navigate("http://localhost:5002");
            
            // 开发者模式（F12）
            webView.CoreWebView2.Settings.AreDevToolsEnabled = true;
        }

        private void StartBackend()
        {
            backendProcess = new Process();
            backendProcess.StartInfo.FileName = "wsl.exe";
            backendProcess.StartInfo.Arguments = "-d Ubuntu -- bash -c 'cd /mnt/d/clawsjoy && ./start.sh'";
            backendProcess.StartInfo.CreateNoWindow = true;
            backendProcess.StartInfo.UseShellExecute = false;
            backendProcess.Start();
        }

        private void InitializeTray()
        {
            trayMenu = new ContextMenuStrip();
            trayMenu.Items.Add("显示", null, (s, e) => { this.Show(); this.WindowState = FormWindowState.Normal; });
            trayMenu.Items.Add("退出", null, (s, e) => { ExitApplication(); });

            trayIcon = new NotifyIcon();
            trayIcon.Text = "ClawsJoy AI 助手";
            trayIcon.Icon = System.Drawing.Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            trayIcon.ContextMenuStrip = trayMenu;
            trayIcon.Visible = true;
            trayIcon.DoubleClick += (s, e) => { this.Show(); this.WindowState = FormWindowState.Normal; };
        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (e.CloseReason == CloseReason.UserClosing)
            {
                e.Cancel = true;
                this.Hide();
            }
        }

        private void ExitApplication()
        {
            try { backendProcess?.Kill(); } catch { }
            Application.Exit();
        }
    }

    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}
