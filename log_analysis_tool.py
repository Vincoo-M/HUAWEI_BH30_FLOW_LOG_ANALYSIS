import os
import struct
import datetime
from constant import *
import flow_log_analysis
import xlwt

info_header = ['序号', '日期', '时间', '身高', '性别', '年龄', '体重', '阻抗', '体脂率', 'time interval', 'last weight', 'last bfr', '用户识别',
          '测量模式']
adc_header = ['日期', '时间', 'zero','filter','origin']
INFO_DATA = [''] * 13
MULTI_USER_FLAG = False
ONLINE_STATE = 0
LINE_FLAG = 0
MATCH_STATE = 0  # -1 唯一  # 1 多用户冲突


# 解析文件中每条log的长度
def getLogLength(file):
    if (file[0] == 0xEC):
        return 32
    elif ((file[0] == 0xEA) or (file[0] == 0xEB)):
        return 8
    else:
        print('log header error')
        return 0


# 获取文件中的log的数量
def getFileLogNumber(file):
    fileSize = len(file)
    logLength = getLogLength(file)
    return fileSize // logLength


def logFileManage(logFilePath, bleBinPath, wifiBinPath, bleAddrOffset, wifiAddrOffset, analysis_signal, total_signal,binVersion):
    f_logFile_obj = open(logFilePath, 'rb')
    f_bleBin_obj = open(bleBinPath, 'rb')
    f_wifiBin_obj = open(wifiBinPath, 'rb')
    f_logFile = f_logFile_obj.read()
    f_bleBin = f_bleBin_obj.read()
    f_wifiBin = f_wifiBin_obj.read()

    logLength = getLogLength(f_logFile)
    logNumber = getFileLogNumber(f_logFile)
    log = [0] * logLength
    excelFile, info_sheet, adc_sheet = createExcel(info_header,adc_header)
    infoExcelRow = 0
    adcExcelRow = 0
    fileName = getNewFilePath()
    txtFile = open(fileName + '.txt', "w", encoding='utf-8')
    total_signal.emit(logNumber)
    for j in range(0, logNumber):
        for i in range(0, logLength):
            log[i] = f_logFile[j * logLength + i]
        result,txt_result = logAnalysis(log, f_bleBin, f_wifiBin, bleAddrOffset, wifiAddrOffset)
        # txt 文件处理
        print(str(j + 1) + '|' + txt_result, file=txtFile)
        # excel 文件处理
        if MODE_BLE in result:
            if 0 <= binVersion < 36:
                info_result = infoExtraction(result)
            else:
                info_result = v36InfoExtraction(result, j+1, logNumber)
            if info_result != []:
                infoExcelRow += 1
                info_sheet.write(infoExcelRow, 0, infoExcelRow)
                for index, val in enumerate(info_result):
                    info_sheet.write(infoExcelRow, index + 1, val)
        if 'zero:' in result:
            adcExcelRow += 1
            adc_list = adcExtraction(result)
            for index,val in enumerate(adc_list):
                adc_sheet.write(adcExcelRow,index,val)
        analysis_signal.emit(j)
    txtFile.flush()
    txtFile.close()
    excelFile.save(fileName + '.xls')
    f_logFile_obj.close()
    f_bleBin_obj.close()
    f_wifiBin_obj.close()
    global MULTI_USER_FLAG
    MULTI_USER_FLAG = False
    global LINE_FLAG
    LINE_FLAG = 0
    global MATCH_STATE
    MATCH_STATE = 0
    global ONLINE_STATE
    ONLINE_STATE = 0


def logAnalysis(logArray, bleFile, wifiFile, bleAddrOffset, wifiAddrOffset):
    result = ''
    txt_result = ''
    byteLogArray = bytes(logArray)
    header = logArray[0]
    if header == LOG_HEADER_ACTION:
        print('ACTION LOG')
    elif header == LOG_HEADER_ERR:
        print('ERROR LOG')
    elif header == LOG_HEADER_FLOW:
        new_log_array = struct.unpack('>BBBBIIIIIII', byteLogArray)
        result,txt_result = flowLogAnalysis(new_log_array, bleFile, wifiFile, bleAddrOffset, wifiAddrOffset)
    else:
        print('HEADER ERROR')
    return result,txt_result


