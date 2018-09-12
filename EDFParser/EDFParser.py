#EDF文件解析器  - xlxw 2018.9.12
#-----------------------------------------------------------------------------
#引用库
from ctypes import *
import os
import numpy as np

#定义一个EDF结构体
class EDFData:
    def __init__(self):
        #EDF Header
        self.Tag           = False
        self.FormatVer     = 0         #数据格式版本
        self.Patient       = ""        #患者身份指定码
        self.Identify      = ""        #EEG身份指定码
        self.YMD           = ""        #EDF文件生成年月日
        self.HMM           = ""        #EDF文件生成时分秒
        self.HeaderLen     = 0         #EDF Header长度
        self.DataTimeL     = 0         #EEG记录时间总长度
        self.DataDuration  = 0         #EEG的数据记录间隔(秒为单位)
        self.ChannelNum    = 0         #EDF文件中EEG使用的电极通道数量
        self.ChanelLabel   = []        #EDF每个通道的名字(电极标志)
        self.ElectrodeType = []        #EDF中每个通道电极的种类
        self.Dimension     = []        #EDF中每个通道电极的物理单位[uv,degreeC]
        self.Minimum       = []        #EDF中每个通道的电压最小值
        self.Maximum       = []        #EDF中每个通道的电压最大值
        self.DigitMinimum  = []        #EDF中每个通道的电子电压最小值
        self.DigitMaximum  = []        #EDF中每个通道的电子电压最大值
        self.Prefilter     = []        #EDF中的前置滤波
        self.SampleFrequen = []        #EDF中的采样频率
        self.Data          = []        #EDF中存储的各个通道EEG信息
        self.Test          = 0

#计算EDF+中的float缩放比例和基准
def ScaleCal(HdrData):
    ScaleLs = []
    DCLs    = []
    for i in range(0,HdrData.ChannelNum):
        TmpDataScale = (HdrData.Maximum[i]-HdrData.Minimum[i])/(HdrData.DigitMaximum[i]-HdrData.DigitMinimum[i])
        TmpDataDC    = (HdrData.Maximum[i]-TmpDataScale*HdrData.DigitMaximum[i])
        ScaleLs.append(TmpDataScale)
        DCLs.append(TmpDataDC)
    return ScaleLs,DCLs

#完成16bit Byte数据转换为 float
def ByteHexToDec(HexByte,Scale,DC,Tag):
    HexSInt   = int.from_bytes(HexByte,byteorder = 'little',signed = True)
    ParseData = HexSInt * Scale[Tag] + DC[Tag]
    return ParseData

#Header通道列表部分数据解析
def EDFHeadChanel(TmpEDFFile,Channel,Length,DataTag):
    TmpList = []
    TmpData = ""
    for i in range(0,Channel):
        if DataTag == True:
            TmpList.append(eval(TmpEDFFile.read(Length)))
        else:
            TmpData = TmpEDFFile.read(Length)
            TmpData = TmpData.lstrip()
            TmpData = TmpData.rstrip()
            TmpList.append(TmpData)
    return TmpList

#EDF数据解析
def EDFDataParse(TmpEDFFile,Data,ScaleLs,DCLs):
    TmpDataLs  = []
    TimeSpan = Data.SampleFrequen[0] * Data.DataTimeL
    TmpDataALs = np.ones((Data.ChannelNum,TimeSpan))
    for i in range(0,Data.ChannelNum):
        TmpDataLs = []
        for j in range(0,TimeSpan):
            TmpDataStr = TmpEDFFile.read(2)
            TmpByte    = TmpDataStr.lstrip()
            TmpByte    = TmpByte.rstrip()
            TmpDataLs.append(ByteHexToDec(TmpByte,ScaleLs,DCLs,i))
        TmpDataALs[i] = np.array(TmpDataLs)
        #TmpDataALs = np.append(TmpDataALs,np.array(TmpDataLs))
    #TmpDataALs.reshape(Data.ChannelNum,TimeSpan)
    return TmpDataALs
               
#EDF解析器
def EDFParser(path):
    print('正在尝试读取文件..')
    #例化一个EDFData结构体
    Data = EDFData()
    if os.path.exists(path) == False:
        print('读取失败,文件不存在')
        return Data
    #通过二进制读取EDF文件
    EDFFile = open(path,"rb+")
    print('尝试读取头部信息..')
    #解析EDF文件的头部
    Data.FormatVer    = eval(EDFFile.read(8))
    Data.Patient      = EDFFile.read(80)
    Data.Patient      = Data.Patient.lstrip()
    Data.Patient      = Data.Patient.rstrip()
    Data.Identify     = EDFFile.read(80)
    Data.Identify     = Data.Identify.lstrip()
    Data.Identify     = Data.Identify.rstrip()
    Data.YMD          = EDFFile.read(8)
    Data.HMM          = EDFFile.read(8)
    Data.HeaderLen    = eval(EDFFile.read(8))
    EDFFile.read(44)
    Data.DataTimeL    = eval(EDFFile.read(8))
    Data.DataDuration = eval(EDFFile.read(8))
    Data.ChannelNum   = eval(EDFFile.read(4))
    Data.ChanelLabel  = EDFHeadChanel(EDFFile,Data.ChannelNum,16,False)
    Data.ElectrodeType= EDFHeadChanel(EDFFile,Data.ChannelNum,80,False)
    Data.Dimension    = EDFHeadChanel(EDFFile,Data.ChannelNum,8,False)
    Data.Minimum      = EDFHeadChanel(EDFFile,Data.ChannelNum,8,True)
    Data.Maximum      = EDFHeadChanel(EDFFile,Data.ChannelNum,8,True)
    Data.DigitMinimum = EDFHeadChanel(EDFFile,Data.ChannelNum,8,True)
    Data.DigitMaximum = EDFHeadChanel(EDFFile,Data.ChannelNum,8,True)
    Data.Prefilter    = EDFHeadChanel(EDFFile,Data.ChannelNum,80,False)
    Data.SampleFrequen= EDFHeadChanel(EDFFile,Data.ChannelNum,8,True)
    EDFHeadChanel(EDFFile,Data.ChannelNum,32,False)
    print('尝试解析数据部分..')
    #计算EDF的缩放和基准
    (ScaleLs,DCLs)    = ScaleCal(Data)
    #解析EDF文件的数据部分
    Data.Data = EDFDataParse(EDFFile,Data,ScaleLs,DCLs)
    EDFFile.close()
    Data.Tag = True
    return Data

def main():
    EDFDataGet = EDFData()
    EDFDataGet = EDFParser("/Users/xulvxiaowei/Downloads/chb01_03.edf")
    if EDFDataGet.Tag == False:
        return
    print(EDFDataGet.Data)
    #print(StrHexToDec("\x01\x00\x00\x00"))

main()
    
    
