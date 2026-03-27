/**
 * 步骤导航组件（两阶段模型）
 * 客户阶段：步骤1-5（创建项目 ~ 提交审核）
 * 管理员阶段：步骤6-9（网关配置 ~ 完成）
 */

const STEP_PAGES = [
    { step: 1, title: '创建项目', page: 'project-create.html', phase: 'customer' },
    { step: 2, title: '创建冷库', page: 'cold-room-create.html', phase: 'customer' },
    { step: 3, title: '登记设备', page: 'device-register.html', phase: 'customer' },
    { step: 4, title: '设备关系', page: 'device-bindline.html', phase: 'customer' },
    { step: 5, title: '提交审核', page: 'project-complete.html?mode=submit', phase: 'customer' },
    { step: 6, title: '网关配置', page: 'gateway-setup.html', phase: 'admin' },
    { step: 7, title: '通讯设置', page: 'communication-setup.html', phase: 'admin' },
    { step: 8, title: '发货登记', page: 'shipping-register.html', phase: 'admin' },
    { step: 9, title: '完成', page: 'project-complete.html?mode=complete', phase: 'admin' }
];

function _getStepNavRole() {
    var raw = (localStorage.getItem('userRole') || 'customer').toLowerCase();
    if (raw === 'factory') return 'admin';
    if (raw === 'user') return 'customer';
    return raw;
}

function renderStepNav(currentStep) {
    var projectId = localStorage.getItem('currentProjectId');
    var container = document.querySelector('.steps');
    if (!container) return;

    var role = _getStepNavRole();
    var visibleSteps = STEP_PAGES.filter(function(s) {
        return role === 'admin' ? s.phase === 'admin' : s.phase === 'customer';
    });

    container.innerHTML = visibleSteps.map(function(s) {
        var cls = '';
        if (s.step < currentStep) cls = 'completed clickable';
        else if (s.step === currentStep) cls = 'active';
        else if (projectId) cls = 'clickable';

        var canClick = projectId ? (s.step !== currentStep) : (s.step < currentStep);
        var numberContent = s.step < currentStep ? '&#10003;' : (s.step <= 5 ? s.step : s.step - 5);

        return '<div class="step ' + cls + '" ' + (canClick ? 'onclick="goToStep(' + s.step + ')"' : '') + '>' +
            '<div class="step-number">' + numberContent + '</div>' +
            '<div class="step-title">' + s.title + '</div>' +
            '</div>';
    }).join('');
}

function goToStep(step) {
    var target = STEP_PAGES.find(function(s) { return s.step === step; });
    if (!target) return;

    var url = target.page;
    if (step === 1) {
        var pid = localStorage.getItem('currentProjectId');
        if (pid) url = 'project-create.html?id=' + pid;
    }
    window.location.href = url;
}
