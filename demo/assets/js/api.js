/**
 * API客户端
 * 统一管理所有后端API调用
 */

/** 从 Content-Disposition 解析文件名（兼容 UTF-8 / utf-8、引号形式） */
function parseContentDispositionFilename(dispo) {
    if (!dispo || typeof dispo !== 'string') {
        return null;
    }
    const star = /filename\*=(?:UTF-8|utf-8)''([^;\n]+)/i.exec(dispo);
    if (star) {
        var raw = star[1].trim().replace(/^["']+|["']+$/g, '');
        try {
            return decodeURIComponent(raw);
        } catch (e) {
            return raw;
        }
    }
    var q = /filename="((?:[^"\\]|\\.)*)"/i.exec(dispo);
    if (q) {
        return q[1].replace(/\\"/g, '"');
    }
    var plain = /filename=([^;\n]+)/i.exec(dispo);
    if (plain) {
        return plain[1].trim().replace(/^["']+|["']+$/g, '');
    }
    return null;
}

class ApiClient {
    constructor() {
        this.baseUrl = CONFIG.API_BASE_URL;
        this.timeout = CONFIG.REQUEST_TIMEOUT;
        this.token = localStorage.getItem(getStorageKey('token'));
    }

    /**
     * 通用请求方法
     */
    async request(method, url, data = null, options = {}) {
        const rawRole = (localStorage.getItem('userRole') || '').toLowerCase();
        const normalizedRole = rawRole === 'factory' ? 'admin' : (rawRole === 'user' ? 'customer' : rawRole);
        const currentUserId = (localStorage.getItem('currentUserId') || '').trim();
        const currentUsername = (localStorage.getItem('currentUsername') || '').trim();
        const encodedUsername = currentUsername ? encodeURIComponent(currentUsername) : '';
        const config = {
            method: method.toUpperCase(),
            headers: {
                'Content-Type': 'application/json',
                ...(normalizedRole ? { 'X-User-Role': normalizedRole } : {}),
                ...(currentUserId ? { 'X-User-Id': currentUserId } : {}),
                ...(encodedUsername ? { 'X-Username': encodedUsername } : {}),
                ...options.headers
            }
        };

        // 添加认证token（如果有）
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        // 添加请求体
        if (data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
            config.body = JSON.stringify(data);
        }

        // 处理查询参数
        let fullUrl = `${this.baseUrl}${url}`;
        if (data && config.method === 'GET') {
            const params = new URLSearchParams(data);
            fullUrl += `?${params.toString()}`;
        }

        try {
            if (CONFIG.DEBUG) {
                console.log(`[API] ${config.method} ${fullUrl}`, data);
            }

            // 显示加载状态
            this.showLoading();

            // 发送请求（带超时控制）
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(fullUrl, {
                ...config,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            // 解析响应
            const result = await response.json();

            if (CONFIG.DEBUG) {
                console.log(`[API] Response:`, result);
            }

            // 隐藏加载状态
            this.hideLoading();

            // 处理错误响应
            if (!response.ok) {
                // #region agent log
                fetch('http://127.0.0.1:7487/ingest/b1782c58-c736-4a26-b251-acb345c57f1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'20b895'},body:JSON.stringify({sessionId:'20b895',location:'api.js:error-response',message:'API error response',data:{status:response.status,url:fullUrl,result:result,detailType:typeof result.detail,detailIsArray:Array.isArray(result.detail),detailValue:JSON.stringify(result.detail)},timestamp:Date.now(),hypothesisId:'H1-H2'})}).catch(()=>{});
                // #endregion
                // 401: Token无效或过期 -> 跳转登录
                if (response.status === 401) {
                    console.warn('[API] 认证失败(401)，跳转登录页');
                    this.clearToken();
                    localStorage.removeItem('userRole');
                    localStorage.removeItem('currentUserId');
                    localStorage.removeItem('currentUsername');
                    const isLoginPage = window.location.pathname.endsWith('login.html');
                    if (!isLoginPage) {
                        alert('登录已过期，请重新登录');
                        window.location.href = 'login.html';
                    }
                    throw new Error('登录已过期');
                }
                let errMsg = result.detail || result.message || '请求失败';
                if (Array.isArray(errMsg)) {
                    errMsg = errMsg.map(e => e.msg || JSON.stringify(e)).join('; ');
                } else if (typeof errMsg === 'object') {
                    errMsg = errMsg.msg || JSON.stringify(errMsg);
                }
                throw new Error(errMsg);
            }

            return result;

        } catch (error) {
            this.hideLoading();
            // #region agent log
            fetch('http://127.0.0.1:7487/ingest/b1782c58-c736-4a26-b251-acb345c57f1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'20b895'},body:JSON.stringify({sessionId:'20b895',location:'api.js:catch-block',message:'API catch error',data:{errorType:typeof error,errorName:error?.name,errorMessage:error?.message,errorStr:String(error),isError:error instanceof Error},timestamp:Date.now(),hypothesisId:'H3-H4'})}).catch(()=>{});
            // #endregion

            if (error.name === 'AbortError') {
                throw new Error('请求超时，请检查网络连接');
            }

            if (CONFIG.DEBUG) {
                console.error(`[API] Error:`, error);
            }

            if (error.message !== '登录已过期' && isProductionMode()) {
                this.showError(error.message);
            }
            throw error;
        }
    }

    /**
     * GET 下载二进制（如 Excel）
     */
    async getBlob(urlPath) {
        const rawRole = (localStorage.getItem('userRole') || '').toLowerCase();
        const normalizedRole = rawRole === 'factory' ? 'admin' : (rawRole === 'user' ? 'customer' : rawRole);
        const currentUserId = (localStorage.getItem('currentUserId') || '').trim();
        const currentUsername = (localStorage.getItem('currentUsername') || '').trim();
        const encodedUsername = currentUsername ? encodeURIComponent(currentUsername) : '';
        const token = localStorage.getItem(getStorageKey('token')) || this.token;
        const headers = {
            ...(normalizedRole ? { 'X-User-Role': normalizedRole } : {}),
            ...(currentUserId ? { 'X-User-Id': currentUserId } : {}),
            ...(encodedUsername ? { 'X-Username': encodedUsername } : {}),
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        const fullUrl = `${this.baseUrl}${urlPath}`;
        this.showLoading();
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            const response = await fetch(fullUrl, {
                method: 'GET',
                headers,
                signal: controller.signal,
            });
            clearTimeout(timeoutId);
            if (!response.ok) {
                let errMsg = '下载失败';
                const text = await response.text();
                try {
                    const j = JSON.parse(text);
                    errMsg = j.detail || j.message || errMsg;
                    if (Array.isArray(errMsg)) {
                        errMsg = errMsg.map(function(e) { return e.msg || JSON.stringify(e); }).join('; ');
                    }
                } catch (e) {
                    if (text) errMsg = text.slice(0, 200);
                }
                if (response.status === 401) {
                    this.clearToken();
                    localStorage.removeItem('userRole');
                    localStorage.removeItem('currentUserId');
                    localStorage.removeItem('currentUsername');
                    if (!window.location.pathname.endsWith('login.html')) {
                        alert('登录已过期，请重新登录');
                        window.location.href = 'login.html';
                    }
                    throw new Error('登录已过期');
                }
                throw new Error(typeof errMsg === 'string' ? errMsg : JSON.stringify(errMsg));
            }
            const blob = await response.blob();
            const sig = new Uint8Array(await blob.slice(0, 4).arrayBuffer());
            const looksLikeZip =
                sig.length >= 2 && sig[0] === 0x50 && sig[1] === 0x4b;
            if (!looksLikeZip) {
                throw new Error('下载内容不是有效的 Excel（可能未登录或接口返回了错误页），请重新登录后重试');
            }
            const dispo = response.headers.get('Content-Disposition') || '';
            const parsed = parseContentDispositionFilename(dispo);
            let filename = parsed || 'download.xlsx';
            var hdrVer = response.headers.get('X-PM-Export-Version');
            var fnVer = /_config_v(\d+)\.xlsx$/i.exec(filename);
            var exportVersion = hdrVer || (fnVer ? fnVer[1] : null);
            return { blob, filename, exportVersion };
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('请求超时，请检查网络连接');
            }
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    /**
     * POST multipart（上传文件）
     */
    async postMultipart(urlPath, formData) {
        const rawRole = (localStorage.getItem('userRole') || '').toLowerCase();
        const normalizedRole = rawRole === 'factory' ? 'admin' : (rawRole === 'user' ? 'customer' : rawRole);
        const currentUserId = (localStorage.getItem('currentUserId') || '').trim();
        const currentUsername = (localStorage.getItem('currentUsername') || '').trim();
        const encodedUsername = currentUsername ? encodeURIComponent(currentUsername) : '';
        const token = localStorage.getItem(getStorageKey('token')) || this.token;
        const headers = {
            ...(normalizedRole ? { 'X-User-Role': normalizedRole } : {}),
            ...(currentUserId ? { 'X-User-Id': currentUserId } : {}),
            ...(encodedUsername ? { 'X-Username': encodedUsername } : {}),
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        const fullUrl = `${this.baseUrl}${urlPath}`;
        this.showLoading();
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            const response = await fetch(fullUrl, {
                method: 'POST',
                headers,
                body: formData,
                signal: controller.signal,
            });
            clearTimeout(timeoutId);
            let result;
            try {
                result = await response.json();
            } catch (e) {
                result = { detail: '服务器返回非 JSON' };
            }
            if (!response.ok) {
                if (response.status === 401) {
                    this.clearToken();
                    localStorage.removeItem('userRole');
                    localStorage.removeItem('currentUserId');
                    localStorage.removeItem('currentUsername');
                    if (!window.location.pathname.endsWith('login.html')) {
                        alert('登录已过期，请重新登录');
                        window.location.href = 'login.html';
                    }
                    throw new Error('登录已过期');
                }
                let errMsg = result.detail || result.message || '请求失败';
                if (Array.isArray(errMsg)) {
                    errMsg = errMsg.map(function(e) { return e.msg || JSON.stringify(e); }).join('; ');
                }
                throw new Error(errMsg);
            }
            return result;
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('请求超时，请检查网络连接');
            }
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    /**
     * GET请求
     */
    async get(url, params = null) {
        return this.request('GET', url, params);
    }

    /**
     * POST请求
     */
    async post(url, data) {
        return this.request('POST', url, data);
    }

    /**
     * PUT请求
     */
    async put(url, data) {
        return this.request('PUT', url, data);
    }

    /**
     * DELETE请求
     */
    async delete(url) {
        return this.request('DELETE', url);
    }

    /**
     * PATCH请求
     */
    async patch(url, data) {
        return this.request('PATCH', url, data);
    }

    /**
     * 显示加载状态
     */
    showLoading() {
        // 检查是否已存在loading元素
        if (document.getElementById('api-loading')) return;

        const loading = document.createElement('div');
        loading.id = 'api-loading';
        loading.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        loading.innerHTML = `
            <div style="
                background: white;
                padding: 24px 40px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                gap: 16px;
            ">
                <div class="spinner"></div>
                <span style="font-size: 16px; color: #333;">加载中...</span>
            </div>
        `;
        document.body.appendChild(loading);
    }

    /**
     * 隐藏加载状态
     */
    hideLoading() {
        const loading = document.getElementById('api-loading');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * 显示错误提示
     */
    showError(message) {
        // 检查是否已存在错误提示
        const existingError = document.getElementById('api-error');
        if (existingError) {
            existingError.remove();
        }

        const error = document.createElement('div');
        error.id = 'api-error';
        error.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff4d4f;
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;
        error.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">⚠️</span>
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 4px;">操作失败</div>
                    <div style="font-size: 14px; opacity: 0.9;">${message}</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 0;
                    line-height: 1;
                ">×</button>
            </div>
        `;
        document.body.appendChild(error);

        // 3秒后自动消失
        setTimeout(() => {
            if (error.parentElement) {
                error.remove();
            }
        }, 3000);
    }

    /**
     * 显示成功提示
     */
    showSuccess(message) {
        const success = document.createElement('div');
        success.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #52c41a;
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        success.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">✓</span>
                <div style="font-size: 14px;">${message}</div>
            </div>
        `;
        document.body.appendChild(success);

        // 2秒后自动消失
        setTimeout(() => {
            if (success.parentElement) {
                success.remove();
            }
        }, 2000);
    }

    /**
     * 设置认证token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem(getStorageKey('token'), token);
    }

    /**
     * 清除认证token
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem(getStorageKey('token'));
    }
}

// ============================================
// 业务API封装
// ============================================

class ProjectAPI extends ApiClient {
    /**
     * 获取项目列表
     */
    async getProjects(params = {}) {
        return this.get('/projects/', params);
    }

    /**
     * 获取项目详情
     */
    async getProject(id) {
        return this.get(`/projects/${id}`);
    }

    /**
     * 创建项目
     */
    async createProject(data) {
        return this.post('/projects/', data);
    }

    /**
     * 获取历史收件信息
     */
    async getContactProfiles(params = {}) {
        return this.get('/projects/contacts', params);
    }

    /**
     * 获取最终用户-业务类型配置
     */
    async getBusinessOptions(params = {}) {
        return this.get('/projects/business-options', params);
    }

    /**
     * 新增最终用户-业务类型配置（管理员）
     */
    async createBusinessOption(data, role = 'customer') {
        return this.request('POST', '/projects/business-options', data, {
            headers: {
                'X-User-Role': role
            }
        });
    }

    /**
     * 更新最终用户-业务类型配置（管理员）
     */
    async updateBusinessOption(id, data, role = 'customer') {
        return this.request('PUT', `/projects/business-options/${id}`, data, {
            headers: {
                'X-User-Role': role
            }
        });
    }

    /**
     * 删除最终用户-业务类型配置（管理员）
     */
    async deleteBusinessOption(id, role = 'customer') {
        return this.request('DELETE', `/projects/business-options/${id}`, null, {
            headers: {
                'X-User-Role': role
            }
        });
    }

    /**
     * 批量创建最终用户-业务类型配置
     */
    async batchCreateBusinessOptions(items) {
        return this.post('/projects/business-options/batch', items);
    }

    /**
     * 更新项目
     */
    async updateProject(id, data) {
        return this.put(`/projects/${id}`, data);
    }

    /**
     * 删除项目
     */
    async deleteProject(id) {
        return this.delete(`/projects/${id}`);
    }

    /**
     * 复制项目（请求体须含 new_project_name；兼容旧版仅传 name）
     */
    async copyProject(id, data) {
        const payload = Object.assign({}, data);
        if (payload.new_project_name == null && payload.name != null) {
            payload.new_project_name = payload.name;
            delete payload.name;
        }
        if (payload.copy_cold_rooms === undefined) {
            payload.copy_cold_rooms = true;
        }
        if (payload.copy_devices === undefined) {
            payload.copy_devices = false;
        }
        return this.post(`/projects/${id}/copy`, payload);
    }

    /** 导出项目配置 Excel */
    async exportProjectConfigXlsx(projectId) {
        return this.getBlob(`/projects/${projectId}/export-config-xlsx?t=${Date.now()}`);
    }

    /** 将 Excel 合并写入项目数据库（多表模板） */
    async importProjectConfigXlsx(projectId, file) {
        const fd = new FormData();
        fd.append('file', file);
        return this.postMultipart(`/projects/${projectId}/import-config-xlsx`, fd);
    }

    /** 上传项目配置 Excel 附件（仅保存文件，可下载） */
    async uploadProjectConfigAttachment(projectId, file) {
        const fd = new FormData();
        fd.append('file', file);
        return this.postMultipart(`/projects/${projectId}/config-attachment`, fd);
    }

    /** 下载已上传的配置 Excel 附件 */
    async downloadProjectConfigAttachment(projectId) {
        return this.getBlob(`/projects/${projectId}/config-attachment`);
    }

    /** 解析已上传附件为 JSON（不写库） */
    async getProjectConfigAttachmentPreview(projectId) {
        return this.get(`/projects/${projectId}/config-attachment/preview`);
    }

    /** 删除已上传的配置附件 */
    async deleteProjectConfigAttachment(projectId) {
        return this.delete(`/projects/${projectId}/config-attachment`);
    }

    /**
     * 获取项目下的冷库列表
     */
    async getColdRooms(projectId) {
        return this.get(`/projects/${projectId}/cold-rooms`);
    }

    /**
     * 创建冷库
     */
    async createColdRoom(projectId, data) {
        return this.post(`/projects/${projectId}/cold-rooms`, data);
    }

    async updateColdRoom(projectId, coldRoomId, data) {
        return this.put(`/projects/${projectId}/cold-rooms/${coldRoomId}`, data);
    }

    /**
     * 批量创建冷库
     */
    async batchCreateColdRooms(projectId, dataList) {
        return this.post(`/projects/${projectId}/cold-rooms/batch`, { cold_rooms: dataList });
    }
}

class DeviceAPI extends ApiClient {
    /**
     * 获取设备列表
     */
    async getDevices(params = {}) {
        return this.get('/devices/', params);
    }

    /**
     * 获取设备详情
     */
    async getDevice(id) {
        return this.get(`/devices/${id}`);
    }

    /**
     * 创建设备
     */
    async createDevice(projectId, data) {
        return this.post(`/devices/?project_id=${projectId}`, data);
    }

    /**
     * 更新设备
     */
    async updateDevice(id, data) {
        return this.put(`/devices/${id}`, data);
    }

    /**
     * 删除设备
     */
    async deleteDevice(id) {
        return this.delete(`/devices/${id}`);
    }

    /**
     * 复制设备
     */
    async copyDevice(id, data) {
        return this.post(`/devices/${id}/copy`, data);
    }

    /**
     * 获取设备统计
     */
    async getDeviceStats(projectId) {
        return this.get(`/devices/stats/${projectId}`);
    }

    /**
     * 获取设备关系列表
     */
    async getRelations(params = {}) {
        return this.get('/devices/relations', params);
    }

    /**
     * 创建设备关系
     */
    async createRelation(data) {
        return this.post('/devices/relations', data);
    }

    /**
     * 删除设备关系
     */
    async deleteRelation(id) {
        return this.delete(`/devices/relations/${id}`);
    }
}

class EquipmentAPI extends ApiClient {
    /**
     * 获取设备类型列表
     */
    async getCategories(params = {}) {
        return this.get('/equipment-library/categories', params);
    }

    /**
     * 获取品牌列表
     */
    async getBrands(params = {}) {
        return this.get('/equipment-library/brands', params);
    }

    /**
     * 创建品牌
     */
    async createBrand(data) {
        return this.post('/equipment-library/brands', data);
    }

    /**
     * 更新品牌
     */
    async updateBrand(id, data) {
        return this.put(`/equipment-library/brands/${id}`, data);
    }

    /**
     * 删除品牌
     */
    async deleteBrand(id) {
        return this.delete(`/equipment-library/brands/${id}`);
    }

    /**
     * 获取型号列表
     */
    async getModels(params = {}) {
        return this.get('/equipment-library/models', params);
    }

    /**
     * 创建型号
     */
    async createModel(data) {
        return this.post('/equipment-library/models', data);
    }

    /**
     * 更新型号
     */
    async updateModel(id, data) {
        return this.put(`/equipment-library/models/${id}`, data);
    }

    /**
     * 删除型号
     */
    async deleteModel(id) {
        return this.delete(`/equipment-library/models/${id}`);
    }

    async batchCreateCategories(items) {
        return this.post('/equipment-library/categories/batch', items);
    }

    async batchCreateBrands(items) {
        return this.post('/equipment-library/brands/batch', items);
    }

    async batchCreateModels(items) {
        return this.post('/equipment-library/models/batch', items);
    }
}

class GatewayAPI extends ApiClient {
    /**
     * 获取网关列表
     */
    async getGateways(params = {}) {
        return this.get('/gateways/', params);
    }

    /**
     * 获取网关详情
     */
    async getGateway(id) {
        return this.get(`/gateways/${id}`);
    }

    /**
     * 创建网关
     */
    async createGateway(data) {
        return this.post('/gateways', data);
    }

    /**
     * 更新网关
     */
    async updateGateway(id, data) {
        return this.put(`/gateways/${id}`, data);
    }

    /**
     * 删除网关
     */
    async deleteGateway(id) {
        return this.delete(`/gateways/${id}`);
    }

    /**
     * 配置通讯（COM口）
     */
    async configCommunication(gatewayId, data) {
        return this.post(`/gateways/${gatewayId}/communication`, data);
    }

    /**
     * 获取通讯配置
     */
    async getCommunicationConfig(gatewayId) {
        return this.get(`/gateways/${gatewayId}/communication`);
    }
}

class UserAPI extends ApiClient {
    async getUsers(role) {
        return this.get('/users/');
    }

    async createUser(data, role) {
        return this.post('/users/', data);
    }

    async updateUser(id, data, role) {
        return this.put(`/users/${id}`, data);
    }

    async deleteUser(id, role) {
        return this.delete(`/users/${id}`);
    }
}

// ============================================
// 创建全局API实例
// ============================================

const api = {
    projects: new ProjectAPI(),
    devices: new DeviceAPI(),
    equipment: new EquipmentAPI(),
    gateways: new GatewayAPI(),
    users: new UserAPI()
};

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .spinner {
        width: 24px;
        height: 24px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #1890ff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

class MailingAPI extends ApiClient {
    async getRecords(projectId) {
        return this.get(`/gateways/mailing`, { project_id: projectId });
    }

    async getRecord(id) {
        return this.get(`/gateways/mailing/${id}`);
    }

    async createRecord(projectId, data) {
        return this.post(`/gateways/mailing?project_id=${projectId}`, data);
    }

    async updateRecord(id, data) {
        return this.put(`/gateways/mailing/${id}`, data);
    }

    async deleteRecord(id) {
        return this.delete(`/gateways/mailing/${id}`);
    }
}

class FlowAPI extends ApiClient {
    async getFlows(projectId) {
        return this.get(`/gateways/flows`, { project_id: projectId });
    }

    async initFlows(projectId) {
        return this.post(`/gateways/flows/init?project_id=${projectId}`, {});
    }

    async completeStep(recordId, remarks) {
        const url = remarks
            ? `/gateways/flows/${recordId}/complete?remarks=${encodeURIComponent(remarks)}`
            : `/gateways/flows/${recordId}/complete`;
        return this.post(url, {});
    }
}

class GatewayLibraryAPI extends ApiClient {
    async getModels(params = {}) {
        return this.get('/gateway-library/models', params);
    }
    async createModel(data) {
        return this.post('/gateway-library/models', data);
    }
    async updateModel(id, data) {
        return this.put(`/gateway-library/models/${id}`, data);
    }
    async deleteModel(id) {
        return this.delete(`/gateway-library/models/${id}`);
    }
    async getInventory(params = {}) {
        return this.get('/gateway-library/inventory', params);
    }
    async getAvailableInventory(params = {}) {
        return this.get('/gateway-library/inventory/available', params);
    }
    async createInventory(data) {
        return this.post('/gateway-library/inventory', data);
    }
    async updateInventory(id, data) {
        return this.put(`/gateway-library/inventory/${id}`, data);
    }
    async deleteInventory(id) {
        return this.delete(`/gateway-library/inventory/${id}`);
    }
    async allocateToProject(itemId, projectId) {
        return this.post(`/gateway-library/inventory/${itemId}/allocate?project_id=${projectId}`, {});
    }
    async releaseFromProject(itemId) {
        return this.post(`/gateway-library/inventory/${itemId}/release`, {});
    }
}

Object.assign(api, {
    mailing: new MailingAPI(),
    flows: new FlowAPI(),
    gatewayLibrary: new GatewayLibraryAPI(),
});

/**
 * 全局登录状态检查
 * 在非登录页面调用，未登录时自动跳转
 */
function requireAuth() {
    const token = localStorage.getItem(getStorageKey('token'));
    const username = localStorage.getItem('currentUsername');
    const isLoginPage = window.location.pathname.endsWith('login.html');
    const isIndexPage = window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/');
    if (!token && !username && !isLoginPage && !isIndexPage) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/**
 * 获取当前用户角色
 */
function getCurrentRole() {
    const raw = (localStorage.getItem('userRole') || '').toLowerCase();
    if (raw === 'factory') return 'admin';
    if (raw === 'user') return 'customer';
    return raw || 'customer';
}

/**
 * 判断当前用户是否为管理员
 */
function isAdmin() {
    return getCurrentRole() === 'admin';
}

// 导出（如果需要）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { api, ApiClient, ProjectAPI, DeviceAPI, EquipmentAPI, GatewayAPI, UserAPI, MailingAPI, FlowAPI };
}
