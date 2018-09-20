# NeuronCare
基于FPGA的癫痫预测平台设计

## 近似熵模型 ApEn Model
>本模型的用处是通过算法提取癫痫的脑电波特征(通过近似熵)
>
>The purpose of this model is to extract the characteristics of epileptic brain waves (approximate entropy) by means of algorithm.
>
>算法来自WikiPedia

## 使用原因 Cause of use This Model
对于eeg信号来说，由于噪声存在、和信号的微弱性、多重信号源叠加，反映出来的是混沌属性，但是同一个人在大脑活动相对平稳的情况下，其eeg近似熵应该变化不大


## 依赖库 Library Dependencies
>numpy

## 使用方法 Usage method
```

ApEn(DATA, M, R))

```

### 示意图
![avatar](http://ol7p21r3m.bkt.clouddn.com/ApEn.png)

## 结论
根据定义，ApEn模型反映了时间序列中新信息发生的可能性，越复杂的时间序列对应的近似熵越大，由于在非癫痫时脑电波没有产生明显的新信息，所以ApEn值较小，而在癫痫前的时间，由于肯定有新信息的产生，所以此时的ApEn值反而会大于癫痫时期，故为图上的结果；将此特征作为癫痫预测的检测标志之一是完备的
