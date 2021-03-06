# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j8jbt9pSb4aHeC1bioFiXIg7c8KIFgFa
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from matplotlib import pyplot as plt
import seaborn as sns
import csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
from sklearn import preprocessing
from sklearn.model_selection import TimeSeriesSplit
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
import gc
import sys
# %matplotlib inline

"""# Importing Data"""

from google.colab import drive
drive.mount('/content/drive')
#pls specify your filepath here for the import of training data
filepath = '/content/drive/My Drive/Colab Notebooks/train.csv'

#predefine some of the data type, for memory efficiency 
type_dict={'ncodpers':np.int32, 'ind_ahor_fin_ult1':np.uint8, 'ind_aval_fin_ult1':np.uint8, 
       'ind_cco_fin_ult1':np.uint8,'ind_cder_fin_ult1':np.uint8,
            'ind_cno_fin_ult1':np.uint8,'ind_ctju_fin_ult1':np.uint8,'ind_ctma_fin_ult1':np.uint8,
            'ind_ctop_fin_ult1':np.uint8,'ind_ctpp_fin_ult1':np.uint8,'ind_deco_fin_ult1':np.uint8,
            'ind_deme_fin_ult1':np.uint8,'ind_dela_fin_ult1':np.uint8,'ind_ecue_fin_ult1':np.uint8,
            'ind_fond_fin_ult1':np.uint8,'ind_hip_fin_ult1':np.uint8,'ind_plan_fin_ult1':np.uint8,
            'ind_pres_fin_ult1':np.uint8,'ind_reca_fin_ult1':np.uint8,'ind_tjcr_fin_ult1':np.uint8,
            'ind_valo_fin_ult1':np.uint8,'ind_viv_fin_ult1':np.uint8,
            'ind_recibo_ult1':np.uint8 }

limit_rows = 700000
df = pd.read_csv(filepath, dtype=type_dict  , nrows = limit_rows ,parse_dates=['fecha_dato', 'fecha_alta'])

df.head()

def rename_columns(data):
    data.rename(columns = {"fecha_dato":"time_series","ncodpers":"customer_code","ind_empleado":"employee_index",\
                       "pais_residencia":"country_residence","sexo":"gender","fecha_alta":"Date_First_Customer",\
                       "ind_nuevo":"New_Customer_ind","antiguedad":"Seniority","indrel":"primary_cust",\
                       "ult_fec_cli_1t":"last_date_primary","indrel_1mes":"customer_type","tiprel_1mes":"cust_rel_type",\
                       "indresi":"residence_index","indext":"foriegn_index","conyuemp":"spouse_index","canal_entrada":"channel_by_cust_joined",\
                       "indfall":"deceased_index","tipodom":"primary_address","cod_prov":"province_code","nomprov":"province_name",\
                       "ind_actividad_cliente":"activity_index","renta":"gross_income","segmento":"segmentation",\
                       "ind_ahor_fin_ult1":"savings_account","ind_aval_fin_ult1":"guarantees","ind_cco_fin_ult1":"current_account",\
                       "ind_cder_fin_ult1":"derivative_account","ind_cno_fin_ult1":"payroll_account","ind_ctju_fin_ult1":"jnr_account",\
                       "ind_ctma_fin_ult1":"mas_particular_account","ind_ctop_fin_ult1":"particular_account","ind_ctpp_fin_ult1":"particular_Plus_Account",\
                       "ind_deco_fin_ult1":"short_term_deposits","ind_deme_fin_ult1":"medium_term_deposits",\
                       "ind_dela_fin_ult1":"long_term_deposits","ind_ecue_fin_ult1":"e_account","ind_fond_fin_ult1":"funds",\
                       "ind_hip_fin_ult1":"mortgage","ind_plan_fin_ult1":"pensions","ind_pres_fin_ult1":"loans",\
                       "ind_reca_fin_ult1":"taxes","ind_tjcr_fin_ult1":"credit_card","ind_valo_fin_ult1":"securities",\
                       "ind_viv_fin_ult1":"home_account","ind_nomina_ult1":"payroll","ind_nom_pens_ult1":"pensions1",
                       "ind_recibo_ult1":"direct_debit"},inplace=True)

