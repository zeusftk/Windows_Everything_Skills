# IPC API 列表（测试通过）

> **版本**: 2.5.0
> **更新日期**: 2026-04-21

&#x20;

***

## API Spec 模块

| Action         | 功能（详细）                                            | 功能触发关键词                             | 输入参数                                        | 输出参数                                                                                   | 测试状态    |
| -------------- | ------------------------------------------------- | ----------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------- | ------- |
| `all_api_spec` | 获取所有 API 规范，用于查询系统中已注册的所有模块及其 API 详细信息，支持按模块和名称过滤 | 所有API、查询API、获取API列表、API规范、查看模块、接口列表 | `module: str`(可选), `action_filter: str`(可选) | `success: bool`, `actions: Dict`, `total_apis: int`, `generated_at: str`, `error: str` | ✅ 02001 |

***

## App Registry 模块

| Action                      | 功能（详细）              | 功能触发关键词              | 输入参数            | 输出参数                                              | 测试状态    |
| --------------------------- | ------------------- | -------------------- | --------------- | ------------------------------------------------- | ------- |
| `registry_app_list`         | 列出应用，返回所有已注册的应用程序列表 | 应用列表、已注册应用、列出应用、应用注册 | 无               | `success: bool`, `apps: List[Dict]`, `error: str` | ✅ 02002 |
| `registry_whitelist_add`    | 添加白名单，将应用添加到白名单中    | 添加白名单、白名单添加、应用白名单    | `app_name: str` | `success: bool`, `added: str`, `error: str`       | ✅ 06001 |
| `registry_whitelist_get`    | 获取白名单，返回应用白名单列表     | 获取白名单、查看白名单、白名单列表    | 无               | `success: bool`, `whitelist: List`, `error: str`  | ✅ 06002 |
| `registry_whitelist_remove` | 移除白名单，从白名单中移除指定应用   | 移除白名单、删除白名单、白名单移除    | `app_name: str` | `success: bool`, `removed: str`, `error: str`     | ✅ 06003 |

***

## Desktop 模块 - 鼠标操作

| Action                 | 功能（详细）                               | 功能触发关键词                               | 输入参数                                                                                                    | 输出参数                          | 测试状态    |
| ---------------------- | ------------------------------------ | ------------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------- | ------- |
| `desktop_mouse_click`  | 鼠标点击，在指定坐标位置执行鼠标点击操作，支持左键/右键/中键及多次点击 | 鼠标点击、点击坐标、点击位置、左键点击、右键点击、中键点击、双击、多次点击 | `x: int`, `y: int`, `button: str`="left", `clicks: int`=1                                               | `success: bool`, `error: str` | ✅ 03023 |
| `desktop_mouse_move`   | 鼠标移动，将鼠标光标平滑移动到指定坐标位置，可设置移动持续时间      | 鼠标移动、移动鼠标、鼠标移到、光标移动                   | `x: int`, `y: int`, `duration: float`=0.0                                                               | `success: bool`, `error: str` | ✅ 03025 |
| `desktop_mouse_drag`   | 鼠标拖拽，从起点坐标拖拽到终点坐标，常用于拖动窗口或选择文本       | 鼠标拖拽、拖拽、拖动、拖放                         | `start_x: int`, `start_y: int`, `end_x: int`, `end_y: int`, `duration: float`=0.5, `button: str`="left" | `success: bool`, `error: str` | ✅ 03022 |
| `desktop_mouse_scroll` | 鼠标滚动，在指定位置或当前位置执行鼠标滚轮滚动操作            | 鼠标滚动、滚轮滚动、滚动页面、向上滚动、向下滚动              | `clicks: int`, `x: int`(可选), `y: int`(可选)                                                               | `success: bool`, `error: str` | ✅ 03021 |

***

## Desktop 模块 - 键盘操作

| Action                    | 功能（详细）                            | 功能触发关键词                | 输入参数                               | 输出参数                          | 测试状态    |
| ------------------------- | --------------------------------- | ---------------------- | ---------------------------------- | ----------------------------- | ------- |
| `desktop_keyboard_type`   | 键盘输入，模拟键盘逐字符输入文本内容，可设置字符间间隔时间     | 键盘输入、输入文本、打字、文字输入、键盘打字 | `text: str`, `interval: float`=0.0 | `success: bool`, `error: str` | ✅ 03020 |
| `desktop_keyboard_press`  | 按键按下，模拟按下并释放单个按键，如 Enter、Escape 等 | 按键、按键按下、按键盘、按下按键       | `key: str`                         | `success: bool`, `error: str` | ✅ 03019 |
| `desktop_keyboard_hotkey` | 快捷键，模拟同时按下多个组合键，如 Ctrl+C、Alt+F4 等 | 快捷键、组合键、热键、同时按键、多键组合   | `keys: List[str]`                  | `success: bool`, `error: str` | ✅ 03010 |

***

## Desktop 模块 - 屏幕操作

