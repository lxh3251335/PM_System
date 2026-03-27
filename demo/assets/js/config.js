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

    /** 与后端 EXPORT_VERSION 一致；跨域时读不到响应头时用于默认导出文件名 */
    PM_EXPORT_CONFIG_VERSION: '2',

    /**
     * 若用 Live Server 等非 8000 端口打开 demo，相对路径 /api 会打到错误端口。
     * 此时自动把 API 指到本机 uvicorn 默认端口 8000（仅 localhost/127.0.0.1）。
     */
    _applyLocalApiOverride: function () {
        if (typeof window === 'undefined') return;
        const h = window.location.hostname;
        const p = window.location.port;
        const local = h === '127.0.0.1' || h === 'localhost';
        if (local && p && p !== '8000') {
            this.API_BASE_URL = 'http://' + h + ':8000/api';
        }
    },
    
    // 分页配置
    PAGE_SIZE: 20,
    
    // 文件上传配置
    UPLOAD: {
        MAX_SIZE: 10 * 1024 * 1024,  // 10MB
        ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
    }
};

if (typeof CONFIG._applyLocalApiOverride === 'function') {
    CONFIG._applyLocalApiOverride();
}

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
