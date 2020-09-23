# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['log_analysis_main.py'],
             pathex=['C:\\Program Files\\Python38\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'C:\\Users\\Vincoo\\Desktop\\Python\\HUAWEI BH30 FLOW LOG ANALYSIS\\HUAWEI BH30 FLOW LOG ANALYSIS'],
             binaries=[],
             datas=[('./CHANGELOG','./'),('./HELP','./')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

def getAppName():
    import log_analysis_main
    return log_analysis_main.APP_NAME + '_' + log_analysis_main.APP_VERSION

def getBuiltDate():
    import time
    appName = getAppName()
    return appName + '_' + time.strftime("%Y%m%d%H%M%S", time.localtime())

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=getAppName(),
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name=getBuiltDate())