| Action                       | 功能（详细）                           | 功能触发关键词             | 输入参数                             | 输出参数                                                       | 测试状态    |
| ---------------------------- | -------------------------------- | ------------------- | -------------------------------- | ---------------------------------------------------------- | ------- |
| `desktop_screenshot`         | 截图，捕获全屏或指定区域的屏幕图像，返回 base64 编码数据 | 截图、屏幕截图、截屏、全屏截图     | `region: Tuple`(可选)              | `success: bool`, `data: str`(base64), `error: str`         | ✅ 03005 |
| `desktop_window_screenshot`  | 窗口截图，根据窗口标题模糊匹配并捕获该窗口的图像         | 窗口截图、窗口截屏、截取窗口、捕获窗口 | `window_title: str`(必填，模糊匹配窗口标题) | `success: bool`, `data: str`(base64), `error: str`         | ✅ 03028 |
| `desktop_get_screen_size`    | 获取屏幕尺寸，返回主显示器的分辨率宽度和高度           | 屏幕尺寸、分辨率、屏幕大小、显示器尺寸 | 无                                | `success: bool`, `width: int`, `height: int`, `error: str` | ✅ 03009 |
| `desktop_get_mouse_position` | 获取鼠标位置，返回当前鼠标光标的屏幕坐标             | 鼠标位置、鼠标坐标、光标位置、获取鼠标 | 无                                | `success: bool`, `x: int`, `y: int`, `error: str`          | ✅ 03024 |

***

## Desktop 模块 - 窗口操作

| Action                     | 功能（详细）                             | 功能触发关键词               | 输入参数                                                       | 输出参数                                                                                                                                          | 测试状态    |
| -------------------------- | ---------------------------------- | --------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `desktop_find_window`      | 查找窗口，根据标题模糊匹配查找一个或多个窗口，返回窗口句柄和位置信息 | 查找窗口、搜索窗口、找窗口、窗口查找    | `title: str` 或 `titles: List[str]`                         | `success: bool`, `count: int`, `windows: List[Dict]`, `error: str`                                                                            | ✅ 03008 |
| `desktop_list_all_windows` | 列出所有窗口，获取系统中所有可见窗口的列表及其属性信息        | 列出窗口、所有窗口、窗口列表、列出所有窗口 | 无                                                          | `success: bool`, `count: int`, `windows: List[Dict]`, `error: str`                                                                            | ✅ 03027 |
| `desktop_find_element`     | 查找元素，在指定窗口中查找包含特定文本的 UI 元素，支持超时等待  | 查找元素、搜索元素、找元素、UI元素    | `window_title: str`(可选), `text: str`(可选), `timeout: int`=5 | `success: bool`, `window_exists: bool`, `window_handle: int`, `window_activated: bool`, `elements: List[Dict]`, `element: Dict`, `error: str` | ✅ 03026 |
| `desktop_launch_app`       | 启动应用，根据应用路径启动指定的应用程序，支持传递命令行参数     | 启动应用、启动程序、打开应用、运行应用   | `app_path: str`, `args: str`(可选)                           | `success: bool`, `error: str`                                                                                                                 | ✅ 03001 |
| `desktop_close_app`        | 关闭应用，根据应用路径关闭指定的应用程序               | 关闭应用、关闭程序、退出应用、杀掉应用   | `app_path: str`                                            | `success: bool`, `error: str`                                                                                                                 | ✅ 03002 |

***

## Desktop 模块 - 剪贴板操作

| Action                  | 功能（详细）              | 功能触发关键词                | 输入参数        | 输出参数                                       | 测试状态    |
| ----------------------- | ------------------- | ---------------------- | ----------- | ------------------------------------------ | ------- |
| `desktop_get_clipboard` | 获取剪贴板，读取系统剪贴板中的文本内容 | 获取剪贴板、读取剪贴板、剪贴板内容、复制内容 | 无           | `success: bool`, `text: str`, `error: str` | ✅ 03007 |
| `desktop_set_clipboard` | 设置剪贴板，将指定文本复制到系统剪贴板 | 设置剪贴板、复制到剪贴板、剪贴板复制     | `text: str` | `success: bool`, `error: str`              | ✅ 03006 |

***

## Desktop 模块 - 文件系统操作

