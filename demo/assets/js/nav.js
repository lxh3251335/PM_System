/**
 * 全局导航和权限管理
 * 在所有页面（除 login.html / index.html）引入此文件
 */
(function () {
    function initNav() {
        // 登录检查
        if (typeof requireAuth === 'function') {
            requireAuth();
        }

        // 构建侧边栏导航（如果页面有 #sidebar 容器）
        const sidebar = document.getElementById('sidebar');
        if (sidebar && !sidebar.querySelector('.sidebar-header')) {
            renderSidebar(sidebar);
        }

        // 顶栏用户信息（如果页面有 .user-menu 或 #userMenu）
        renderUserMenu();
    }

    // 确保 DOM 加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNav);
    } else {
        initNav();
    }

    function renderSidebar(container) {
        var role = 'customer';
        try {
            if (typeof getCurrentRole === 'function') {
                role = getCurrentRole();
            }
        } catch (e) {
            console.warn('nav.js: getCurrentRole error', e);
        }
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';

        // 分组导航菜单配置
        var navGroups = [
            {
                title: '项目配置',
                roles: ['admin', 'customer'],
                items: [
                    { href: 'project-list.html', icon: '📋', label: '项目管理', roles: ['admin', 'customer'] },
                    { href: 'shipping-register.html', icon: '📦', label: '发货登记', roles: ['admin'] }
                ]
            },
            {
                title: '后台管理',
                roles: ['admin'],
                items: [
                    { href: 'equipment-config.html', icon: '🧩', label: '设备配置管理', roles: ['admin'] },
                    { href: 'business-options.html', icon: '⚙️', label: '业务类型配置', roles: ['admin'] },
                    { href: 'gateway-inventory.html', icon: '🗄️', label: '网关库存', roles: ['admin'] },
                    { href: 'user-management.html', icon: '👥', label: '用户管理', roles: ['admin'] }
                ]
            }
        ];

        var navHtml = '';
        navGroups.forEach(function(group) {
            if (!group.roles.includes(role)) return;
            var visibleItems = group.items.filter(function(item) { return item.roles.includes(role); });
            if (visibleItems.length === 0) return;

            navHtml += '<div class="nav-group-label">' + group.title + '</div>';
            visibleItems.forEach(function(item) {
                var active = currentPage === item.href ? ' active' : '';
                navHtml += '<a href="' + item.href + '" class="nav-item' + active + '">' +
                    '<span class="nav-icon">' + item.icon + '</span>' +
                    '<span>' + item.label + '</span>' +
                    '</a>';
            });
        });

        // 底部固定：返回项目列表
        navHtml += '<a href="project-list.html" class="nav-item" style="margin-top:auto;">' +
            '<span class="nav-icon">←</span>' +
            '<span>返回项目列表</span>' +
            '</a>';

        container.innerHTML =
            '<div class="sidebar-header">' +
            '    <div class="logo">📦</div>' +
            '    <span class="brand-name">冷库项目信息管理系统</span>' +
            '</div>' +
            '<nav class="sidebar-nav">' +
            navHtml +
            '</nav>' +
            '<div class="sidebar-footer" style="padding:12px 16px;font-size:11px;color:rgba(255,255,255,0.4);border-top:1px solid rgba(255,255,255,0.1);text-align:center;line-height:1.6;">' +
            '    V1.0.0<br>&copy; 天津天商酷凌科技有限公司' +
            '</div>';
    }

    function renderUserMenu() {
        const menuEl = document.querySelector('.user-menu') || document.getElementById('userMenu');
        if (!menuEl) return;

        const username = localStorage.getItem('currentUsername') || '未登录';
        var role = 'customer';
        try {
            if (typeof getCurrentRole === 'function') {
                role = getCurrentRole();
            }
        } catch (e) {}
        const roleLabel = role === 'admin' ? '管理员' : '客户';

        const logoutBtn = '<button class="btn-logout" onclick="doLogout()" style="margin-left:12px;">退出登录</button>';
        menuEl.innerHTML =
            '<span style="font-size:14px; color:var(--text-secondary);">' +
            username + ' (' + roleLabel + ')' +
            '</span>' + logoutBtn;
    }
})();


function doLogout() {
    localStorage.removeItem(getStorageKey('token'));
    localStorage.removeItem('userRole');
    localStorage.removeItem('currentUserId');
    localStorage.removeItem('currentUsername');
    window.location.href = 'login.html';
}
