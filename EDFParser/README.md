# NeuronCare
基于FPGA的癫痫预测平台设计

## EDF Parser Class
>本模块的作用是用于解析存储 EEG,ECG的EDF/EDF+文件，并还原其中的头部以及数据
>
>The function of this module is to parse and store the EDF / EDF + files of EEG and ECG, and restore the header and data.

## 依赖库 Library Dependencies
>os
>
>numpy
>
>random
>
>scipy.io

## 使用方法 Usage method
1.数据解析 
>1-设EDFDataOut专门用于存储Data

>2-EDFData()为类的名字

1.实例化类
```
EDFDataGet = EDFData()  
EDFDataOut = EDFDataGet.EDFParser("XXX.edf")
```
2.数据的CSV形式存储
```
EDFDataGet.EDFDataToCSV(EDFDataOut.Data,'XXX.csv')
```

3.将数据按要求切片，并最后将数据输出为.mat文件
```
EDF2DataSet(self,Start,End,Data,Duration,Channel,Val)
#EDFDataGet.EDF2DataSet(StartTime,EndTime,Structer Of Data,Sample Frequency,Electrode number,[Not Ill Time,Befor Ill Time,Ill Time])

#Start为癫痫发生时间(s)   End为癫痫截止时间(s)   Data为解析的数据
#Duration为时间间隔(s)   Channel 通道          Val为所需要的数据总数[非病,病前,病](s)


example:
EDFDataOut.EDF2DataSet(2996,3036,EDFDataOut,256,[0],[500,20,30])
```

## 输出效果 OutPut Effect
1.输出为.mat后显示的癫痫脑电波数据
![avatar](http://ol7p21r3m.bkt.clouddn.com/%E7%99%AB%E7%97%AB%E8%84%91%E7%94%B5%E7%89%B9%E5%BE%81.png)