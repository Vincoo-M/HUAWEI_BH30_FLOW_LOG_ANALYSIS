import os
import time
import traceback

from PyQt5.Qt import *
import sys
from UI.main_ui import Ui_main
from log_analysis_tool import logFileManage
import logging
import constant

# app information
APP_NAME = 'FLOW LOG Analysis'
APP_VERSION = '1.10_Beta'
BUILT_DATE = 'Built on Oct 12, 2020'
POWERED_BY = 'Powered by: Vincoo'
EMAIL = 'Email: movincoo@163.com | matengnan@ebelter.com'

MREGE_TEMP_FILE_NAME = './mrege_temp_file'
FONT_LABEL = '微软雅黑'
DEFAULT_BLE_ADDROFFSET = '0x1FFEED80'
DEFAULT_WIFI_ADDROFFSET = '0x40210000'

# log config
logging.basicConfig(level=constant.DEBUG, format=constant.LOG_FORMAT, datefmt=constant.DATE_FORMAT)


class MainWindow(QMainWindow, Ui_main):
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setMaximumSize(self.width(), self.height())
        self.setMinimumSize(self.width(), self.height())
        self.setWindowTitle(APP_NAME + '_' + APP_VERSION)
        self.logpath = ''
        self.setting = None
        self.initView()
        self.bleVersion = 0
        # 测试使用

        # logFilePath = r'C:/Users/Vincoo/Desktop/HUAWEI BH30 流水日志解析项目/Log/Log20200902/Herm-B19_1.0.1.24_BF844BD274CB13D64BC0B621215C9A028414056552A88672C3A51ED32BB1486B_20200902155916_WearableBeta_mcu_debug.log'
        # self.logFilePath = r'C:/Users/Vincoo/Desktop/HUAWEI BH30 流水日志解析项目/Log/Log20200902/Herm-B19_1.0.1.24_126A7EED3B4DAD503125B3EECFF9747FBA15B6BC8FC66584D952DFF95530744D_20200902235919_WearableBeta_mcu_debug.log'
        # self.bleBinFilePath = r'C:/Users/Vincoo/Desktop/HUAWEI BH30 流水日志解析项目/Log/Log20200902/Herm_BLE_V1.0.1.24.bin'
        # self.wifiBinFilePath = r'C:/Users/Vincoo/Desktop/HUAWEI BH30 流水日志解析项目/Log/Log20200902/Herm_WIFI_V1.0.1.24A_COMBINE.bin'
        # self.bleAddrOffset = 0x1FFEED80
        # self.wifiAddrOffset = 0x40210000

    def initView(self):
        # addr offset恢复默认
        self.addrOffsetDefault()
        self.bt_select_logfile.clicked.connect(self.selectLogFiles)
        self.bt_add_ble_binfile.clicked.connect(self.selectBleBinFile)
        self.bt_add_wifi_binfile.clicked.connect(self.selectWifiBinFile)
        self.bt_analysis.clicked.connect(self.analysisFile)

        self.bt_lock.clicked.connect(self.addrOffsetChangeLock)
        self.bt_default.clicked.connect(self.addrOffsetDefault)
        self.bt_opendir.clicked.connect(self.openDir)

        self.actionAbout.triggered.connect(self.showAboutDialog)
        self.actionUpdateInfo.triggered.connect(self.showChangeLogDialog)
        self.actionHelp.triggered.connect(self.showHelpDialog)

        self.rb_36down.setHidden(True)
        self.rb_36up.setHidden(True)

    def showAboutDialog(self):
        '''
            菜单栏显示关于窗口
        '''
        self.aboutDialog = QDialog(self, flags=Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.aboutDialog.resize(480, 180)
        self.aboutDialog.setWindowTitle('关于')

        self.aboutLabel_0 = QLabel()
        self.aboutLabel_0.setText(APP_NAME)
        self.aboutLabel_0.setFont(QFont(FONT_LABEL, 10, QFont.Bold))

        self.aboutLabel_1 = QLabel()
        self.aboutLabel_1.setText('Version: ' + APP_VERSION)
        self.aboutLabel_1.setFont(QFont(FONT_LABEL, 9))

        self.aboutLabel_2 = QLabel()
        self.aboutLabel_2.setText(BUILT_DATE)
        self.aboutLabel_2.setFont(QFont(FONT_LABEL, 9))

        self.aboutLabel_3 = QLabel()
        self.aboutLabel_3.setText(POWERED_BY)
        self.aboutLabel_3.setFont(QFont(FONT_LABEL, 9))

        self.aboutLabel_4 = QLabel()
        self.aboutLabel_4.setText(EMAIL)
        self.aboutLabel_4.setFont(QFont(FONT_LABEL, 9))

        self.vbox = QVBoxLayout()
        self.vbox.addStretch()
        self.vbox.addWidget(self.aboutLabel_0)
        self.vbox.addWidget(self.aboutLabel_1)
        self.vbox.addWidget(self.aboutLabel_2)
        self.vbox.addWidget(self.aboutLabel_3)
        self.vbox.addWidget(self.aboutLabel_4)
        self.vbox.addStretch()
        self.vbox.setContentsMargins(30, 0, 30, 0)
        self.aboutDialog.setLayout(self.vbox)
        self.aboutDialog.open()  # open窗口模态，只会阻塞一个窗口，而不是将整个系统阻塞掉

    def showChangeLogDialog(self):
        '''
            菜单栏显示软件版本更新日志
        '''
        self.changeLogDialog = QDialog(self, flags=Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.changeLogDialog.resize(480, 420)
        self.changeLogDialog.setWindowTitle('版本更新日志')
        self.changeLog_text = QTextBrowser(self.changeLogDialog)
        self.changeLog_text.resize(480, 420)
        self.changeLog_text.setFont(QFont(FONT_LABEL, 10))
        self.changeLog_text.setMarkdown(open('./CHANGELOG', mode='r', encoding='utf8').read())
        # self.changeLog_text.setText()
        self.changeLog_text.setStyleSheet('background-color: rgb(240, 240, 240);')  # rgb(240, 240, 240)
        self.changeLog_text.setFrameShape((QFrame.NoFrame))

        self.changeLogDialog.open()

    def showHelpDialog(self):
        '''
           菜单栏显示帮助
        '''
        self.helpDialog = QDialog(self, flags=Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.helpDialog.resize(480, 420)
        self.helpDialog.setWindowTitle('帮助')
        self.help_text = QTextBrowser(self.helpDialog)
        self.help_text.resize(480, 420)
        self.help_text.setFont(QFont(FONT_LABEL, 10))
        self.help_text.setMarkdown(open('./HELP', mode='r', encoding='utf8').read())
        # self.changeLog_text.setText()
        self.help_text.setStyleSheet('background-color: rgb(240, 240, 240);')  # rgb(240, 240, 240)
        self.help_text.setFrameShape((QFrame.NoFrame))

        self.helpDialog.open()

    def addrOffsetDefault(self):
        self.le_ble_addr_offset.setText(DEFAULT_BLE_ADDROFFSET)
        self.le_wifi_addr_offset.setText(DEFAULT_WIFI_ADDROFFSET)

    def addrOffsetChangeLock(self):
        if self.bt_lock.text() == '解锁':
            self.le_ble_addr_offset.setEnabled(True)
            self.le_wifi_addr_offset.setEnabled(True)
            self.bt_lock.setText('加锁')
        else:
            self.le_ble_addr_offset.setEnabled(False)
            self.le_wifi_addr_offset.setEnabled(False)
            self.bt_lock.setText('解锁')

    def openDir(self):
        if os.path.exists('./OutFile'):
            os.startfile('.\\OutFile')
        else:
            QMessageBox.warning(self, '错误', '未找到文件夹路径，打开文件夹失败！', QMessageBox.Ok)

    def selectLogFiles(self):
        lastPath = self.getConfigInfo()
        path = QFileDialog.getOpenFileNames(self, '选择Log文件', lastPath, 'ALL(*.*);;log files(*.txt *.log)',
                                            'log files(*.txt *.log)')[0]

        if path != []:
            self.setConfigInfo(path[0])
            self.logpath = path
            self.list_file_path.clear()
            try:
                for i, val in enumerate(self.logpath):
                    self.list_file_path.addItem(str(i + 1) + ' | ' + val)
            except Exception as e:
                print(repr(e))

    def selectBleBinFile(self):
        lastPath = self.getConfigInfo()
        path = QFileDialog.getOpenFileName(self, '选择蓝牙烧录文件', lastPath, 'ALL(*.*);;firmware files(*.bin)',
                                           'firmware files(*.bin)')[0]
        if path != '':
            self.setConfigInfo(path)
            self.le_ble_binfile.setText(path)
            blefilename = os.path.basename(path)
            if 'BLE' in blefilename:
                try:
                    ble_version = blefilename.rstrip('.bin').split('V')[1]
                    self.bleVersion = int(ble_version.split('.')[3], 10)
                except Exception as e:
                    self.lb_version.setText('[未识别，请选择版本信息！]')
                    self.rb_36down.setHidden(False)
                    self.rb_36up.setHidden(False)
                    QMessageBox.information(self, '提示', '版本号未能自动识别，请选择BIN版本信息，确认蓝牙地址偏移量是否正确！', QMessageBox.Ok)
                else:
                    self.lb_version.setText(
                        '[已识别版本] -%s- [已设置偏移量为%s]' % (ble_version, self.getBleAddrOffset(self.bleVersion)))
                    self.rb_36down.setHidden(True)
                    self.rb_36up.setHidden(True)

            else:
                self.lb_version.setText('[未识别，请选择版本信息！]')
                self.rb_36down.setHidden(False)
                self.rb_36up.setHidden(False)
                QMessageBox.information(self, '提示', '版本号未能自动识别，请选择BIN版本信息，确认蓝牙地址偏移量是否正确！', QMessageBox.Ok)

    def selectWifiBinFile(self):
        lastPath = self.getConfigInfo()
        path = QFileDialog.getOpenFileName(self, '选择WIFI烧录文件', lastPath, 'ALL(*.*);;firmware files(*.bin)',
                                           'firmware files(*.bin)')[0]
        if path != '':
            self.setConfigInfo(path)
            self.le_wifi_binfile.setText(path)

    def getConfigInfo(self):
        self.setting = QSettings("./Setting.ini", QSettings.IniFormat)
        path = str(self.setting.value('LastFilePath'))
        if path is None or path == '':
            return './'
        return path

    def setConfigInfo(self, path):
        self.setting.setValue('LastFilePath', path)

    def getBleAddrOffset(self, version):
        if 0 <= version < 28:
            offset = DEFAULT_BLE_ADDROFFSET
        elif 28 <= version < 31:
            offset = '0x1FFEED90'
        elif 31 <= version < 51:
            offset = '0x1FFEE920'
        elif 51 <= version < 53:
            offset = '0x1FFEE890'
        elif 53 <= version < 63:
            offset = '0x1FFEE880'
        else:
            offset = '0x1FFEE850'
        self.le_ble_addr_offset.setText(offset)
        return offset

    def analysisFile(self):
        ble_addr_offset = self.le_ble_addr_offset.text()
        wifi_addr_offset = self.le_wifi_addr_offset.text()
        if not all([ble_addr_offset, wifi_addr_offset]):
            QMessageBox.warning(self, '错误', '偏移量输入错误', QMessageBox.Ok)
            return
        bin_ble_path = self.le_ble_binfile.text()
        bin_wifi_path = self.le_wifi_binfile.text()
        if not all([self.logpath, bin_ble_path, bin_wifi_path]):
            QMessageBox.warning(self, '错误', '未选择文件！', QMessageBox.Ok)
            return
        if self.lb_version.text() == '[未识别，请选择版本信息！]':
            if not any([self.rb_36up.isChecked(), self.rb_36down.isChecked()]):
                QMessageBox.warning(self, '错误', '版本号未能自动识别，请选择BIN版本！', QMessageBox.Ok)
                return
            else:
                if self.rb_36down.isChecked():
                    self.bleVersion = 0
                if self.rb_36up.isChecked():
                    self.bleVersion = 36
        try:
            if len(self.logpath) == 1:
                log_path = self.logpath[0]
            else:
                if os.path.exists(MREGE_TEMP_FILE_NAME):
                    os.remove(MREGE_TEMP_FILE_NAME)
                tempfile = open(MREGE_TEMP_FILE_NAME, 'ab+')
                for path in self.logpath:
                    f = open(path, 'rb')
                    s = f.read()
                    tempfile.write(s)
                    tempfile.flush()
                    f.close()
                tempfile.close()
                log_path = MREGE_TEMP_FILE_NAME
        except Exception as e:
            print(repr(e))
        else:
            # 开始解析
            try:
                self.analysis_progressBar_dialog()
                self.analysisThread = AnalysisThread(log_path, bin_ble_path, bin_wifi_path, int(ble_addr_offset, 16),
                                                     int(wifi_addr_offset, 16), self.bleVersion)
                self.analysisThread.total_signal.connect(self.total_callBack)
                self.analysisThread.analysis_signal.connect(self.analysis_callBack)
                self.analysisThread.start()
            except Exception as e:
                time.sleep(0.5)
                self.progressBarDialog.close()
                QMessageBox.warning(self, '提示', '失败，解析出错，请将对应日志和BIN文件发送开发者！', QMessageBox.Ok)
                print(e)

    def total_callBack(self, number):
        self.progressBar.setRange(0, number)

    def analysis_callBack(self, number):
        if number == -1:
            time.sleep(0.5)
            self.progressBarDialog.close()
            QMessageBox.information(self, '提示', '解析结束', QMessageBox.Ok)
        elif number == -2:
            time.sleep(0.5)
            self.progressBarDialog.close()
            QMessageBox.warning(self, '提示', '失败，解析出错，请将对应日志和BIN文件发送至开发者！', QMessageBox.Ok)
        else:
            self.progressBar.setValue(number + 1)

    def analysis_progressBar_dialog(self):
        '''
            从服务器下载烧录文件的界面与逻辑
        '''
        # Dialog
        self.progressBarDialog = QDialog(self, flags=Qt.FramelessWindowHint | Qt.MSWindowsFixedSizeDialogHint)
        self.progressBarDialog.resize(400, 150)
        # Label
        self.lb_state = QLabel(self.progressBarDialog)
        self.lb_state.setContentsMargins(0, 0, 0, 10)
        self.lb_state.setFont(QFont(FONT_LABEL, 9))
        # ProgressBar
        self.progressBar = QProgressBar(self.progressBarDialog)
        # self.progressBar.setRange(0, 100)
        # Layout
        self.vbox_download = QVBoxLayout(self.progressBarDialog)
        self.vbox_download.addStretch()
        self.vbox_download.addWidget(self.lb_state)
        self.vbox_download.addWidget(self.progressBar)
        self.vbox_download.addStretch()
        self.vbox_download.setContentsMargins(30, 0, 30, 15)

        self.progressBarDialog.setLayout(self.vbox_download)
        self.progressBarDialog.open()
        self.lb_state.setText('正在解析，请稍后……')


class AnalysisThread(QThread):
    analysis_signal = pyqtSignal(int)
    total_signal = pyqtSignal(int)

    def __init__(self, logFilePath, bleBinPath, wifiBinPath, bleAddrOffset, wifiAddrOffset, binVersion):
        super(AnalysisThread, self).__init__()
        self.logFilePath = logFilePath
        self.bleBinPath = bleBinPath
        self.wifiBinPath = wifiBinPath
        self.bleAddrOffset = bleAddrOffset
        self.wifiAddrOffset = wifiAddrOffset
        self.binVersion = binVersion

    def run(self):
        try:
            logFileManage(self.logFilePath, self.bleBinPath, self.wifiBinPath, self.bleAddrOffset, self.wifiAddrOffset,
                          self.analysis_signal, self.total_signal, self.binVersion)
            self.analysis_signal.emit(-1)
        except Exception as e:
            self.analysis_signal.emit(-2)
            traceback.print_exc()
            # print(repr(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    logging.info('Version: %s' % APP_VERSION)
    logging.info('Time: %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    sys.exit(app.exec_())