| Action                      | 功能（详细）                           | 功能触发关键词               | 输入参数                                                                                | 输出参数                                        | 测试状态    |
| --------------------------- | -------------------------------- | --------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------- | ------- |
| `desktop_filesystem_read`   | 读取文件，读取指定路径文件的内容，支持指定编码、偏移量和行数限制 | 读取文件、文件读取、读取文本、打开文件   | `path: str`, `offset: int`(可选), `limit: int`(可选), `encoding: str`="utf-8"           | `success: bool`, `data: str`, `error: str`  | ✅ 03016 |
| `desktop_filesystem_write`  | 写入文件，将内容写入指定路径文件，支持追加模式和指定编码     | 写入文件、文件写入、保存文件、写文件    | `path: str`, `content: str`, `append: bool`=False, `encoding: str`="utf-8"          | `success: bool`, `data: Any`, `error: str`  | ✅ 03012 |
| `desktop_filesystem_copy`   | 复制文件，将源文件复制到目标路径，支持覆盖已存在文件       | 复制文件、文件复制、拷贝文件        | `source: str`, `destination: str`, `overwrite: bool`=False                          | `success: bool`, `data: Any`, `error: str`  | ✅ 03013 |
| `desktop_filesystem_move`   | 移动文件，将源文件移动到目标路径，支持覆盖已存在文件       | 移动文件、文件移动、剪切文件、重命名文件  | `source: str`, `destination: str`, `overwrite: bool`=False                          | `success: bool`, `data: Any`, `error: str`  | ✅ 03015 |
| `desktop_filesystem_delete` | 删除文件，删除指定路径的文件或目录，支持递归删除         | 删除文件、文件删除、删除目录、移除文件   | `path: str`, `recursive: bool`=False                                                | `success: bool`, `data: Any`, `error: str`  | ✅ 03014 |
| `desktop_filesystem_list`   | 列出目录，列出指定目录下的文件和子目录，支持通配符过滤和递归   | 列出目录、目录列表、查看目录、浏览目录   | `path: str`, `pattern: str`(可选), `recursive: bool`=False, `show_hidden: bool`=False | `success: bool`, `data: List`, `error: str` | ✅ 03011 |
| `desktop_filesystem_search` | 搜索文件，在指定目录下搜索匹配模式的文件，支持递归搜索      | 搜索文件、文件搜索、查找文件、文件查找   | `path: str`, `pattern: str`="\*", `recursive: bool`=True                            | `success: bool`, `data: List`, `error: str` | ✅ 03018 |
| `desktop_filesystem_info`   | 获取文件信息，返回文件的大小、修改时间、权限等元数据       | 文件信息、文件详情、获取文件信息、文件属性 | `path: str`                                                                         | `success: bool`, `data: Dict`, `error: str` | ✅ 03017 |

***

## Desktop 模块 - PowerShell 操作

| Action                       | 功能（详细）                                       | 功能触发关键词                                | 输入参数                              | 输出参数                                         | 测试状态    |
| ---------------------------- | -------------------------------------------- | -------------------------------------- | --------------------------------- | -------------------------------------------- | ------- |
| `desktop_powershell_execute` | 执行 PowerShell，运行 PowerShell 命令并返回执行结果，支持超时设置 | 执行PowerShell、运行PowerShell、PowerShell命令 | `command: str`, `timeout: int`=30 | `success: bool`, `output: str`, `error: str` | ✅ 03004 |

***

## Desktop 模块 - 虚拟桌面操作

| Action                     | 功能（详细）                                                       | 功能触发关键词                              | 输入参数                                                 | 输出参数                                                                  | 测试状态    |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------ | ---------------------------------------------------- | --------------------------------------------------------------------- | ------- |
| `desktop_vd_get_count`     | 获取虚拟桌面数量，使用 COM 接口返回当前系统中的虚拟桌面总数                             | 虚拟桌面数量、桌面计数                          | 无                                                    | `success: bool`, `count: int`, `error: str`                           | ✅ 03029 |
| `desktop_vd_get_current`   | 获取当前虚拟桌面，使用 COM 接口返回当前激活的虚拟桌面信息（包含 GUID 和名称）                 | 当前虚拟桌面、当前桌面                          | 无                                                    | `success: bool`, `desktop_id: str`, `desktop_name: str`, `error: str` | ✅ 03029 |
| `desktop_vd_get_all`       | 获取所有虚拟桌面，使用 COM 接口返回所有虚拟桌面的列表（包含 GUID、名称和索引）                 | 所有虚拟桌面、桌面列表                          | 无                                                    | `success: bool`, `desktops: List[Dict]`, `count: int`, `error: str`   | ✅ 03029 |
| `desktop_vd_create`        | 创建虚拟桌面，使用 COM 接口创建新的 Windows 虚拟桌面，返回真实 GUID 和名称              | 创建虚拟桌面、新增桌面、虚拟桌面                     | 无                                                    | `success: bool`, `desktop_id: str`, `desktop_name: str`, `error: str` | ✅ 03032 |
| `desktop_vd_remove`        | 删除虚拟桌面，使用 COM 接口删除指定虚拟桌面，窗口迁移到回退桌面                           | 删除虚拟桌面、移除桌面                          | `desktop_name: str`                                  | `success: bool`, `error: str`                                         | ✅ 03032 |
| `desktop_vd_switch`        | 切换虚拟桌面，使用 COM 接口按方向或名称切换，支持 left/right/first/last 或桌面名称/GUID | 切换虚拟桌面、切换桌面、下一个桌面、上一个桌面、第一个桌面、最后一个桌面 | `direction: str`="left"/"right"/"first"/"last" 或桌面名称 | `success: bool`, `desktop_name: str`, `direction: str`, `error: str`  | ✅ 03032 |
| `desktop_vd_move_window`   | 移动窗口到虚拟桌面，使用 COM 接口将指定窗口移动到目标虚拟桌面                            | 移动窗口到桌面、窗口迁移                         | `hwnd: int`, `direction: str`="left"/"right" 或桌面名称   | `success: bool`, `error: str`                                         | ✅ 03033 |
| `desktop_vd_is_on_current` | 检查窗口是否在当前桌面，使用 COM 接口判断指定窗口是否在当前虚拟桌面上                        | 窗口是否在当前桌面、窗口桌面检查                     | `hwnd: int`, `desktop_id: str`(可选)                   | `success: bool`, `is_on_current: bool`, `error: str`                  | ✅ 03033 |

***

## Desktop 模块 - 多显示器操作

