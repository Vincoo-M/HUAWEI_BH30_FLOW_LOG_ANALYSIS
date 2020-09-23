from constant import *
import time

# FLOW LOG LEVEL ANALYSIS
def level(level_data):
    if level_data == LOG_FLOW_LEVEL_FATAL:
        string = 'Fatal'
    elif level_data == LOG_FLOW_LEVEL_ERROR:
        string = 'Error'
    elif level_data == LOG_FLOW_LEVEL_WARN:
        string = 'Warn'
    elif level_data == LOG_FLOW_LEVEL_INFO:
        string = 'Info'
    elif level_data == LOG_FLOW_LEVEL_DEBUG:
        string = 'Debug'
    else:
        string = 'Flow log level error'
    return string

# FLOW LOG MODE ANALYSIS
def mode(mode_data):
    if 0 <= mode_data <= 15:
        string = MODE_BLE
    elif 16 <= mode_data <= 31:
        string = MODE_WIFI
    else:
        string = 'Flow log mode error'
    return string

# FLOW LOG TIME ANALYSIS
def time_(timeStamp_data):
    timeArray = time.localtime(timeStamp_data)
    date = time.strftime("%Y-%m-%d", timeArray)
    time_ = time.strftime("%H:%M:%S", timeArray)
    return date, time_

# FLOW LOG ADDRESS ANALYSIS
def addr(address_data, addr_offset, f_bin):
    address = address_data - addr_offset
    if address < 0:
        string = 'Flow log address error'
    elif address >= len(f_bin):
        string = 'Flow log address error'
    else:
        try:
            buf = {}
            s = 0
            while (f_bin[address] != 0x00):
                if f_bin[address] != 0x0a and f_bin[address] != 0x0d:
                    buf[s] = f_bin[address]
                address += 1
                s += 1
            buf_temp1 = bytes(buf.values())
            string = buf_temp1.decode()
        except Exception as e:
            string = 'Analysis error -> 0x{:02X}'.format(address_data)
    return string

# FLOW LOG PARA_1 ANALYSIS
def fileIndexAndLineNum(para1_data):
    index = para1_data >> 16
    lineNum = para1_data & 0x0000FFFF
    string = ('%d' % index), ('%d' % lineNum)
    return string

# FLOW LOG PARA_2/3/4/5 ANALYSIS
def para2_5(para2_data, para3_data, para4_data, para5_data):
    string = ('%d' % para2_data), ('%d' % para3_data), ('%d' % para4_data), ('%d' % para5_data)
    return string