def flowLogAnalysis(logArray, bleFile, wifiFile, bleAddrOffset, wifiAddrOffset):
    result = ''
    str_header = logHeaderAnalysis(logArray[0])
    str_level = flow_log_analysis.level(logArray[1])
    str_mode = flow_log_analysis.mode(logArray[2])
    str_data, str_time = flow_log_analysis.time_(logArray[4])
    if str_mode == MODE_BLE:
        str_addr_result = flow_log_analysis.addr(logArray[5], bleAddrOffset, bleFile)
    elif str_mode == MODE_WIFI:
        str_addr_result = flow_log_analysis.addr(logArray[5], wifiAddrOffset, wifiFile)
    else:
        str_addr_result = str_mode
    str_index, str_line_number = flow_log_analysis.fileIndexAndLineNum(logArray[6])
    para2 = logArray[7]
    para3 = logArray[8]
    para4 = logArray[9]
    para5 = logArray[10]
    str_addr_result = addrResultFormat(str_addr_result, para2, para3, para4, para5)
    result = '%s|%s|%s|%s|%s|%s|%s|%s|0x%x|0x%x|0x%x|0x%x|' % (
    str_header, str_level, str_mode, str_data, str_time, str_addr_result, str_index, str_line_number, para2, para3,
    para4, para5)
    txt_result = '%s|%s|%s|%s|%s|%s| File index = %s | Line = %s | Para2 = 0x%x | Para3 = 0x%x | Para4 = 0x%x | Para5 = 0x%x' % (
    str_header, str_level, str_mode, str_data, str_time, str_addr_result, str_index, str_line_number, para2, para3,
    para4, para5)
    return result,txt_result


# LOG HEADER ANALYSIS
def logHeaderAnalysis(header):
    result = ''
    if header == LOG_HEADER_ACTION:
        string = 'ACITON LOG(行为日志)'
    elif header == LOG_HEADER_ERR:
        string = 'ERROR LOG(错误日志)'
    elif header == LOG_HEADER_FLOW:
        string = 'FLOW LOG(流水日志)'
    else:
        string = 'LOG HEADER ERROR'
    return string


def addrResultFormat(str, p2, p3, p4, p5):
    try:
        string = ''
        if '%' in str:
            count = str.count('%')
            if count == 1:
                string = str % p2
            elif count == 2:
                string = str % (p2, p3)
            elif count == 3:
                string = str % (p2, p3, p4)
            elif count == 4:
                string = str % (p2, p3, p4, p5)
            elif count == 5:
                string = str % (p2, p3, p4, p5, 00)
            elif count == 6:
                string = str % (p2, p3, p4, p5, 00, 00)
            else:
                string = str
        else:
            string = str
    except Exception as e:
        string = str
    return string


def createExcel(info_header,adc_header):
    excelFile = xlwt.Workbook(encoding='utf-8', style_compression=0)
    info_sheet = excelFile.add_sheet('information')
    adc_sheet = excelFile.add_sheet('adc')
    for i, val in enumerate(info_header):
        info_sheet.write(0, i, val)
    for i, val in enumerate(adc_header):
        adc_sheet.write(0, i, val)
    return excelFile, info_sheet,adc_sheet