rename_columns(df)


output_cols = ["savings_account","guarantees","current_account","derivative_account",\
           "payroll_account","jnr_account","mas_particular_account","particular_account",\
           "particular_Plus_Account","short_term_deposits","medium_term_deposits","long_term_deposits",\
           "e_account","funds","mortgage","pensions",\
            "loans","taxes","credit_card","securities",\
            "home_account","payroll","pensions1","direct_debit"]

feature_cols = []
for col in df.columns:
  if(col not in output_cols):
    feature_cols.append(col)


train_cols = feature_cols + output_cols

train = df.filter(train_cols)

train.head()

"""# Null Values and Correlation"""

#Function to get a sorted correlation plot, based on the target column specified ( decreasing)
def CorrPlotLargest(df, target):
    k = 10
    numerical_feature_columns = list(df._get_numeric_data().columns)
    cols = df[numerical_feature_columns].corr().nlargest(k, target)[target].index
    cm = df[cols].corr()
    plt.figure(figsize=(10,6))
    return sns.heatmap(cm, annot=True, cmap = 'viridis')

#Function to get a sorted correlation plot, based on the target column specified (increasing)
def CorrPlotSmallest(df, target):
    k = 10
    numerical_feature_columns = list(df._get_numeric_data().columns)
    cols = df[numerical_feature_columns].corr().nsmallest(k-1, target)[target].index
    cols = cols.insert(0,target)
    cm = df[cols].corr()
    plt.figure(figsize=(10,6))
    return sns.heatmap(cm, annot=True, cmap = 'viridis')

null_values = train.isnull().sum() * 100 / len(train)
null_values.sort_values(ascending = False)

train[['cust_rel_type','customer_type']].value_counts()

"""Now in the above plot we can see that 2 of the columns have 99% empty entries, so we just drop them right away and we can predict the renta based on the columns its most correlated with, and the ones we think imply some causality as well."""

train.primary_address.unique()
#Only one unique value for the column primary_address

CorrPlotLargest(df[feature_cols],'gross_income')

#This function is a representation of how many times are the user entries present.
train['customer_code'].value_counts()

del df

"""## Some initial Product Count analysis"""

output_cols = pd.read_csv(filepath, dtype='float16', 
                    usecols=['ind_ahor_fin_ult1', 'ind_aval_fin_ult1', 
                             'ind_cco_fin_ult1', 'ind_cder_fin_ult1',
                             'ind_cno_fin_ult1', 'ind_ctju_fin_ult1',
                             'ind_ctma_fin_ult1', 'ind_ctop_fin_ult1',
                             'ind_ctpp_fin_ult1', 'ind_deco_fin_ult1',
                             'ind_deme_fin_ult1', 'ind_dela_fin_ult1',
                             'ind_ecue_fin_ult1', 'ind_fond_fin_ult1',
                             'ind_hip_fin_ult1', 'ind_plan_fin_ult1',
                             'ind_pres_fin_ult1', 'ind_reca_fin_ult1',
                             'ind_tjcr_fin_ult1', 'ind_valo_fin_ult1',
                             'ind_viv_fin_ult1', 'ind_nomina_ult1',
                             'ind_nom_pens_ult1', 'ind_recibo_ult1'])

"""From the above data we can see that most of the customers have the entries for the entirity of 16 months , we ahve a small peak on 10 months as well could be something useful"""

train.head()

amount_bought = output_cols.astype('float64').sum(axis = 0)

amount_bought

plt.figure(figsize = (8,4))
amount_bought.values

sns.barplot(amount_bought.index,amount_bought.values)
plt.xticks(rotation='vertical')



"""Looking at this we can see that the  most bought item from the banks are the corrent accounts (ind_cco_fin_ult1) and the least bought is Guarentees (ind_aval_fin_ult1)

# Date of Joining and Date of recording of data EDA
"""

