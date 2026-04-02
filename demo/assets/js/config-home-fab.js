/**
 * 一键返回「项目管理 - 项目列表」（project-list.html）
 * 有 .top-bar + .user-menu 时在顶栏插入链接；否则右上角固定按钮。
 * 请在 nav.js 之后引入（若页面有 nav.js）。
 */
(function () {
    var file = (window.location.pathname.split('/').pop() || '').toLowerCase();
    if (file === 'project-list.html') return;
    if (document.getElementById('configHomeEntry')) return;

    if (!document.querySelector('link[href*="app.css"]')) {
        var fallback = document.createElement('style');
        fallback.textContent =
            '.config-home-fab{position:fixed;top:14px;right:16px;z-index:9998;padding:8px 18px;font-size:14px;font-weight:500;color:#fff!important;background:#1890ff;border-radius:6px;text-decoration:none!important;box-shadow:0 2px 10px rgba(0,0,0,.12);}' +
            '.config-home-fab:hover{background:#096dd9;color:#fff!important;}' +
            '.config-home-link{font-size:14px;color:#1890ff!important;text-decoration:none!important;font-weight:500;white-space:nowrap;}' +
            '.config-home-link:hover{text-decoration:underline!important;color:#096dd9!important;}';
        document.head.appendChild(fallback);
    }

    var link = document.createElement('a');
    link.id = 'configHomeEntry';
    link.href = 'project-list.html';
    link.title = '返回项目管理 - 项目列表';
    link.textContent = '返回项目列表';

    var userMenu = document.querySelector('.user-menu');
    var topBar = document.querySelector('.top-bar');

    if (userMenu && topBar) {
        link.className = 'config-home-link';
        userMenu.insertBefore(link, userMenu.firstChild);
        var sep = document.createElement('span');
        sep.className = 'config-home-sep';
        sep.setAttribute('aria-hidden', 'true');
        sep.textContent = '|';
        sep.style.cssText = 'color:#d9d9d9;margin:0 6px 0 2px;font-size:12px;user-select:none;';
        var next = link.nextSibling;
        if (next) {
            userMenu.insertBefore(sep, next);
        } else {
            userMenu.appendChild(sep);
        }
    } else {
        link.className = 'config-home-fab';
        document.body.appendChild(link);
    }
})();
