生成可执行应用程序（绿色版免安装）
1、获得site-packages\PyQt5\Qt\bin目录
2、进入C:\Windows\System32，右键cmd.exe管理员运行
3、cd 定位到工程目录下
4、pyinstaller -Dw --paths "C:\Users\movin\AppData\Local\Programs\Python\Python37\Lib\site-packages\PyQt5\Qt\bin" log_analysis_main.spec