train = pd.read_csv(filepath,usecols=['fecha_dato','fecha_alta'],parse_dates=['fecha_dato','fecha_alta'])

#Creating a new column for the year + month of observation each employee_index
train['fecha_dato_yearmonth'] = train['fecha_dato'].apply(lambda x: (100*x.year) + x.month)
yearmonth = train['fecha_dato_yearmonth'].value_counts()

#A plot of the number of employee index per time_series datapoint
plt.figure(figsize=(8,4))
sns.barplot(yearmonth.index, yearmonth.values, alpha=0.8)
plt.xlabel('Year and month of observation', fontsize=12)
plt.ylabel('Number of customers', fontsize=12)
plt.xticks(rotation='vertical')
plt.show()

"""So we can see here that the distrubtion was quite similar during the first half of the year but after the 6th month there was a significant increase in the amount of customers, which then ever slightly increased till the next year as well. Maybe some scheme launched by us, or some specific reason other than seasonal caused this as the effects were permanent even through till the next year."""

#Creating a new column for the year + month of joining each employee_index
train['fecha_alta_yearmonth'] = train['fecha_alta'].apply(lambda x: (100*x.year) + x.month)
yearmonth = train['fecha_alta_yearmonth'].value_counts()
plt.figure(figsize=(15,4))

#A plot of the number of employee index per data joining grouped over datapoints
sns.barplot(yearmonth.index, yearmonth.values, alpha=0.8)
plt.xlabel('Year and month of joining', fontsize=12)
plt.ylabel('Number of customers', fontsize=12)
plt.xticks(rotation='vertical')
plt.show()

#A closer look at the above plot at the end of the years
year_month = yearmonth.sort_index().reset_index()
year_month = year_month.iloc[185:]
year_month.columns = ['yearmonth', 'number_of_customers']

plt.figure(figsize=(12,4))
sns.barplot(year_month.yearmonth.astype('int'), year_month.number_of_customers, alpha=0.8)
plt.xlabel('Year and month of joining', fontsize=12)
plt.ylabel('Number of customers', fontsize=12)
plt.xticks(rotation='vertical')
plt.show()

"""So it seems that the account contracts for the customers have been there from since 1995 and there seems to be an increase in the start date of account contracts in the later stages with a  more seasonal peak (from july to december)."""

del train

"""# Age EDA"""

train = pd.read_csv(filepath, usecols=['age'])
train.head()

train.age.unique()

train[train.age == " NA"] = np.nan
train['age'] = train['age'].astype('float64')

# A plot for the number of customer per age category (outliers detected in this)
age_series = train.age.value_counts()
age_series = age_series.sort_index()
plt.figure(figsize=(20,4))
sns.barplot(age_series.index, age_series.values, alpha=0.8)
plt.ylabel('Number of Occurrences of the customer', fontsize=12)
plt.xlabel('Age', fontsize=12)
plt.xticks(rotation='vertical')
plt.show()

"""So most of our cutomers are between the age 20-24 and then there is some middle aged peole as well, so we can maybe remove the age gp below 20 and > 90 as it is only becoming a long tail. Also for the NaN values, we can use mean imputation technique (not a very good or preffered technique though) , to increase the dataset size.

Mean imputation refers to replacing the null values with the mean value to make it more biased towards the higher values in the dataset
"""

train.age.isnull().sum()

train.age.mean()

del train

"""# Seniority EDA"""

#Customer seniority in months - understood as for how many months has he/she been there customers
train = pd.read_csv(filepath, usecols=['antiguedad'])
train.head()

train.antiguedad.unique()

#Preprocessing for antiguedad
train['antiguedad'] = train['antiguedad'].replace(to_replace=['     NA'], value=np.nan)
train[train['antiguedad'] == -999999.0]['antiguedad'] == 0
train['antiguedad'] = train['antiguedad'].astype('float64')

#A plot of number of customers vs antiguedad(or seniority)
col_series = train.antiguedad.value_counts()
col_series = col_series.sort_index()
plt.figure(figsize=(20,4))
sns.barplot(col_series.index, col_series.values, alpha=0.8 )
plt.ylabel('Number of Occurrences of the customer', fontsize=12)
plt.xlabel('Customer Seniority', fontsize=12)
plt.xticks(rotation='vertical')
plt.show()

