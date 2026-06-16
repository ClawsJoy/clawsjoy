// 推荐结果展示优化
function displayRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        return "未找到合适的能力";
    }
    
    let html = `## 🎯 推荐能力 (Top ${recommendations.length})\n\n`;
    for (let i = 0; i < recommendations.length; i++) {
        const r = recommendations[i];
        const typeIcon = r._type === 'agent' ? '🤖' : 
                         r._type === 'skill' ? '🔧' : 
                         r._type === 'tool' ? '🛠️' : '📦';
        html += `${i+1}. ${typeIcon} **${r.name}**\n`;
        html += `   ${r.description}\n`;
        if (r._type === 'agent') {
            html += `   📌 能力: ${r.capabilities?.map(c => c.name).join(', ') || '通用'}\n`;
        }
        html += `\n`;
    }
    return html;
}
