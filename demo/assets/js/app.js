// ========== 通用功能 ==========

// 侧边栏收缩功能
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const icon = document.getElementById('collapseIcon');
    
    sidebar.classList.toggle('collapsed');
    
    if (sidebar.classList.contains('collapsed')) {
        sidebar.style.width = '60px';
        if (icon) icon.textContent = '▶';
        // 隐藏文字
        document.querySelectorAll('.sidebar .brand-name, .sidebar .nav-item span:not(.nav-icon)').forEach(el => {
            el.style.display = 'none';
        });
    } else {
        sidebar.style.width = '240px';
        if (icon) icon.textContent = '◀';
        // 显示文字
        document.querySelectorAll('.sidebar .brand-name, .sidebar .nav-item span:not(.nav-icon)').forEach(el => {
            el.style.display = '';
        });
    }
}

// 显示设备统计弹窗
function showDeviceStats(event, id) {
    event.stopPropagation();
    
    // 隐藏所有其他弹窗
    document.querySelectorAll('.device-stats-tooltip').forEach(el => {
        el.classList.remove('show');
    });
    
    const tooltip = document.getElementById(id);
    if (tooltip) {
        tooltip.classList.toggle('show');
        
        // 定位弹窗
        const icon = event.target;
        const rect = icon.getBoundingClientRect();
        tooltip.style.position = 'fixed';
        tooltip.style.left = (rect.left - 120) + 'px';
        tooltip.style.top = (rect.top + 30) + 'px';
    }
}

// 切换操作菜单
function toggleActionMenu(event, menuId) {
    event.stopPropagation();
    
    // 隐藏所有其他菜单
    document.querySelectorAll('.action-menu').forEach(menu => {
        if (menu.id !== menuId) {
            menu.classList.remove('show');
        }
    });
    
    const menu = document.getElementById(menuId);
    if (menu) {
        menu.classList.toggle('show');
    }
}

// 点击页面其他地方关闭所有弹窗和菜单
document.addEventListener('click', () => {
    document.querySelectorAll('.device-stats-tooltip, .action-menu').forEach(el => {
        el.classList.remove('show');
    });
});

// Tab切换功能
function switchTab(index) {
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));
    
    if (tabs[index]) tabs[index].classList.add('active');
    if (contents[index]) contents[index].classList.add('active');
}