"""# Gross Income EDA"""

#renta = gross dometic income
train = pd.read_csv(filepath, usecols=['renta'])
train.head()

unique_values = np.sort(train.renta.unique())
plt.scatter(range(len(unique_values)), unique_values)
plt.show()

"""This data doesnt seem right seems very skewed might be due to some very weatlhy outliers lets see"""

train.renta.mean()

train.renta.median()

train.renta.isnull().sum()

#Seeing how the log transformation affects it
fig, ax = plt.subplots(figsize=(30,15))
sample_df = pd.DataFrame()
sample_df['renta'] = train['renta']
sample_df['renta'] = np.log(sample_df['renta'])
train['renta'].hist(color='plum', edgecolor='black',  
                          grid=False, bins= 100)
ax.set_title('Gross Income bins', fontsize=12)
ax.set_xlabel('Income', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
fig, ax = plt.subplots(figsize=(30,15))
sample_df['renta'].hist(color='plum', edgecolor='black',  
                          grid=False, bins= 100)
ax.set_title('Gross Income bins', fontsize=12)
ax.set_xlabel('Income', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)

#Plotting quartile range vs gross income to see presence of outliers
train.fillna(101850., inplace=True) #filling NA as median for now
quantile_series = train.renta.quantile(np.arange(0.99,1,0.001))
plt.figure(figsize=(12,4))
sns.barplot((quantile_series.index*100), quantile_series.values, alpha=0.8)
plt.ylabel('Rent value', fontsize=12)
plt.xlabel('Quantile value', fontsize=12)
plt.xticks(rotation='vertical')
plt.show()

"""So you can see that there is a huge gap between the 99.9 percentile of rent amount and 100 percentile"""

del train

"""# Product Analysis"""

#predefine some of the data type, for memory efficiency 
type_dict={'ncodpers':np.int32, 'ind_ahor_fin_ult1':np.uint8, 'ind_aval_fin_ult1':np.uint8, 
       'ind_cco_fin_ult1':np.uint8,'ind_cder_fin_ult1':np.uint8,
            'ind_cno_fin_ult1':np.uint8,'ind_ctju_fin_ult1':np.uint8,'ind_ctma_fin_ult1':np.uint8,
            'ind_ctop_fin_ult1':np.uint8,'ind_ctpp_fin_ult1':np.uint8,'ind_deco_fin_ult1':np.uint8,
            'ind_deme_fin_ult1':np.uint8,'ind_dela_fin_ult1':np.uint8,'ind_ecue_fin_ult1':np.uint8,
            'ind_fond_fin_ult1':np.uint8,'ind_hip_fin_ult1':np.uint8,'ind_plan_fin_ult1':np.uint8,
            'ind_pres_fin_ult1':np.uint8,'ind_reca_fin_ult1':np.uint8,'ind_tjcr_fin_ult1':np.uint8,
            'ind_valo_fin_ult1':np.uint8,'ind_viv_fin_ult1':np.uint8,
            'ind_recibo_ult1':np.uint8 }

limit_rows = 700000
df = pd.read_csv(filepath, dtype=type_dict  , nrows = limit_rows ,parse_dates=['fecha_dato', 'fecha_alta'])

df.head()

train = pd.read_csv('/content/drive/My Drive/Colab Notebooks/train.csv', nrows=100000)
target_cols = ['ind_cco_fin_ult1', 'ind_cder_fin_ult1',
                             'ind_cno_fin_ult1', 'ind_ctju_fin_ult1',
                             'ind_ctma_fin_ult1', 'ind_ctop_fin_ult1',
                             'ind_ctpp_fin_ult1', 'ind_deco_fin_ult1',
                             'ind_deme_fin_ult1', 'ind_dela_fin_ult1',
                             'ind_ecue_fin_ult1', 'ind_fond_fin_ult1',
                             'ind_hip_fin_ult1', 'ind_plan_fin_ult1',
                             'ind_pres_fin_ult1', 'ind_reca_fin_ult1',
                             'ind_tjcr_fin_ult1', 'ind_valo_fin_ult1',
                             'ind_viv_fin_ult1', 'ind_nomina_ult1',
                             'ind_nom_pens_ult1', 'ind_recibo_ult1']
train[target_cols] = (train[target_cols].fillna(0))
train["age"] = train['age'].map(str.strip).replace(['NA'], value=0).astype('float')
train["antiguedad"] = train["antiguedad"].map(str.strip)
train["antiguedad"] = train['antiguedad'].replace(['NA'], value=0).astype('float')

train[train["antiguedad"]>65] = 65 # there is one very high skewing the graph
train[train["renta"]>1e6] = 1e6 # capping the higher values for better visualisation
train.fillna(-1, inplace=True)

df['age']=pd.to_numeric(df.age, errors='coerce')

df.rename(columns = {"fecha_dato":"time_series","ncodpers":"customer_code","ind_empleado":"employee_index",\
                       "pais_residencia":"country_residence","sexo":"gender","fecha_alta":"Date_First_Customer",\
                       "ind_nuevo":"New_Customer_ind","antiguedad":"Seniority","indrel":"primary_cust",\
                       "ult_fec_cli_1t":"last_date_primary","indrel_1mes":"customer_type","tiprel_1mes":"cust_rel_type",\
                       "indresi":"residence_index","indext":"foriegn_index","conyuemp":"spouse_index","canal_entrada":"channel_by_cust_joined",\
                       "indfall":"deceased_index","tipodom":"primary_address","cod_prov":"province_code","nomprov":"province_name",\
                       "ind_actividad_cliente":"activity_index","renta":"gross_income","segmento":"segmentation",\
                       "ind_ahor_fin_ult1":"savings_account","ind_aval_fin_ult1":"guarantees","ind_cco_fin_ult1":"current_account",\
                       "ind_cder_fin_ult1":"derivative_account","ind_cno_fin_ult1":"payroll_account","ind_ctju_fin_ult1":"jnr_account",\
                       "ind_ctma_fin_ult1":"mas_particular_account","ind_ctop_fin_ult1":"particular_account",\
                       "ind_deco_fin_ult1":"short_term_deposits","ind_deme_fin_ult1":"medium_term_deposits",\
                       "ind_dela_fin_ult1":"long_term_deposits","ind_ecue_fin_ult":"e_account1","ind_fond_fin_ult1":"funds",\
                       "ind_hip_fin_ult1":"mortgage","ind_plan_fin_ult1":"pensions1","ind_pres_fin_ult1":"loans",\
                       "ind_reca_fin_ult1":"taxes","ind_tjcr_fin_ult1":"credit_card","ind_valo_fin_ult1":"securities",\
                       "ind_viv_fin_ult1":"home_account","ind_nomina_ult1":"payroll","ind_nom_pens_ult1":"pensions2",
                       "ind_recibo_ult1":"direct_debit","ind_ecue_fin_ult1":"e_account2"},inplace=True)



output_cols = ["savings_account","guarantees","current_account","derivative_account",\
           "payroll_account","jnr_account","mas_particular_account","particular_account",\
           "short_term_deposits","medium_term_deposits","long_term_deposits",\
           "long_term_deposits","e_account1","funds","mortgage","pensions1",\
           "loans","taxes","credit_card","securities","home_account","payroll","pensions2",\
           "direct_debit","e_account2"]

feature_cols = []
for col in df.columns:
  if(col not in output_cols):
    feature_cols.append(col)

#A plot of the different age groups over different products
fig, axes = plt.subplots(nrows=5, ncols=5, figsize=(15,20))
plt.subplots_adjust(wspace=1.3, hspace=0.6)
fig_row=0
for col_id in range(24, 48):
    ax_id=col_id-24
    fig_label=df.columns[col_id]
    feat=df.columns[col_id]
    fig_col=(col_id+1)%5
    print(df[feat].value_counts())
    box_plot=sns.violinplot(y='age', data=df[(df[feat] == 1) & (df['age'] > 0) & (df['age'] < 100)], ax=axes[fig_row][fig_col],split=True, hue= 'gender')
    box_plot.set(xlabel=fig_label)
    if fig_col==4: 
      fig_row+=1

data = df[(df[feat] == 1) & (df['age'] > 0) & (df['age'] < 100)]

#A plot of how products are bought over different provinces vary
fig, axes = plt.subplots(nrows=8, ncols=3, figsize=(9,18))
plt.subplots_adjust(wspace=0.4, hspace=0.6)
fig_row=0
for col_id in range(24, 48):
    ax_id=col_id-24
    fig_label= df.columns[col_id]
    feat=df.columns[col_id]
    fig_col=col_id%3
    sns.distplot(df.province_code[(df[feat]==1) & (df['province_code']>=0)], kde=False, 
                 axlabel=fig_label, ax=axes[fig_row][fig_col])
    if fig_col==2: 
      fig_row+=1

train_cols = feature_cols + output_cols

train = df.filter(train_cols)

train.head()

dummy_train = train[train['gender'].notna()]
from sklearn.preprocessing import LabelEncoder

lb_make = LabelEncoder()
dummy_train['gender'] = lb_make.fit_transform(dummy_train['gender'])
dummy_train['gender']
# H 2 
# V 3
dummy_train.customer_code.value_counts()

#A plot of how products bought by different genders vary

fig, axes = plt.subplots(nrows=8, ncols=3, figsize=(9,18))
plt.subplots_adjust(wspace=0.4, hspace=0.6)
fig_row=0

for col_id in range(24, 48):
    ax_id=col_id-24
    fig_label= df.columns[col_id]
    feat=df.columns[col_id]
    fig_col=col_id%3
    sns.distplot(dummy_train.gender[(df[feat]==1)], kde=False, 
                 axlabel=fig_label, ax=axes[fig_row][fig_col])
    if fig_col==2: 
      fig_row+=1

"""# Lag EDA Analysis

### Please see the other Lag notebook for this

# Doing Time Series analysis

> Indented block
"""

from pandas import datetime
#predefine some of the data type, for memory efficiency 
type_dict={'ncodpers':np.int32, 'ind_ahor_fin_ult1':np.uint8, 'ind_aval_fin_ult1':np.uint8, 
       'ind_cco_fin_ult1':np.uint8,'ind_cder_fin_ult1':np.uint8,
            'ind_cno_fin_ult1':np.uint8,'ind_ctju_fin_ult1':np.uint8,'ind_ctma_fin_ult1':np.uint8,
            'ind_ctop_fin_ult1':np.uint8,'ind_ctpp_fin_ult1':np.uint8,'ind_deco_fin_ult1':np.uint8,
            'ind_deme_fin_ult1':np.uint8,'ind_dela_fin_ult1':np.uint8,'ind_ecue_fin_ult1':np.uint8,
            'ind_fond_fin_ult1':np.uint8,'ind_hip_fin_ult1':np.uint8,'ind_plan_fin_ult1':np.uint8,
            'ind_pres_fin_ult1':np.uint8,'ind_reca_fin_ult1':np.uint8,'ind_tjcr_fin_ult1':np.uint8,
            'ind_valo_fin_ult1':np.uint8,'ind_viv_fin_ult1':np.uint8,
            'ind_recibo_ult1':np.uint8 }

# def parser(x):
# 	return datetime.strptime(x, '%Y-%m-%d')
 
df = pd.read_csv(filepath, dtype=type_dict ,parse_dates=['fecha_dato', 'fecha_alta'],squeeze=True)

rename_columns(df)

output_cols = ["savings_account","guarantees","current_account","derivative_account",\
           "payroll_account","jnr_account","mas_particular_account","particular_account",\
           "particular_Plus_Account","short_term_deposits","medium_term_deposits","long_term_deposits",\
           "e_account","funds","mortgage","pensions",\
            "loans","taxes","credit_card","securities",\
            "home_account","payroll","pensions1","direct_debit"]


# df.sort_values('Order Date')

df[output_cols]

df = df.groupby('time_series')[output_cols].sum()

'''
Plots of different output cols change with time
'''

sns.set()
fig, axes = plt.subplots(nrows=9, ncols=3, figsize=(33,66))
plt.subplots_adjust(wspace=0.4, hspace=0.6)
fig_row=0

for col in range(len(output_cols)):
  # print(output_cols)
  fig_col = col%3
  axes[fig_row][fig_col].plot(df.index,df[output_cols[col]].to_numpy())
  axes[fig_row][fig_col].set_xlabel(output_cols[col])
  axes[fig_row][fig_col].set_ylabel('Total Change in products')
  if fig_col==2: 
      fig_row+=1

from pandas import read_csv
from pandas import datetime
from pandas import DataFrame
from statsmodels.tsa.arima_model import ARIMA
from matplotlib import pyplot
 
def parser(x):
	return datetime.strptime('190'+x, '%Y-%m')
 
# series = read_csv('shampoo-sales.csv', header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)
# fit model
model = ARIMA(df['home_account'], order=(3,2,0))
model_fit = model.fit(disp=0)
print(model_fit.summary())
# plot residual errors
residuals = DataFrame(model_fit.resid)
residuals.plot()
pyplot.show()
residuals.plot(kind='kde')
pyplot.show()

"""Almost a gaussian error not bad . . ."""

from pandas import datetime
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
 
def parser(x):
	return datetime.strptime('190'+x, '%Y-%m')
 
# series = read_csv('shampoo-sales.csv', header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)

col = 'home_account'
X = df[col].values
# X

size = int(len(X) * 0.66)
train, test = X[0:size], X[size:len(X)]
# test
history = [x for x in train]
predictions = list()
# history

for t in range(len(test)):
	model = ARIMA(history, order=(0,1,0))
	model_fit = model.fit(disp=0)
	output = model_fit.forecast()
	yhat = output[0]
	predictions.append(yhat)
	obs = test[t]
	history.append(obs)
	print('predicted=%f, expected=%f' % (yhat, obs))
error = mean_squared_error(test, predictions)
print('Test MSE: %.3f' % error)
# plot
pyplot.plot(test)
pyplot.plot(predictions, color='red')
pyplot.show()

from statsmodels.tsa.seasonal import seasonal_decompose

sns.set()
fig_row=0
# Add the column here to indivdually check the seasonal decomposition of the specified column
col = 'payroll'

X = df[col].values
size = int(len(X) * 0.80)
train, test = X[0:size], X[size:len(X)]
# test
history = [x for x in train]

decomposition = seasonal_decompose(history, model='multiplicative',freq = 1)
trend    = decomposition.trend
seasonal = decomposition.seasonal
residual = decomposition.resid
print('\t \t\t' + col.upper())
decomposition.plot()
pyplot.show()

"""You will see that all of the products didn't show any new things in Seasonal or residual part averything which is observed comes out to be a trend which is not very helpful for us"""

#A plot of different columns via FFT we didn't complete this but we were trying different frequencies for a fft over our time series data

# Frequency and sampling rate
f = 10 # frequency
Fs = 100 # sampling rate

# Sine function
for col in output_cols:
  X = df[col].values
  size = int(len(X) * 0.80)
  train, test = X[0:size], X[size:len(X)]
  # test
  t = np.linspace(1,len(train),len(train))
  T = 1
  print(t)
  history = [x for x in train]
  # Perform Fourier transform using scipy
  from scipy import fftpack
  y_fft = fftpack.fft(history)
  # # Plot data
  # n = np.size(t)
  N = train.size
  fr = np.linspace(0,0.5 * (1/T),N)
  fr = fr * 1000
  
  below_cutoff = np.abs(y_fft) < 5.5
  y_fft[below_cutoff] = 0
  cleaner_signal = fftpack.ifft(y_fft)
  plt.plot(t,cleaner_signal)
  plt.plot(t,history)
  plt.show()

cleaner_signal