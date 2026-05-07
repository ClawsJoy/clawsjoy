// ClawsJoy 动态配置 - 自动适应手机/电脑访问
(function() {
    const hostname = window.location.hostname;
    // 如果是本地访问，用 localhost；否则用当前 IP
    let baseUrl = 'http://localhost';
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        baseUrl = `http://${hostname}`;
    }
    
    window.CLAWSJOY_API = {
        base: baseUrl,
        tenant: `${baseUrl}:8088/api/tenants`,
        libraryList: `${baseUrl}:8084/api/library/list?tenant_id=1`,
        libraryUpload: `${baseUrl}:8084/api/library/upload`,
        libraryFile: (id) => `${baseUrl}:8084/api/library/file/${id}?tenant_id=1`,
        taskPromo: `${baseUrl}:8084/api/task/promo`,
        agent: `${baseUrl}:8087/api/agent`,
        coffee: `${baseUrl}:8085/api/coffee/shops`,
        health: `${baseUrl}:8092/api/auth/health`
    };
    
    console.log('✅ API 已配置:', window.CLAWSJOY_API);
})();