| Action                            | 功能（详细）                             | 功能触发关键词         | 输入参数 | 输出参数                                                                             | 测试状态    |
| --------------------------------- | ---------------------------------- | --------------- | ---- | -------------------------------------------------------------------------------- | ------- |
| `desktop_get_monitors_info`       | 获取显示器信息，返回所有连接显示器的详细信息（名称、分辨率、位置等） | 显示器信息、多显示器、屏幕信息 | 无    | `success: bool`, `monitors: List[Dict]`, `count: int`, `error: str`              | ✅ 03030 |
| `desktop_get_virtual_screen_rect` | 获取虚拟屏幕矩形，返回所有显示器组合成的虚拟屏幕边界         | 虚拟屏幕、屏幕边界、虚拟矩形  | 无    | `success: bool`, `rect: Dict`, `error: str`                                      | ✅ 03030 |
| `desktop_get_dpi_scaling`         | 获取 DPI 缩放，返回当前系统的 DPI 缩放比例         | DPI缩放、缩放比例、屏幕缩放 | 无    | `success: bool`, `dpi_x: int`, `dpi_y: int`, `scale_factor: float`, `error: str` | ✅ 03030 |

***

## Desktop 模块 - 高级操作

| Action                  | 功能（详细）                                | 功能触发关键词          | 输入参数              | 输出参数                                                                     | 测试状态    |
| ----------------------- | ------------------------------------- | ---------------- | ----------------- | ------------------------------------------------------------------------ | ------- |
| `desktop_detect_dialog` | 检测对话框，检测当前屏幕是否弹出对话框（ClassName=#32770） | 检测对话框、弹窗检测、对话框识别 | 无                 | `success: bool`, `dialog_found: bool`, `dialog_info: Dict`, `error: str` | ✅ 03031 |
| `desktop_wait`          | 等待指定时间，暂停执行指定的秒数                      | 等待、延时、暂停         | `duration: float` | `success: bool`, `waited: float`, `error: str`                           | ✅ 03031 |

***

## Desktop 模块 - Ping

| Action         | 功能（详细）          | 功能触发关键词     | 输入参数 | 输出参数                          | 测试状态    |
| -------------- | --------------- | ----------- | ---- | ----------------------------- | ------- |
| `desktop_ping` | 桌面Ping，测试桌面服务响应 | 桌面ping、桌面响应 | 无    | `success: bool`, `error: str` | ✅ 03003 |

***

## Web 模块 - 浏览器控制

| Action                   | 功能（详细）                                   | 功能触发关键词                   | 输入参数                                                                                                                                                                                                                                                                                                 | 输出参数                                                                                                                                              | 测试状态    |
| ------------------------ | ---------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `web_start`              | 启动浏览器，创建新的浏览器实例并打开指定 URL，支持无头模式、代理、隐身等配置 | 启动浏览器、打开浏览器、启动Chrome、打开网页 | `url: str`, `headless: bool`=False, `viewport: Dict`(可选), `cookie_record_id: str`(可选), `account_name: str`(可选), `stealth: bool`=False, `persistent_context: bool`=False, `user_data_dir: str`(可选), `proxy: Dict`(可选), `simulate_browsing: bool`=False, `use_cdp: bool`=True, `browser_path: str`(可选) | `success: bool`, `session_id: str`, `error: str`                                                                                                  | ✅ 04001 |
| `web_stop`               | 停止浏览器，关闭当前浏览器实例并释放相关资源                   | 停止浏览器、关闭浏览器、销毁浏览器         | 无                                                                                                                                                                                                                                                                                                    | `success: bool`, `error: str`                                                                                                                     | ✅ 04010 |
| `web_restart`            | 重启浏览器，关闭并重新启动浏览器，可指定新的 URL 和配置           | 重启浏览器、刷新浏览器、浏览器重启         | `url: str`(可选), `headless: bool`=False, `stealth: bool`=False, `use_cdp: bool`=True, `browser_path: str`(可选)                                                                                                                                                                                         | `success: bool`, `error: str`                                                                                                                     | ✅ 04011 |
| `web_get_browser_status` | 获取浏览器状态，返回浏览器运行状态、当前 URL、标签页数量等信息        | 浏览器状态、获取浏览器状态、浏览器信息       | 无                                                                                                                                                                                                                                                                                                    | `success: bool`, `is_started: bool`, `has_page: bool`, `has_context: bool`, `session_id: str`, `current_url: str`, `tab_count: int`, `error: str` | ✅ 04003 |

***

## Web 模块 - 页面导航

| Action          | 功能（详细）                            | 功能触发关键词                | 输入参数                                                                                              | 输出参数                                                                                                                                                                                                         | 测试状态    |
| --------------- | --------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| `web_navigate`  | 导航到 URL，在当前页面加载指定 URL，支持等待策略和超时设置 | 导航、打开网址、访问URL、跳转到、网页导航 | `url: str`, `wait_until: str`="domcontentloaded", `timeout: int`=30000, `activate_tab: bool`=True | `success: bool`, `url: str`, `final_url: str`, `title: str`, `load_time_ms: int`, `redirected: bool`, `tab_activated: bool`, `browser_started: bool`, `page_loaded: bool`, `login_status: str`, `error: str` | ✅ 04002 |
| `web_get_url`   | 获取当前 URL，返回浏览器当前页面的 URL 地址        | 获取URL、当前URL、页面URL、网址   | 无                                                                                                 | `success: bool`, `url: str`, `error: str`                                                                                                                                                                    | ✅ 04012 |
| `web_get_title` | 获取页面标题，返回当前页面的标题文本                | 获取标题、页面标题、网页标题         | 无                                                                                                 | `success: bool`, `title: str`, `error: str`                                                                                                                                                                  | ✅ 04013 |

