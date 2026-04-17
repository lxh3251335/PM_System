# -*- coding: utf-8 -*-
"""
修复 cb2742b 编码回归：
  - 19 个损坏 HTML 文件从 988a20b 恢复为干净 UTF-8
  - 补回 cb2742b 里两项真实业务改动（冷柜类型、类型别名）
  - 统一 api.js 版本号为 v=20260418c
  - 核心页面插入 version-badge.js 脚本

运行方式：
  python backend/scripts/fix_encoding_regression.py
"""
from pathlib import Path
import subprocess
import re

GOOD_COMMIT = '988a20b'
NEW_API_VER = '20260418c'
BADGE_SCRIPT_TAG = '<script src="assets/js/version-badge.js?v=20260418c"></script>'

# 19 个需要从 988a20b 恢复的 HTML
DAMAGED = [
    # 类型 A（整体 GBK 损坏）
    'business-options.html', 'cold-room-create.html', 'communication-setup.html',
    'device-bindline.html', 'device-management.html', 'device-relations.html',
    'equipment-config.html', 'gateway-config.html', 'gateway-setup.html',
    'project-complete.html', 'shipping-register.html', 'user-management.html',
    # 类型 B（UTF-8 中 mojibake）
    'demo-guide.html', 'index.html', 'init-device-register.html',
    'login.html', 'project-create.html',
    'set-demo-admin.html', 'set-demo-user.html',
]

# 需要插入 version-badge.js 的核心页面（与已部署的 11 核心页对齐）
CORE_PAGES_WITH_BADGE = {
    'login.html', 'index.html', 'project-create.html', 'device-management.html',
    'gateway-setup.html', 'equipment-config.html', 'communication-setup.html',
}

DEMO_DIR = Path('demo')


def git_show(ref: str, path: str) -> bytes:
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], stderr=subprocess.PIPE)


def step1_restore_from_good():
    """Step 1: 从 988a20b 恢复所有损坏文件为纯 UTF-8"""
    print('\n==== Step 1: 从 988a20b 恢复 19 个文件 ====')
    for name in DAMAGED:
        rel = f'demo/{name}'
        data = git_show(GOOD_COMMIT, rel)
        # 验证 UTF-8 可解码
        data.decode('utf-8')
        (DEMO_DIR / name).write_bytes(data)
        print(f'  [OK] {name}  ({len(data)}B)')


def step2_patch_coldroom():
    """Step 2: 为 cold-room-create.html 补回低温冷柜/中温冷柜类型改动"""
    print('\n==== Step 2: 补回 cold-room-create 冷柜类型 ====')
    f = DEMO_DIR / 'cold-room-create.html'
    text = f.read_text(encoding='utf-8')

    # 2.1 下拉选项加入低温/中温冷柜
    sel_old = '<option value="">请选择冷库类型</option>'
    sel_new = '<option value="">请选择冷库/冷柜类型</option>'
    if sel_old not in text:
        raise RuntimeError('找不到原下拉占位选项，无法补丁冷柜类型')
    # 在 "请选择冷库类型" 所在 <select> 末尾添加低/中温冷柜选项
    # 先替换占位文案
    text = text.replace(sel_old, sel_new, 1)

    # 找到"保鲜冷库"选项行，在它后面插入两行（如果还没有）
    fresh_opt = '<option value="fresh_food">保鲜冷库'
    if fresh_opt in text and 'low_temp_cabinet' not in text:
        # 插入点：匹配"请选择冷库/冷柜类型" 后第一处结尾 </select>
        # 更稳妥：在最后一个 <option value="xxx"> 保鲜冷库 的整行尾追加两行
        line_re = re.compile(r'(\s*)(<option value="fresh_food">[^<]+</option>)')
        m = line_re.search(text)
        if m:
            indent = m.group(1)
            ins = (indent + '<option value="low_temp_cabinet">低温冷柜(-18℃~-15℃)</option>'
                   + indent + '<option value="medium_temp_cabinet">中温冷柜(2℃~8℃)</option>')
            text = text[:m.end()] + ins + text[m.end():]
            print('  [OK] 已插入低/中温冷柜 <option>')

    # 2.2 switch-case 分支添加处理
    # 找到现有的 case 'fresh_food': 分支，在其 break 之后插入两段
    case_insert_anchor = "case 'fresh_food':"
    if case_insert_anchor in text and "case 'low_temp_cabinet':" not in text:
        # 定位 fresh_food 分支的结束 break（包含）
        idx = text.find(case_insert_anchor)
        # 向后找第一个 'break;'
        br = text.find('break;', idx)
        if br >= 0:
            insert_pos = br + len('break;')
            block = (
                "\n                case 'low_temp_cabinet':\n"
                "                    tempMinInput.value = -18;\n"
                "                    tempMaxInput.value = -15;\n"
                "                    if (!roomNameInput.value) {\n"
                "                        roomNameInput.value = (roomCount + 1) + '号低温冷柜';\n"
                "                    }\n"
                "                    break;\n"
                "                case 'medium_temp_cabinet':\n"
                "                    tempMinInput.value = 2;\n"
                "                    tempMaxInput.value = 8;\n"
                "                    if (!roomNameInput.value) {\n"
                "                        roomNameInput.value = (roomCount + 1) + '号中温冷柜';\n"
                "                    }\n"
                "                    break;"
            )
            text = text[:insert_pos] + block + text[insert_pos:]
            print('  [OK] 已插入 switch-case 分支')

    # 2.3 id 类型一致性
    text = text.replace(
        'const idx = coldRooms.findIndex(r => r.id === editingRoomId);',
        'const idx = coldRooms.findIndex(r => String(r.id) === String(editingRoomId));'
    )

    f.write_text(text, encoding='utf-8', newline='\n')
    print('  [OK] cold-room-create.html 已更新')


