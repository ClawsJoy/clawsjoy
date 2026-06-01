const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

// 导入插件
const ClawsJoyPlugin = require('./src/plugin/ClawsJoyPlugin');

let mainWindow;
let plugin;

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
    
    // 开发模式打开 DevTools
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
    }
}

app.whenReady().then(() => {
    // 初始化插件
    plugin = new ClawsJoyPlugin({
        serverUrl: 'http://localhost:5002'
    });
    
    createWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// 暴露插件给渲染进程
ipcMain.handle('get-plugin-info', () => {
    return {
        version: plugin ? plugin.version : '未加载',
        hasKey: plugin && plugin.encryptionKey ? true : false
    };
});
