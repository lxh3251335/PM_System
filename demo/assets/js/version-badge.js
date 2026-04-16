/**
 * 前端版本标签
 * ------------------------------------------------------------
 * 作用：在页面右下角显示当前前端版本号，便于运维确认部署是否生效。
 * 用法：在页面 <head> 中引入即可：
 *   <script src="assets/js/version-badge.js?v=20260418c"></script>
 * 更新版本：改下面的 APP_VERSION 常量 + 引入时的 ?v= 参数即可。
 */
(function () {
    'use strict';

    // 单一版本源 —— 与 api.js?v= 保持一致
    var APP_VERSION = '20260418c';
    var BUILD_DATE = '2026-04-18';
    var FEATURE_NOTE = '批量修改 / 数据同步修复';

    // 允许通过 URL 参数 ?nover=1 隐藏（方便截图）
    try {
        if (/[?&]nover=1/.test(location.search)) return;
    } catch (e) { /* noop */ }

    window.APP_VERSION = APP_VERSION;

    function mount() {
        if (document.getElementById('app-version-badge')) return;

        var badge = document.createElement('div');
        badge.id = 'app-version-badge';
        badge.setAttribute('role', 'status');
        badge.title = '版本: v' + APP_VERSION + '\n构建: ' + BUILD_DATE + '\n' + FEATURE_NOTE +
            '\n\n点击复制，双击隐藏';
        badge.textContent = 'v' + APP_VERSION;

        var css = [
            'position:fixed',
            'right:12px',
            'bottom:12px',
            'z-index:9999',
            'padding:4px 10px',
            'font:12px/1.4 -apple-system,"Segoe UI",Roboto,"Microsoft YaHei",sans-serif',
            'color:#fff',
            'background:rgba(23,43,77,0.78)',
            'border:1px solid rgba(255,255,255,0.15)',
            'border-radius:12px',
            'box-shadow:0 2px 6px rgba(0,0,0,0.2)',
            'cursor:pointer',
            'user-select:none',
            'transition:opacity .2s'
        ].join(';');
        badge.style.cssText = css;

        badge.addEventListener('mouseenter', function () { badge.style.opacity = '1'; });
        badge.addEventListener('mouseleave', function () { badge.style.opacity = '0.75'; });
        badge.style.opacity = '0.75';

        // 单击：复制版本号到剪贴板
        badge.addEventListener('click', function () {
            var txt = 'v' + APP_VERSION + ' (' + BUILD_DATE + ')';
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(txt);
                }
            } catch (e) { /* noop */ }
            var orig = badge.textContent;
            badge.textContent = '已复制';
            setTimeout(function () { badge.textContent = orig; }, 900);
        });

        // 双击：当前会话内隐藏
        badge.addEventListener('dblclick', function () {
            badge.style.display = 'none';
        });

        document.body.appendChild(badge);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mount);
    } else {
        mount();
    }
})();