def infoExtraction(str):
    info = []
    str_temp = str.split('|')
    global LINE_FLAG
    global INFO_DATA
    global MULTI_USER_FLAG
    if 'weight match' in str:

        LINE_FLAG = 1
        INFO_DATA[12] = '离线'    # mode
        if ',' in str:
            match = int(str_temp[9], 16)    # 在BLE OTA版本31之后，此处会打印出2个数值，后一个才为用户识别标识
        else:
            match = int(str_temp[8], 16)
        MULTI_USER_FLAG = False
        if match == 0xffffffff:
            identify_state = '已识别'
            INFO_DATA[11] = identify_state
        if match == 0x0:
            # 未识别
            LINE_FLAG = 0
        if match == 0x02:
            identify_state = '冲突识别'
            MULTI_USER_FLAG = True
            INFO_DATA[11] = identify_state
        if match == 0xfffffffe:
            LINE_FLAG = 0
    elif 'online' in str:
        LINE_FLAG = -1
        INFO_DATA[12] = '在线'    # mode
        INFO_DATA[11] = '/'

    if (LINE_FLAG == 1 or LINE_FLAG == -1) and 'sex:' in str:
        INFO_DATA[0] = str_temp[3]  # date
        INFO_DATA[1] = str_temp[4]  # time
        INFO_DATA[2] = int(str_temp[10], 16) / 10  # high
        if int(str_temp[8], 16) == 0x0:  # sex
            INFO_DATA[3] = '女'
        else:
            INFO_DATA[3] = '男'
        INFO_DATA[4] = int(str_temp[9], 16)  # age
        INFO_DATA[5] = int(str_temp[11], 16) / 100  # weight
        if LINE_FLAG == 1:
            LINE_FLAG = 2
        elif LINE_FLAG == -1:
            LINE_FLAG = -2

    if (LINE_FLAG == 2 or LINE_FLAG == -2) and 'res:' in str:
        INFO_DATA[6] = int(str_temp[8], 16) / 10  # res
        INFO_DATA[9] = int(str_temp[9], 16) / 100  # last weight
        INFO_DATA[10] = int(str_temp[10], 16) / 10  # last bfr
        INFO_DATA[8] = int(str_temp[11], 16)  # time interval
        if int(str_temp[8], 16) == 0:
            INFO_DATA[7] = 'null'
            info = INFO_DATA
            INFO_DATA = [''] * 13
            if MULTI_USER_FLAG:
                LINE_FLAG = 1
                INFO_DATA[11] = '冲突识别'
                INFO_DATA[12] = '离线'
            else:
                LINE_FLAG = 0
        else:
            if LINE_FLAG == 2:
                LINE_FLAG = 3
            elif LINE_FLAG == -2:
                LINE_FLAG = -3
            return info
    if (LINE_FLAG == 3 or LINE_FLAG == -3) and 'body fat:' in str:
        str_body_fat = int(str_temp[8], 16) / 10
        INFO_DATA[7] = str_body_fat
        info = INFO_DATA
        INFO_DATA = [''] * 13
        if MULTI_USER_FLAG:
            LINE_FLAG = 1
            INFO_DATA[11] = '冲突识别'
            INFO_DATA[12] = '离线'
        else:
            LINE_FLAG = 0
    if (LINE_FLAG == 3 or LINE_FLAG == -3) and 'body fat:' not in str:
        INFO_DATA[7] = '未打点'
        info = INFO_DATA
        INFO_DATA = [''] * 13
        if MULTI_USER_FLAG:
            LINE_FLAG = 1
            INFO_DATA[11] = '冲突识别'
            INFO_DATA[12] = '离线'
        else:
            LINE_FLAG = 0
    return info