***

## Web 模块 - 页面交互

| Action       | 功能（详细）                      | 功能触发关键词           | 输入参数                                                                           | 输出参数                          | 测试状态    |
| ------------ | --------------------------- | ----------------- | ------------------------------------------------------------------------------ | ----------------------------- | ------- |
| `web_click`  | 点击元素，根据选择器或元素 ID 点击页面上的元素   | 点击、点击元素、点击按钮、点击链接 | `selector: str`(可选), `element_id: str`(可选), `timeout: int`=10000               | `success: bool`, `error: str` | ✅ 04014 |
| `web_fill`   | 填充输入框，在指定的输入框中填入文本内容        | 填充、填写、输入、填入文本     | `selector: str`(可选), `value: str`, `element_id: str`(可选), `timeout: int`=10000 | `success: bool`, `error: str` | ✅ 04015 |
| `web_scroll` | 滚动页面，按指定方向和距离滚动页面内容         | 滚动、滚动页面、向下滚动、向上滚动 | `direction: str`="down", `amount: int`=500                                     | `success: bool`, `error: str` | ✅ 04006 |
| `web_press`  | 按键，在页面上模拟按键操作，如 Enter、Tab 等 | 按键、按键操作、按下键盘      | `key: str`                                                                     | `success: bool`, `error: str` | ✅ 04016 |
| `web_hover`  | 悬停，将鼠标移动到指定元素上并悬停           | 悬停、鼠标悬停、hover     | `selector: str`                                                                | `success: bool`, `error: str` | ✅ 04017 |

***

## Web 模块 - 页面信息获取

| Action               | 功能（详细）                           | 功能触发关键词               | 输入参数                                         | 输出参数                                               | 测试状态    |
| -------------------- | -------------------------------- | --------------------- | -------------------------------------------- | -------------------------------------------------- | ------- |
| `web_screenshot`     | 截图，捕获当前页面或指定元素的图像，返回 base64 编码数据 | 截图、网页截图、页面截图          | `selector: str`(可选), `full_page: bool`=False | `success: bool`, `data: str`(base64), `error: str` | ✅ 04004 |
| `web_get_content`    | 获取页面内容，返回当前页面的 HTML 源码           | 获取内容、HTML内容、网页源码、页面源码 | 无                                            | `success: bool`, `content: str`, `error: str`      | ✅ 04005 |
| `web_get_clean_text` | 获取纯净文本，提取页面主要内容文本，去除导航栏、广告等无关内容  | 纯净文本、主要文本、页面文本、内容提取   | 无                                            | `success: bool`, `clean_text: str`, `error: str`   | ✅ 04018 |

***

## Web 模块 - Cookie 操作

| Action            | 功能（详细）                         | 功能触发关键词                      | 输入参数 | 输出参数                                           | 测试状态    |
| ----------------- | ------------------------------ | ---------------------------- | ---- | ---------------------------------------------- | ------- |
| `web_get_cookies` | 获取 Cookies，返回当前页面的所有 Cookie 信息 | 获取Cookies、读取Cookies、Cookie信息 | 无    | `success: bool`, `cookies: List`, `error: str` | ✅ 04007 |

***

## Web 模块 - 页面结构

| Action                         | 功能（详细）                        | 功能触发关键词               | 输入参数                               | 输出参数                                             | 测试状态    |
| ------------------------------ | ----------------------------- | --------------------- | ---------------------------------- | ------------------------------------------------ | ------- |
| `web_get_page_structure`       | 获取页面结构，分析页面 DOM 结构，返回层级化的元素信息 | 页面结构、DOM结构、网页结构、页面分析  | `config: Dict`(可选)                 | `success: bool`, `structure: Dict`, `error: str` | ✅ 04019 |
| `web_get_page_urls`            | 获取页面 URL 列表，提取页面中所有链接地址       | 页面URL、所有链接、链接列表、提取链接  | `url: str`(必填), `config: Dict`(可选) | `success: bool`, `urls: List`, `error: str`      | ✅ 04028 |
| `web_get_interactive_elements` | 获取可交互元素，识别页面中所有可点击、可输入的交互元素   | 可交互元素、交互元素、按钮列表、可点击元素 | `config: Dict`(可选)                 | `success: bool`, `elements: List`, `error: str`  | ✅ 04020 |
| `web_find_buttons`             | 查找按钮，根据按钮文本查找页面中的按钮元素         | 查找按钮、找按钮、按钮定位         | `button_text: str`(必填)             | `success: bool`, `buttons: List`, `error: str`   | ✅ 04021 |

***

## Web 模块 - 等待操作