def step3_patch_commset():
    """Step 3: 为 communication-setup.html 补回设备类型别名增强"""
    print('\n==== Step 3: 补回 communication-setup 类型别名 ====')
    f = DEMO_DIR / 'communication-setup.html'
    text = f.read_text(encoding='utf-8')

    # 找到映射字典，添加别名
    # 旧行：'electric_meter': 'meter'（末尾，无逗号或有逗号）
    patterns = [
        ("'electric_meter': 'meter'",
         "'electric_meter': 'meter',\n                'temp_controller': 'thermostat',\n"
         "                'temperature_controller': 'thermostat',\n"
         "                'electric-meter': 'meter',\n"
         "                'power_meter': 'meter',\n"
         "                'refrigeration-unit': 'unit',\n"
         "                'air-cooler': 'air_cooler',\n"
         "                'cooling-tower': 'cooling_tower',\n"
         "                'defrost-controller': 'defrost_controller'"),
    ]
    patched = False
    for old, new in patterns:
        if old in text and 'temp_controller' not in text:
            text = text.replace(old, new, 1)
            patched = True
            print('  [OK] 已追加类型别名')
            break

    if not patched:
        # fallback：没找到目标键或已经打过补丁；给出提示
        if 'temp_controller' in text:
            print('  [SKIP] 类型别名已存在')
        else:
            print('  [WARN] 未找到 electric_meter 锚点，略过')

    f.write_text(text, encoding='utf-8', newline='\n')


def step4_bump_api_version():
    """Step 4: 所有 demo/*.html 的 api.js 版本号统一到 NEW_API_VER"""
    print('\n==== Step 4: 统一 api.js 版本号 ====')
    pat = re.compile(r'<script src="assets/js/api\.js\?v=[\w.\-]+"></script>')
    target = f'<script src="assets/js/api.js?v={NEW_API_VER}"></script>'
    changed = 0
    for f in sorted(DEMO_DIR.glob('*.html')):
        s = f.read_text(encoding='utf-8')
        s2, n = pat.subn(target, s)
        if n > 0 and s2 != s:
            f.write_text(s2, encoding='utf-8', newline='\n')
            changed += 1
            print(f'  [OK] {f.name} ({n} 处)')
    print(f'  共更新 {changed} 个文件')


def step5_insert_badge():
    """Step 5: 在核心页面的 </head> 前插入 version-badge.js 脚本"""
    print('\n==== Step 5: 插入 version-badge.js ====')
    for name in sorted(CORE_PAGES_WITH_BADGE):
        f = DEMO_DIR / name
        if not f.exists():
            print(f'  [MISS] {name} 不存在')
            continue
        text = f.read_text(encoding='utf-8')
        if 'version-badge.js' in text:
            print(f'  [SKIP] {name} 已有徽章')
            continue
        # 优先跟随 api.js 行后插入
        api_line = re.search(r'([ \t]*)<script src="assets/js/api\.js\?v=[\w.\-]+"></script>', text)
        if api_line:
            indent = api_line.group(1)
            insert = f'\n{indent}{BADGE_SCRIPT_TAG}'
            text = text[:api_line.end()] + insert + text[api_line.end():]
        else:
            # 否则在 </head> 前插入
            idx = text.find('</head>')
            if idx < 0:
                print(f'  [WARN] {name} 找不到 </head>')
                continue
            indent = '    '
            text = text[:idx] + indent + BADGE_SCRIPT_TAG + '\n' + text[idx:]
        f.write_text(text, encoding='utf-8', newline='\n')
        print(f'  [OK] {name}')


def step6_verify():
    """Step 6: 验证所有 HTML 是否纯 UTF-8 + 不再包含 ?-mojibake 模式"""
    print('\n==== Step 6: 校验 ====')
    broken_re = re.compile(rb'[\xE0-\xEF][\x80-\xBF]\x3F')
    bad = 0
    for f in sorted(DEMO_DIR.glob('*.html')):
        data = f.read_bytes()
        try:
            data.decode('utf-8')
            utf = 'OK'
        except UnicodeDecodeError as e:
            utf = f'FAIL@{e.start}'
        hits = len(broken_re.findall(data))
        status = 'OK' if utf == 'OK' and hits == 0 else 'BAD'
        if status == 'BAD':
            bad += 1
            print(f'  [{status}] {f.name}  utf8={utf}  mojibake={hits}')
    if bad == 0:
        print('  全部 HTML 通过 UTF-8 + mojibake 校验')
    else:
        print(f'  共 {bad} 个文件仍有问题')


if __name__ == '__main__':
    step1_restore_from_good()
    step2_patch_coldroom()
    step3_patch_commset()
    step4_bump_api_version()
    step5_insert_badge()
    step6_verify()
    print('\n== 修复完成 ==')