def v36InfoExtraction(str,count,total):
    info = []
    str_temp = str.split('|')
    global ONLINE_STATE
    global INFO_DATA
    global MATCH_STATE
    if 'weight match:' in str:
        INFO_DATA = [''] * 13
        INFO_DATA[5] = int(str_temp[8], 16) / 100  # weight
        match = int(str_temp[9], 16)
        INFO_DATA[0] = str_temp[3]  # date
        INFO_DATA[1] = str_temp[4]  # time
        INFO_DATA[12] = '离线'    # mode
        if match == 0xffffffff:
            INFO_DATA[11] = '匹配到唯一用户'
            MATCH_STATE = -1
        elif match == 0x0:
            INFO_DATA[11] = '未匹配到用户'
            info = INFO_DATA
            INFO_DATA = [''] * 13
            # 这里如果是0，后面run_identify_flag是不是一定是3
        elif match != 0xffffffff and match != 0xfffffffe and match >= 0x01:
            INFO_DATA[11] = '多用户冲突（体重）'
            MATCH_STATE = 1
        elif match == 0xfffffffe:
            INFO_DATA[11] = '没有绑定WiFi账号'
            info = INFO_DATA
            INFO_DATA = [''] * 13
            # 这里如果是-2，后面run_identify_flag是不是一定是1
        else:
            INFO_DATA[11] = '解析工具出错或者bin文件错误'
            info = INFO_DATA
            INFO_DATA = [''] * 13

    elif 'online sex:' in str:
        # 防止出现已经找weight match头，但是中间出现 online sex, 所以丢掉上条weight match的数据
        MATCH_STATE = 0
        INFO_DATA = [''] * 13

        ONLINE_STATE = 1
        INFO_DATA[12] = '在线'    # mode
        INFO_DATA[11] = '/'


    if MATCH_STATE == -1 or MATCH_STATE == 1 or ONLINE_STATE == 1:
        if 'sex:' in str and 'age:' in str and 'high:' in str:
            INFO_DATA[0] = str_temp[3]  # date
            INFO_DATA[1] = str_temp[4]  # time
            INFO_DATA[2] = int(str_temp[10], 16) / 10  # high
            if int(str_temp[8], 16) == 0x0:  # sex
                INFO_DATA[3] = '女'
            else:
                INFO_DATA[3] = '男'
            INFO_DATA[4] = int(str_temp[9], 16)  # age
            INFO_DATA[5] = int(str_temp[11], 16) / 100  # weight
            if MATCH_STATE == -1:
                MATCH_STATE = -2
            if MATCH_STATE == 1:
                MATCH_STATE = 2
            if ONLINE_STATE == 1:
                ONLINE_STATE = 2
        else:
            if MATCH_STATE == 1:
                if 'offline measure,identify fat,res:' in str:
                    INFO_DATA[6] = int(str_temp[8], 16) / 10  # res
                # if 'run_identify_flag:' in str or '':     # 1.7版本是写的这条判断语句，不知道为什么，可能写错了
                if 'run_identify_flag:' in str:
                    # 1 没有WIFI权限的用户
                    # 2 识别到唯一用户
                    # 3 未匹配到用户
                    # 4 多用户冲突
                    identify = int(str_temp[8], 16)
                    if identify == 1:
                        INFO_DATA[11] = '没有WIFI权限的用户'
                    elif identify == 2:
                        INFO_DATA[11] = '识别到唯一用户'
                    elif identify == 3:
                        INFO_DATA[11] = '未匹配到用户'
                    elif identify == 4:
                        INFO_DATA[11] = '多用户冲突'
                    else:
                        INFO_DATA[11] = '解析工具出错或者bin文件出错，identify不等于1，2，3，4'
                    MATCH_STATE = 0
                    info = INFO_DATA
                    INFO_DATA = [''] * 13
                if 'status' in str:  #
                    MATCH_STATE = 0
                    info = INFO_DATA
                    INFO_DATA = [''] * 13
            if MATCH_STATE == -1 and 'zero:' in str and 'filter:' in str and 'origin:' in str:
                MATCH_STATE = 0
                info = INFO_DATA
                INFO_DATA = [''] * 13
            elif MATCH_STATE == -1 and count == total:
                MATCH_STATE = 0
                info = INFO_DATA
                INFO_DATA = [''] * 13

    if MATCH_STATE == -2 or MATCH_STATE == 2 or ONLINE_STATE == 2:
        if 'res:' in str and 'last:' in str:
            INFO_DATA[6] = int(str_temp[8], 16) / 10  # res
            INFO_DATA[9] = int(str_temp[9], 16) / 100  # last weight
            INFO_DATA[10] = int(str_temp[10], 16) / 10  # last bfr
            INFO_DATA[8] = int(str_temp[11], 16)  # time interval
            if int(str_temp[8], 16) == 0:       # res=0,下面不会打印体脂和run_identify_flag
                INFO_DATA[7] = 'null'
                MATCH_STATE = 0
                ONLINE_STATE = 0
                info = INFO_DATA
                INFO_DATA = [''] * 13
            else:
                if MATCH_STATE == -2:
                    MATCH_STATE = -3
                if MATCH_STATE == 2:
                    MATCH_STATE = 3
                if ONLINE_STATE == 2:
                    ONLINE_STATE = 3

    if MATCH_STATE == -3 or MATCH_STATE == 3 or ONLINE_STATE == 3:
        if 'body fat:' in str:
            str_body_fat = int(str_temp[8], 16) / 10
            INFO_DATA[7] = str_body_fat
            if MATCH_STATE == -3:
                MATCH_STATE = 0
                info = INFO_DATA
                INFO_DATA = [''] * 13
            if MATCH_STATE == 3:
                MATCH_STATE = 1
            if ONLINE_STATE == 3:
                ONLINE_STATE = 0
                info = INFO_DATA
                INFO_DATA = [''] * 13
    return info

def adcExtraction(str):
    str_temp = str.split('|')
    adc_list = [str_temp[3],str_temp[4],int(str_temp[8], 16),int(str_temp[9], 16),int(str_temp[10], 16)]
    return adc_list

def getNewFilePath():
    path = './OutFile/'
    if not os.path.exists(path):
        os.mkdir(path)
    return path + "out_log%s" % (datetime.datetime.now().strftime("-%Y-%m-%d-%H-%M-%S"))


# header = ['序号','日期','时间','身高','性别','年龄','体重','阻抗','脂肪率','time interval','last weight','last bfr','用户识别','测量模式']
# sex:0,age:25,high:1650,weight:5090  8,9,10,11
# res:0 last:0 0 0