| Action                     | 功能（详细）                            | 功能触发关键词          | 输入参数                                                                                                                   | 输出参数                          | 测试状态    |
| -------------------------- | --------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ------- |
| `web_wait_for_selector`    | 等待选择器，等待指定选择器的元素出现在页面上            | 等待元素、等待加载、等待出现   | `selector: str`, `timeout: int`=30000                                                                                  | `success: bool`, `error: str` | ✅ 04022 |
| `web_wait_for_text_stable` | 等待文本稳定，等待指定元素的文本内容不再变化，用于等待动态加载完成 | 等待文本、文本稳定、等待加载完成 | `selector: str`, `timeout: int`=300000, `stable_duration: int`=8000, `check_interval: int`=200, `initial_delay: int`=0 | `success: bool`, `error: str` | ✅ 04023 |

***

## Web 模块 - JavaScript 执行

| Action         | 功能（详细）                                     | 功能触发关键词                | 输入参数          | 输出参数                                         | 测试状态    |
| -------------- | ------------------------------------------ | ---------------------- | ------------- | -------------------------------------------- | ------- |
| `web_evaluate` | 执行 JavaScript，在页面上下文中执行 JavaScript 代码并返回结果 | 执行JS、执行JavaScript、运行脚本 | `script: str` | `success: bool`, `result: Any`, `error: str` | ✅ 04024 |

***

## Web 模块 - 标签页管理

| Action             | 功能（详细）                  | 功能触发关键词           | 输入参数                        | 输出参数                                                     | 测试状态    |
| ------------------ | ----------------------- | ----------------- | --------------------------- | -------------------------------------------------------- | ------- |
| `web_get_tabs`     | 获取标签页列表，返回浏览器中所有标签页的信息  | 标签页列表、所有标签页、获取标签页 | 无                           | `success: bool`, `tabs: List[Dict]`, `error: str`        | ✅ 04008 |
| `web_new_tab`      | 新建标签页，创建新标签页并导航到指定 URL  | 新建标签页、打开新标签、新标签页  | `url: str`="about:blank"    | `success: bool`, `tab_id: str`, `url: str`, `error: str` | ✅ 04009 |
| `web_close_tab`    | 关闭标签页，关闭指定的标签页          | 关闭标签页、关闭标签、关闭页面   | `tab_id: str`(可选)           | `success: bool`, `error: str`                            | ✅ 04025 |
| `web_activate_tab` | 激活标签页，切换到指定的标签页使其成为活动标签 | 激活标签页、切换标签、切换标签页  | `tab_id: str`(可选，默认激活当前标签页) | `success: bool`, `error: str`                            | ✅ 04029 |

***

## Web 模块 - 任务管理

| Action             | 功能（详细）                       | 功能触发关键词        | 输入参数                                                                     | 输出参数                                                                         | 测试状态    |
| ------------------ | ---------------------------- | -------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------- | ------- |
| `web_execute_task` | 执行任务，使用 AI 模型执行自然语言描述的网页操作任务 | 执行任务、AI任务、智能任务 | `task: str`, `initial_url: str`="<https://www.baidu.com>"                | `success: bool`, `result: Any`, `error: str`                                 | ✅ 04026 |
| `web_task_submit`  | 提交异步任务，将操作提交到任务队列异步执行        | 提交任务、异步任务、队列任务 | `action: str`, `params: Dict`                                            | `success: bool`, `task_id: str`, `status: str`, `error: str`                 | ✅ 04027 |
| `web_task_status`  | 获取任务状态，查询异步任务的执行状态           | 任务状态、查询任务、任务进度 | `task_id: str`                                                           | `success: bool`, `task_id: str`, `status: str`, `error: str`                 | ✅ 04027 |
| `web_task_result`  | 获取任务结果，获取已完成异步任务的执行结果        | 任务结果、获取结果、任务输出 | `task_id: str`                                                           | `success: bool`, `task_id: str`, `status: str`, `result: Any`, `error: str`  | ✅ 04027 |
| `web_task_cancel`  | 取消任务，取消指定的异步任务               | 取消任务、停止任务、任务取消 | `task_id: str`(可选), `action: str`(可选), `cancel_running: bool`=False      | `success: bool`, `cancelled_count: int`, `cancelled_ids: List`, `error: str` | ✅ 04027 |
| `web_task_list`    | 获取任务列表，返回任务队列中的任务列表和统计信息     | 任务列表、所有任务、待办任务 | `status: str`(可选), `include_queued: bool`=True, `resource_type: str`(可选) | `success: bool`, `tasks: List`, `summary: Dict`, `error: str`                | ✅ 04027 |

***

## Web 模块 - 模拟人类行为

| Action                  | 功能（详细）                   | 功能触发关键词        | 输入参数                                                                    | 输出参数                          | 测试状态    |
| ----------------------- | ------------------------ | -------------- | ----------------------------------------------------------------------- | ----------------------------- | ------- |
| `web_human_scroll`      | 人类滚动，模拟人类滚动行为，包含随机速度和停顿  | 人类滚动、自然滚动、模拟滚动 | `direction: str`="down", `distance: int`(可选)                            | `success: bool`, `error: str` | ✅ 04030 |
| `web_human_type`        | 人类输入，模拟人类打字行为，包含随机延迟     | 人类输入、自然打字、模拟打字 | `selector: str`, `text: str`, `min_delay: int`=50, `max_delay: int`=150 | `success: bool`, `error: str` | ✅ 04031 |
| `web_simulate_browsing` | 模拟浏览，模拟真实用户浏览行为，用于绕过反爬检测 | 模拟浏览、模拟人类、反爬检测 | `warmup_url: str`="<https://www.baidu.com>"                             | `success: bool`, `error: str` | ✅ 04032 |
| `web_random_delay`      | 随机延迟，在指定范围内随机等待一段时间      | 随机延迟、随机等待、延时等待 | `min_sec: float`=0.5, `max_sec: float`=2.0                              | `success: bool`, `error: str` | ✅ 04033 |

