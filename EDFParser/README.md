# NeuronCare
基于FPGA的癫痫预测平台设计

## EDF Parser Class
>本模块的作用是用于解析存储 EEG,ECG的EDF/EDF+文件，并还原其中的头部以及数据
>
>The function of this module is to parse and store the EDF / EDF + files of EEG and ECG, and restore the header and data.

## 使用方法 Usage method
1.数据解析 
>1-设EDFDataOut专门用于存储Data

>2-EDFData()为类的名字

```
EDFDataGet = EDFData()  
EDFDataOut = EDFDataGet.EDFParser("XXX.edf")
```
2.数据的CSV形式存储
```
EDFDataGet.EDFDataToCSV(EDFDataOut.Data,'EEGData.csv')
```
