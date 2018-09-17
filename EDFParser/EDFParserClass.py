#EDF文件解析器  - xlxw 2018.9.12
#EDF PARSER CLASS
#2018.9.17 ADD [DataSetCreate format For Matlab]
#-----------------------------------------------------------------------------
import os
import numpy as np
import random
import scipy.io as sio

#定义一个EDF CLASS
class EDFData:
    import os
    import numpy as np
    import random
    import scipy.io as sio
    
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
        self.Data          = []        #EDF中存储的各个通道EEG信息‘

    #计算EDF+中的float缩放比例和基准
    def ScaleCal(self,HdrData):
        ScaleLs = []
        DCLs    = []
        for i in range(0,HdrData.ChannelNum):
            TmpDataScale = (HdrData.Maximum[i]-HdrData.Minimum[i])/(HdrData.DigitMaximum[i]-HdrData.DigitMinimum[i])
            TmpDataDC    = (HdrData.Maximum[i]-TmpDataScale*HdrData.DigitMaximum[i])
            ScaleLs.append(TmpDataScale)
            DCLs.append(TmpDataDC)
        return ScaleLs,DCLs

    #完成16bit Byte数据转换为 float
    def ByteHexToDec(self,HexByte,Scale,DC,Tag):
        HexSInt   = int.from_bytes(HexByte,byteorder = 'little',signed = True)
        ParseData = HexSInt * Scale[Tag] + DC[Tag]
        return ParseData

    #Header通道列表部分数据解析
    def EDFHeadChanel(self,TmpEDFFile,Channel,Length,DataTag):
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

    #数据存储为CSV
    def EDFDataToCSV(self,EEGData,path):
        np.set_printoptions(precision=4)
        np.savetxt(path, EEGData, delimiter = ',')
    
    #EDF数据解析
    def EDFDataParse(self,TmpEDFFile,Data,ScaleLs,DCLs):
        TmpDataLs  = []
        TimeSpan = Data.SampleFrequen[0] * Data.DataTimeL
        TmpDataALs = np.ones((Data.ChannelNum,TimeSpan))
        for i in range(0,Data.DataTimeL):
            for j in range(0,Data.ChannelNum):
                for q in range(0,Data.SampleFrequen[j]):
                    TmpDataStr = TmpEDFFile.read(2)
                    TmpByte    = TmpDataStr.lstrip()
                    TmpByte    = TmpByte.rstrip()
                    TmpDataALs[j,i*Data.SampleFrequen[j] + q] = (EDFData.ByteHexToDec(self,TmpByte,ScaleLs,DCLs,j))
        return TmpDataALs

    #EDF切分为可训练数据集
    def EDF2DataSet(self,Start,End,Data,Duration,Channel,Val):
        #Start为癫痫发生时间(s) End为癫痫截止时间(s) Data为解析的数据
        #Duration为时间间隔(s) Channel 通道       Val为所需要的数据总数[非病,病前,病](s)
        if Channel not in list(np.linspace(0,Data.ChannelNum,Data.ChannelNum)):
            print('无可用需要采集的通道')
            return
        for i in Channel:
            print('正在采集电极通道 [{}] 的数据'.format(Data.ChanelLabel[i]))
            #按秒切片
            Sample     = Data.SampleFrequen[i]
            TmpData    = np.reshape(Data.Data[i],(EDFDataOut.DataTimeL,Duration))
            DataLength = [End - Start,Start - Val[1] + EDFDataOut.DataTimeL - End,Val[1]]
            #顺序为[病,非病,病前]
            TmpNIllData= np.insert(TmpData[0:Start -Val[1],:],-1,TmpData[End:EDFDataOut.DataTimeL,:],0)
            TmpILLData = TmpData[Start:End,:]
            TmpBILLData= TmpData[Start-Val[1]:Start,:]
            if Val[0] > DataLength[1] or Val[0] > DataLength[1] or Val[0] > DataLength[1]:
                print('输入的需求数据超过最大上限')
                return
            #随机取出数据作为数据集
            IllRandLab = random.sample(range(0,DataLength[0]),Val[2])
            NIllRandLab= random.sample(range(0,DataLength[1]),Val[0])
            BIllRandLab= random.sample(range(0,DataLength[2]),Val[1])
            IllData    = TmpILLData [IllRandLab,:]
            BIllData   = TmpBILLData[BIllRandLab,:]
            NIllData   = TmpNIllData[NIllRandLab,:]
            #存储为.m文件
            sio.savemat(str(Data.ChanelLabel[i])+str(' [Data]'),{'IllData':IllData,'BeforIllData':BIllData,'NotIllData':NIllData})
            print('生成完成，文件名为:[{}]'.format(str(Data.ChanelLabel[i])+str(' [Data]')+str('.mat')))

    #EDF解析器
    def EDFParser(self,path):
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
        Data.ChanelLabel  = EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,16,False)
        Data.ElectrodeType= EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,80,False)
        Data.Dimension    = EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,8,False)
        Data.Minimum      = EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,8,True)
        Data.Maximum      = EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,8,True)
        Data.DigitMinimum = EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,8,True)
        Data.DigitMaximum = EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,8,True)
        Data.Prefilter    = EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,80,False)
        Data.SampleFrequen= EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,8,True)
        EDFData.EDFHeadChanel(self,EDFFile,Data.ChannelNum,32,False)
        print('尝试解析数据部分..')
        #计算EDF的缩放和基准
        ScaleLs,DCLs      = EDFData.ScaleCal(self,Data)
        #解析EDF文件的数据部分
        Data.Data = EDFData.EDFDataParse(self,EDFFile,Data,ScaleLs,DCLs)
        EDFFile.close()
        Data.Tag = True
        return Data
    
if __name__ == '__main__':
    EDFDataGet = EDFData()
    EDFDataOut = EDFDataGet.EDFParser("/Users/xulvxiaowei/Downloads/chb01_03.edf")
    #EDFDataGet.EDFDataToCSV(EDFDataOut.Data,'EEGData.csv')
    EDFDataOut.EDF2DataSet(2996,3036,EDFDataOut,256,[0],[500,20,30])
    print('数据导出完成')