***

## WeChat 模块 - 连接管理

| Action               | 功能（详细）                       | 功能触发关键词           | 输入参数 | 输出参数                                                                               | 测试状态    |
| -------------------- | ---------------------------- | ----------------- | ---- | ---------------------------------------------------------------------------------- | ------- |
| `wechat_connect`     | 连接微信，建立与微信客户端的 IPC 连接，返回用户资料 | 连接微信、连接微信客户端、登录微信 | 无    | `success: bool`, `connected: bool`, `profile: Dict`, `error: str`                  | ✅ 05001 |
| `wechat_disconnect`  | 断开微信连接，关闭与微信客户端的连接           | 断开微信、断开连接、退出微信    | 无    | `success: bool`, `error: str`                                                      | ✅ 05007 |
| `wechat_get_status`  | 获取微信状态，返回微信连接状态和当前活动会话       | 微信状态、连接状态、微信状态查询  | 无    | `success: bool`, `connected: bool`, `active: bool`, `chat_name: str`, `error: str` | ✅ 05008 |
| `wechat_get_profile` | 获取用户资料，返回当前登录用户的昵称和微信号       | 用户资料、个人资料、微信资料    | 无    | `success: bool`, `profile: Dict`, `error: str`                                     | ✅ 05009 |

***

## WeChat 模块 - 会话管理

| Action                  | 功能（详细）               | 功能触发关键词        | 输入参数 | 输出参数                                                                               | 测试状态    |
| ----------------------- | -------------------- | -------------- | ---- | ---------------------------------------------------------------------------------- | ------- |
| `wechat_get_sessions`   | 获取会话列表，返回微信左侧会话列表信息  | 会话列表、聊天列表、获取会话 | 无    | `success: bool`, `sessions: List[Dict]`, `error: str`                              | ✅ 05002 |
| `wechat_get_all_unread` | 获取所有未读，返回所有会话的未读消息统计 | 所有未读、未读消息、未读统计 | 无    | `success: bool`, `unread_data: Dict[str, Dict]`, `total_unread: int`, `error: str` | ✅ 05011 |

***

## WeChat 模块 - 消息操作

| Action                       | 功能（详细）               | 功能触发关键词        | 输入参数                                                                 | 输出参数                                                  | 测试状态    |
| ---------------------------- | -------------------- | -------------- | -------------------------------------------------------------------- | ----------------------------------------------------- | ------- |
| `wechat_send_message`        | 发送消息，向指定联系人或群组发送文本消息 | 发送消息、发消息、微信发消息 | `chat_name: str`, `message: str`, `target_type: str`="contact"       | `success: bool`, `message: str`, `error: str`         | ✅ 05005 |
| `wechat_send_file`           | 发送文件，向指定联系人或群组发送文件   | 发送文件、发文件、微信发文件 | `chat_name: str`, `file_path: str`, `target_type: str`="contact"     | `success: bool`, `message: str`, `error: str`         | ✅ 05012 |
| `wechat_get_messages`        | 获取聊天记录，获取指定会话的历史消息   | 聊天记录、历史消息、获取消息 | `chat_name: str`, `target_type: str`="contact", `since: str`="today" | `success: bool`, `messages: List[Dict]`, `error: str` | ✅ 05003 |
| `wechat_get_unread_messages` | 获取未读消息，获取指定会话的未读消息列表 | 未读消息、最新消息、未读列表 | `chat_name: str`, `unread_count: int`=10                             | `success: bool`, `messages: List[Dict]`, `error: str` | ✅ 05004 |

***

## WeChat 模块 - 群组操作

| Action                     | 功能（详细）            | 功能触发关键词         | 输入参数              | 输出参数                                                | 测试状态    |
| -------------------------- | ----------------- | --------------- | ----------------- | --------------------------------------------------- | ------- |
| `wechat_get_group_members` | 获取群成员，返回指定群组的成员列表 | 群成员、群成员列表、获取群成员 | `group_name: str` | `success: bool`, `members: List[str]`, `error: str` | ✅ 05006 |

***

## OpenCLI 模块 - 适配器管理

| Action                  | 功能（详细）                       | 功能触发关键词            | 输入参数                                            | 输出参数                                                                | 测试状态    |
| ----------------------- | ---------------------------- | ------------------ | ----------------------------------------------- | ------------------------------------------------------------------- | ------- |
| `opencli_list_adapters` | 列出适配器，返回所有已注册的 OpenCLI 适配器列表 | 列出适配器、适配器列表、CLI适配器 | `category: str`(可选), `enabled_only: bool`=False | `success: bool`, `adapters: List[Dict]`, `count: int`, `error: str` | ✅ 07001 |
| `opencli_get_adapter`   | 获取适配器，返回指定适配器的详细配置信息         | 获取适配器、适配器信息、CLI配置  | `adapter: str`                                  | `success: bool`, `adapter: Dict`, `error: str`                      | ✅ 07003 |

