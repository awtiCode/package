- This is to show you step by step guide for filling missed Rainfall Data using three methods (`Mean`, `IDW`, and `Normal Ration`) methods
  
- Simply download this manual [Sample.pdf](https://github.com/user-attachments/files/15845951/Sample.pdf)


## **Steps To Follow**

### **Step-1: Install the package**
- Open your terminal (*anaconda prompt*) and install both `git` and `awtiCode` package
```
conda install git
```
```
pip install git+https://github.com/awtiCode/package.git
```
### **Step-2: Import awtiCode package**

#### **Step-2.1: This is specifically for data loading**

```
from awtiCode.loadData import *
```
#### **Step-2.2: This is specifically for filling of loaded data**

```
from awtiCode.fillMissing import *
```

### **Step-3: Load your data**
- Assuming that you have the file named `emi22.csv` in the same directory.
#### **Step-3.1: Data loading as per your request**

- Give the path first and here you are expected to load `PRECIP` from `emi22.csv` file, and you station column_name is `station`
- Request the data .csv data from here [Demiso, Awel, Jdd, ](demo.nkmt1@gmail.com)

```
file_path = 'emi22.csv'
```
```
data = dataLoad(file_path, element='PRECIP', stations_col='station')
```

#### **Step-3.2: Load coordinates Specifically for IDW**
- We need to have a coordinate to calculate a distance between each stations

```
coord = coordDataLoad(file_path)
```

### **Step-4: Fill missig datas**

- This is to fill a missing rainfall data using three methods
- Namely: IDW , MEAN , and Normal Ratio


#### **Step-4.1:Fill using Arithemetic method**
```
filled_arithmetic = fill_missing_data_arithmetic(data)
```
#### **Step-4.2:Fill using Normal Ratio method**
```
filled_normal_ratio = fill_missing_data_normal_ratio(data)
```
#### **Step-4.3:Fill using IDW method**
```
filled_IDW = fill_missing_data_inverse_distance(data, coord)
```
