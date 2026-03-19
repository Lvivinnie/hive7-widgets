# HIVE-7 Red Queen Desktop Widgets

红皇后主题桌面控件 for Windows.

## 运行

```bash
python redqueen_server.py
```

## 文件说明

- `redqueen_widget.html` — 日历控件
- `redqueen_price.html` — 价格监控控件
- `redqueen_sysmon.html` — 系统监控控件
- `redqueen_server.py` — 主启动器（同时打开三个窗口）
- `redqueen_launch.py` — 单独启动日历控件
- `redqueen_wallpaper.png` — 红皇后主题壁纸

## 依赖

- Python 3
- pywebview (`pip install pywebview`)
- psutil (`pip install psutil`)

## 开机自启

将 `redqueen_start.bat` 放到启动文件夹。
