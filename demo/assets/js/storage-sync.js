/**
 * localStorage 缓存管理
 * 在生产模式下，localStorage 仅用作 API 的降级缓存。
 * 此模块提供清理和同步逻辑。
 */

/**
 * 清理所有业务数据缓存（不清理认证信息）
 */
function clearBusinessDataCache() {
    const keysToKeep = new Set([
        getStorageKey('token'),
        'userRole',
        'currentUserId',
        'currentUsername',
        'currentProjectId',
        'currentProject',
    ]);

    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (!keysToKeep.has(key)) {
            keysToRemove.push(key);
        }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key));
    console.log('[StorageSync] 已清理 ' + keysToRemove.length + ' 个缓存项');
}

/**
 * 将 API 数据同步到 localStorage 缓存（用于离线降级）
 */
async function syncProjectDataToCache(projectId) {
    if (!projectId || !isProductionMode()) return;

    try {
        const [coldRooms, devices, gateways] = await Promise.all([
            api.projects.getColdRooms(projectId).catch(() => null),
            api.devices.getDevices({ project_id: projectId }).catch(() => null),
            api.gateways.getGateways({ project_id: projectId }).catch(() => null),
        ]);

        if (coldRooms) {
            const existing = JSON.parse(localStorage.getItem('coldRooms') || '[]');
            const others = existing.filter(r => String(r.project_id) !== String(projectId));
            localStorage.setItem('coldRooms', JSON.stringify([...others, ...coldRooms]));
        }
        if (devices) {
            localStorage.setItem('devices_' + projectId, JSON.stringify(devices));
        }
        if (gateways) {
            localStorage.setItem('gateways_' + projectId, JSON.stringify(gateways));
        }
        console.log('[StorageSync] 项目 ' + projectId + ' 数据已同步到缓存');
    } catch (e) {
        console.warn('[StorageSync] 同步缓存失败:', e.message);
    }
}
