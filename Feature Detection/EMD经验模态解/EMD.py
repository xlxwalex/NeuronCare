import numpy as np
import pandas as pd
from sklearn import datasets
import matplotlib.pyplot as plt
from pyhht.emd import EMD
from pyhht.visualization import plot_imfs
from scipy.io import loadmat
import scipy.io as sio

#载入时间序列数据
m = loadmat("/Users/xulvxiaowei/Documents/GitHub/NeuronCare/EDFParser/FP1-F7.mat")
data = m['NotIllData']
#EMD经验模态分解
data = data[0]
decomposer = EMD(data)
imfs = decomposer.decompose()
#绘制分解图
#plot_imfs(data,imfs,data.tolist().index)
#保存IMFs
#arr = np.vstack((imfs,data[0]))
#dataframe = pd.DataFrame(arr.T)
#dataframe.to_csv('D:/imf.csv',index=None,columns=None)
sio.savemat('EMDRESULT',{'IMF1':imfs[0],'IMF2':imfs[1],'IMF3':imfs[2]})
