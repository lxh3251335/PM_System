/**
 * 系统配置文件
 * 用于配置API地址、运行模式等
 */

const CONFIG = {
    // 运行模式：'demo' 使用LocalStorage演示，'production' 使用真实API
    MODE: 'production',
    
    // API基础地址（生产环境通过 Nginx 反向代理，前端和 API 同域）
    API_BASE_URL: '/api',
    
    // 请求超时时间（毫秒）
    REQUEST_TIMEOUT: 30000,
    
    // 是否显示调试信息
    DEBUG: false,
    
    // 本地存储键名前缀
    STORAGE_PREFIX: 'pm_system_',
    
    // 分页配置
    PAGE_SIZE: 20,
    
    // 文件上传配置
    UPLOAD: {
        MAX_SIZE: 10 * 1024 * 1024,  // 10MB
        ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
    }
};

// 工具函数：判断是否为演示模式
function isDemoMode() {
    return CONFIG.MODE === 'demo';
}

// 工具函数：判断是否为生产模式
function isProductionMode() {
    return CONFIG.MODE === 'production';
}

// 工具函数：获取完整API地址
function getApiUrl(path) {
    return `${CONFIG.API_BASE_URL}${path}`;
}

// 工具函数：本地存储键名
function getStorageKey(key) {
    return `${CONFIG.STORAGE_PREFIX}${key}`;
}

// 导出（如果需要）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, isDemoMode, isProductionMode, getApiUrl, getStorageKey };
}
