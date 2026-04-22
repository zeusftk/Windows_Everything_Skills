# -*- coding: utf-8 -*-
from ipc_skills_creator import MetaSkillGenerator

modules = {
    "desktop": {
        "apis": [
            {"action": "desktop_mouse_click", "description": "鼠标点击，在指定坐标位置执行鼠标点击操作，支持左键，鼠标移动"},
            {"action": "desktop_keyboard_type", "description": "键盘输入，模拟键盘逐字符输入文本内容"}
        ]
    },
    "web": {
        "apis": [
            {"action": "web_navigate", "description": "导航到指定URL地址，支持等待页面加载"},
            {"action": "web_click", "description": "点击网页元素，支持CSS选择器和XPath"}
        ]
    }
}

result = MetaSkillGenerator._generate_trigger_index(modules)
print(result)
print("\n--- TEST PASSED ---")
