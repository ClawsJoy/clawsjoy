const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');

let mainWindow;
let workflowWindow;
let codeReviewWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            webSecurity: false
        },
        title: 'ClawsJoy 智能助手',
        backgroundColor: '#0a0a1a'
    });
    mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
    mainWindow.setMenuBarVisibility(false);
    if (process.argv.includes('--dev')) mainWindow.webContents.openDevTools();
}

function createWorkflowWindow() {
    if (workflowWindow) { workflowWindow.focus(); return; }
    workflowWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: { nodeIntegration: true, contextIsolation: false },
        frame: false,
        titleBarStyle: 'hidden',
        backgroundColor: '#1a1a2e'
    });
    workflowWindow.loadFile(path.join(__dirname, 'renderer', 'workflow.html'));
    workflowWindow.on('closed', () => { workflowWindow = null; });
    if (process.argv.includes('--dev')) workflowWindow.webContents.openDevTools();
}

function createCodeReviewWindow() {
    if (codeReviewWindow) { codeReviewWindow.focus(); return; }
    codeReviewWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: { nodeIntegration: true, contextIsolation: false },
        frame: false,
        titleBarStyle: 'hidden',
        backgroundColor: '#1a1a2e'
    });
    codeReviewWindow.loadFile(path.join(__dirname, 'renderer', 'code_review.html'));
    codeReviewWindow.on('closed', () => { codeReviewWindow = null; });
    if (process.argv.includes('--dev')) codeReviewWindow.webContents.openDevTools();
}

const menuTemplate = [
    {
        label: '文件',
        submenu: [
            { label: '新建工作流', click: () => createWorkflowWindow() },
            { label: '代码审核', click: () => createCodeReviewWindow() },
            { type: 'separator' },
            { label: '退出', role: 'quit' }
        ]
    },
    {
        label: '视图',
        submenu: [
            { label: '刷新', role: 'reload' },
            { label: '开发者工具', role: 'toggleDevTools' }
        ]
    },
    {
        label: '帮助',
        submenu: [
            { label: '关于 ClawsJoy', click: () => {
                dialog.showMessageBox({ message: 'ClawsJoy v4.0.0\n智能体AI系统\n\n工作流编辑器 | 代码审核 | Agent协作', title: '关于' });
            }}
        ]
    }
];

app.whenReady().then(() => {
    createWindow();
    const menu = Menu.buildFromTemplate(menuTemplate);
    Menu.setApplicationMenu(menu);
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('get-app-info', () => {
    return { name: 'ClawsJoy', version: '4.0.0' };
});