***

## OpenCLI 模块 - 执行/配置

| Action                  | 功能（详细）                    | 功能触发关键词               | 输入参数                                              | 输出参数                                                                       | 测试状态    |
| ----------------------- | ------------------------- | --------------------- | ------------------------------------------------- | -------------------------------------------------------------------------- | ------- |
| `opencli_execute`       | 执行命令，通过指定适配器执行 CLI 命令     | 执行命令、CLI命令、执行CLI      | `adapter: str`, `command: str`, `params: Dict`={} | `success: bool`, `data: Any`, `adapter: str`, `command: str`, `error: str` | ✅ 07002 |
| `opencli_validate_yaml` | 验证 YAML，验证适配器 YAML 配置的正确性 | 验证YAML、YAML验证、CLI配置验证 | `yaml_content: str`                               | `success: bool`, `errors: List`, `warnings: List`                          | ✅ 07007 |
| `opencli_get_stats`     | 获取统计，返回 OpenCLI 使用统计信息    | 使用统计、CLI统计、统计信息       | 无                                                 | `success: bool`, `stats: Dict`, `error: str`                               | ✅ 07005 |
| `opencli_get_logs`      | 获取日志，返回 OpenCLI 操作日志记录    | 操作日志、CLI日志、日志记录       | `limit: int`=100, `adapter: str`(可选)              | `success: bool`, `logs: List`, `count: int`, `error: str`                  | ✅ 07004 |

***

## OCR 模块

| Action           | 功能（详细）                             | 功能触发关键词               | 输入参数                                                                      | 输出参数                                                                                                 | 测试状态    |
| ---------------- | ---------------------------------- | --------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------- |
| `ocr_recognize`  | 识别文本，对传入的图像数据进行 OCR 文字识别           | 文字识别、图像识别、OCR识别       | `image_data: str`(base64), `session_id: str`(可选)                          | `success: bool`, `source: str`, `elements: List[Dict]`, `forms: List`, `summary: Dict`, `error: str` | ✅ 09001 |
| `ocr_click_text` | 点击文本，通过 OCR 识别屏幕上的文本并点击指定文本位置      | OCR点击、点击文字、识别点击       | `text: str`, `screenshot_data: str`(base64)(可选)                           | `success: bool`, `error: str`                                                                        | ✅ 09002 |
| `ocr_screenshot` | OCR 截图，截取屏幕并进行 OCR 文字识别，返回识别到的文本元素 | OCR截图、屏幕识别、文字识别、截图OCR | `image_data: str`(base64)(可选), `region: Tuple`(可选), `session_id: str`(可选) | `success: bool`, `source: str`, `elements: List[Dict]`, `forms: List`, `summary: Dict`, `error: str` | ✅ 09003 |

***

## Embedding 模块

| Action                    | 功能（详细）                                | 功能触发关键词                 | 输入参数                                 | 输出参数                                                                                           | 测试状态    |
| ------------------------- | ------------------------------------- | ----------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------- | ------- |
| `embedding_health`        | 健康检查，检查 Embedding 服务的可用性，返回服务状态、模型信息等 | 健康检查、服务状态、Embedding状态   | 无                                    | `success: bool`, `status: str`, `model: str`, `version: str`, `dimension: int`, `error: str`   | ✅ 08001 |
| `embedding_embed`         | 生成嵌入向量，将文本转换为向量表示，用于语义搜索等场景           | 生成向量、嵌入向量、文本向量、语义向量     | `texts: List[str]`, `model: str`(可选) | `success: bool`, `embeddings: List[List[float]]`, `dimension: int`, `count: int`, `error: str` | ✅ 08002 |
| `embedding_similar_score` | 计算相似度分数，计算多个文本与基准文本的语义相似度             | 相似度计算、文本相似度、语义相似度、向量相似度 | `texts: List[str]`, `base_text: str` | `success: bool`, `scores: List[Tuple[str, float]]`, `error: str`                               | ✅ 08003 |

***

## Web Info 模块（非浏览器状态下，使用）

| Action            | 功能（详细）                       | 功能触发关键词          | 输入参数                            | 输出参数                                                                                     | 测试状态    |
| ----------------- | ---------------------------- | ---------------- | ------------------------------- | ---------------------------------------------------------------------------------------- | ------- |
| `web_info_search` | 信息搜索，通过搜索引擎获取相关信息            | 信息搜索、网页搜索、搜索引擎搜索 | `query: str`, `engine: str`(可选) | `success: bool`, `results: List`, `error: str`                                           | ✅ 11001 |
| `web_info_fetch`  | 信息抓取，从指定 URL 获取网页内容并解析为结构化数据 | 信息抓取、网页抓取、内容获取   | `url: str`                      | `success: bool`, `content: List[Dict]`(包含text和url的结构化列表), `text: str`(纯文本), `error: str` | ✅ 11002 |

***

**文档版本**: 2.5.0\
**更新日期**: 2026-04-21
