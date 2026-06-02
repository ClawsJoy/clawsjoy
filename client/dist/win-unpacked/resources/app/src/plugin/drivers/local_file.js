class LocalFileDriver {
    constructor(plugin) {
        this.plugin = plugin;
    }
    
    async select(params) {
        const { dialog } = require('electron');
        const result = await dialog.showOpenDialog({
            properties: ['openFile']
        });
        
        if (result.canceled) return { success: false };
        
        const fs = require('fs');
        const stats = fs.statSync(result.filePaths[0]);
        
        return {
            success: true,
            path: result.filePaths[0],
            name: require('path').basename(result.filePaths[0]),
            size: stats.size
        };
    }
    
    async read(params) {
        const fs = require('fs');
        const content = fs.readFileSync(params.path, 'utf8');
        return {
            success: true,
            content: this.plugin.redactSensitive(content),
            length: content.length
        };
    }
}

module.exports = LocalFileDriver;
