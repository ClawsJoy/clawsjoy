const { app, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

class ClawsJoyPlugin {
    constructor(options = {}) {
        this.version = '1.0.0';
        this.serverUrl = options.serverUrl || 'http://localhost:5002';
        this.userDataPath = path.join(app.getPath('userData'), 'clawsjoy');
        this.encryptionKey = null;
        this.drivers = new Map();
        
        this.init();
    }
    
    async init() {
        console.log('🦞 ClawsJoy 插件 v' + this.version);
        
        // 创建数据目录
        if (!fs.existsSync(this.userDataPath)) {
            fs.mkdirSync(this.userDataPath, { recursive: true });
        }
        
        // 加载密钥
        await this.loadEncryptionKey();
        
        // 注册 IPC
        this.registerIpcHandlers();
        
        // 加载本地驱动
        await this.loadLocalDrivers();
    }
    
    async loadEncryptionKey() {
        const keyPath = path.join(this.userDataPath, 'key.bin');
        
        if (fs.existsSync(keyPath)) {
            this.encryptionKey = fs.readFileSync(keyPath);
        } else {
            this.encryptionKey = crypto.randomBytes(32);
            fs.writeFileSync(keyPath, this.encryptionKey);
        }
    }
    
    encrypt(data) {
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv('aes-256-gcm', this.encryptionKey, iv);
        
        const encrypted = Buffer.concat([
            cipher.update(JSON.stringify(data), 'utf8'),
            cipher.final()
        ]);
        
        return {
            iv: iv.toString('base64'),
            data: encrypted.toString('base64'),
            tag: cipher.getAuthTag().toString('base64')
        };
    }
    
    decrypt(encrypted) {
        const decipher = crypto.createDecipheriv(
            'aes-256-gcm',
            this.encryptionKey,
            Buffer.from(encrypted.iv, 'base64')
        );
        
        decipher.setAuthTag(Buffer.from(encrypted.tag, 'base64'));
        
        const decrypted = Buffer.concat([
            decipher.update(Buffer.from(encrypted.data, 'base64')),
            decipher.final()
        ]);
        
        return JSON.parse(decrypted.toString('utf8'));
    }
    
    redactSensitive(text) {
        // 手机号
        text = text.replace(/1[3-9]\d{9}/g, (m) => m.slice(0,3) + '****' + m.slice(7));
        // 身份证
        text = text.replace(/\d{17}[\dXx]/g, (m) => m.slice(0,6) + '********' + m.slice(14));
        // 邮箱
        text = text.replace(/([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g, (m, l, d) => l.slice(0,2) + '***@' + d);
        // API Key
        text = text.replace(/sk-[a-zA-Z0-9]{32,}/g, 'sk-***[API_KEY]');
        
        return text;
    }
    
    async loadLocalDrivers() {
        const driversPath = path.join(__dirname, 'drivers');
        
        if (fs.existsSync(driversPath)) {
            const files = fs.readdirSync(driversPath);
            for (const file of files) {
                if (file.endsWith('.js')) {
                    const DriverClass = require(path.join(driversPath, file));
                    const name = file.replace('.js', '');
                    this.drivers.set(name, new DriverClass(this));
                    console.log(`✅ 驱动: ${name}`);
                }
            }
        }
    }
    
    registerIpcHandlers() {
        ipcMain.handle('plugin:select-file', async () => {
            const result = await dialog.showOpenDialog({ properties: ['openFile'] });
            return result;
        });
        
        ipcMain.handle('plugin:read-file', async (event, filePath) => {
            const content = fs.readFileSync(filePath, 'utf8');
            return this.redactSensitive(content);
        });
        
        ipcMain.handle('plugin:save-data', async (event, { key, data }) => {
            const encrypted = this.encrypt(data);
            const filePath = path.join(this.userDataPath, `${key}.enc`);
            fs.writeFileSync(filePath, JSON.stringify(encrypted));
            return { success: true };
        });
        
        ipcMain.handle('plugin:load-data', async (event, key) => {
            const filePath = path.join(this.userDataPath, `${key}.enc`);
            if (fs.existsSync(filePath)) {
                const encrypted = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                return this.decrypt(encrypted);
            }
            return null;
        });
    }
}

module.exports = ClawsJoyPlugin;
