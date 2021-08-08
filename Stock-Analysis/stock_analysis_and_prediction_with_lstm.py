# -*- coding: utf-8 -*-
"""Stock Analysis and Prediction with LSTM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1E4wQUlD6NUqFFduUQqQDTAWKWYf9P0O_
"""

!pip install yfinance
!pip install plotly==4.5.2

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import yfinance as yf

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
plt.style.use("fivethirtyeight")
# %matplotlib inline

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import itertools

# For reading stock data from yahoo
from pandas_datareader.data import DataReader

# For time stamps
from datetime import datetime

stock_list = ['BABA', 'GOOG', 'MSFT', 'AMZN']
end = datetime.now()
start = datetime(end.year - 3, end.month, end.day)

for i in stock_list:
  src = yf.Ticker(i)
  globals()[i] = src.history(period='max', auto_adjust=True)
  globals()[i] = globals()[i][start:end]

BABA.info()

BABA.columns

"""#Membuat Fungsi Plot Price"""

company_list = [BABA, GOOG, MSFT, AMZN]
def plot_price (use_col):
  plt.figure(figsize=(15,8))
  for i, company in enumerate (company_list):
    plt.subplot(2,2,i+1)
    plt.suptitle(f"{use_col} Price")
    company[use_col].plot()
    plt.ylabel(stock_list[i])

"""MEMBUAT PLOT UNTUK CLOSE PRICE"""

plot_price('Close')

"""Plot Volume"""

plot_price('Volume')

"""#**MOVING AVERAGE FOR CLOSE**"""

ma_list = [21, 60, 120]
for company in company_list:
  for col  in ma_list:
    company[f'MA-{col}'] = company['Close'].rolling(col).mean()

ma_col = ['Close', 'MA-21', 'MA-60', 'MA-120']
def plot_ma(company_name):
  fig = go.Figure()
  for col in ma_col:
    fig.add_trace(go.Scatter(x=company_name.index, y=company_name[col],mode='lines', name=f'{col}'))
  fig.show()

plot_ma(GOOG)

"""CORRELATION BETWEEN STOCKS CLOSE PRICE"""

df_close = pd.DataFrame()
for company in stock_list:
  df_close[company] = globals()[company]['Close']
df_close = pd.DataFrame(df_close)

df_close.head()

#persentase selisih antar index 
stock_rets = df_close.pct_change()
stock_rets.head()

stock_rets.plot(figsize=(12,5))

sns.pairplot(stock_rets, kind='reg')

# Set up our figure by naming it returns_fig, call PairPLot on the DataFrame
return_fig = sns.PairGrid(stock_rets.dropna())

# Using map_upper we can specify what the upper triangle will look like.
return_fig.map_upper(plt.scatter, color='purple')

# We can also define the lower triangle in the figure, inclufing the plot type (kde) 
# or the color map (BluePurple)
return_fig.map_lower(sns.kdeplot, cmap='cool_d')

# Finally we'll define the diagonal as a series of histogram plots of the daily return
return_fig.map_diag(plt.hist, bins=30)

# Set up our figure by naming it returns_fig, call PairPLot on the DataFrame
returns_fig = sns.PairGrid(df_close)

# Using map_upper we can specify what the upper triangle will look like.
returns_fig.map_upper(plt.scatter,color='purple')

# We can also define the lower triangle in the figure, inclufing the plot type (kde) or the color map (BluePurple)
returns_fig.map_lower(sns.kdeplot,cmap='cool_d')

# Finally we'll define the diagonal as a series of histogram plots of the daily return
returns_fig.map_diag(plt.hist,bins=30)

"""Heatmap for corr()"""

sns.heatmap(stock_rets.corr(), annot=True)

sns.heatmap(df_close.corr(), annot=True)

"""#Berapa nilai yang kita gunakan dengan berinvestasi pada saham tertentu?"""

rets = stock_rets.dropna()

area = np.pi * 20

plt.figure(figsize=(10, 7))
plt.scatter(rets.mean(), rets.std(), s=area)
plt.xlabel('Expected return')
plt.ylabel('Risk')

for label, x, y in zip(rets.columns, rets.mean(), rets.std()):
    plt.annotate(label, xy=(x, y), xytext=(50, 50), textcoords='offset points', ha='right', va='bottom', 
                 arrowprops=dict(arrowstyle='-', color='blue', connectionstyle='arc3,rad=-0.3'))

"""So we have for the highest expected return is MSFT.

#Predict MSFT Price
"""

MSFT.head()

fig = go.Figure()
fig.add_trace(go.Scatter(x=MSFT.index, y=MSFT['Close'], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=MSFT.index, y=MSFT['MA-21'], mode='lines', name='MA-21'))
fig.add_trace(go.Scatter(x=MSFT.index, y=MSFT['MA-60'], mode='lines', name='MA-60'))
fig.add_trace(go.Scatter(x=MSFT.index, y=MSFT['MA-120'], mode='lines', name='MA-120'))
fig.update_layout(title='MSFT Price')
fig.show()

"""#Using Close data for prediction"""

data = MSFT.filter(['Close'])
dataset = data.values
dataset

"""Scaling data"""

from sklearn.preprocessing import MinMaxScaler
minmax = MinMaxScaler(feature_range=(0,1))
scaled_data = minmax.fit_transform(dataset)

# how many days do i want to base my predictions on ?
prediction_days = 60

x_train = []
y_train = []

for x in range(prediction_days, len(scaled_data)):
    x_train.append(scaled_data[x - prediction_days:x, 0])
    y_train.append(scaled_data[x, 0])
    
x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

from keras.models import Sequential
from keras import layers

# Build the LSTM model
model = Sequential([
                    layers.LSTM(128, return_sequences=True, input_shape= (x_train.shape[1], 1)),
                    layers.LSTM(64, return_sequences=False),
                    layers.Dense(25),
                    layers.Dense(1)
                    ])

model.summary()

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=10)

# test model accuracy on existing data
test_data = data['2021-01-01':]

actual_prices = test_data['Close'].values

total_dataset = pd.concat((data['Close'], test_data['Close']), axis=0)

model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:].values
model_inputs = model_inputs.reshape(-1,1)
model_inputs = minmax.transform(model_inputs)

x_test = []
for x in range(prediction_days, len(model_inputs)):
    x_test.append(model_inputs[x-prediction_days:x, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1] ,1))

predicted_prices = model.predict(x_test)
predicted_prices = minmax.inverse_transform(predicted_prices)

plt.figure(figsize=(15,5))
plt.plot(actual_prices, color='black', label="Actual price")
plt.plot(predicted_prices, color= 'green', label="Predicted price")
plt.title("MSFT Share price")
plt.xlabel("time")
plt.ylabel("MSFT Share price")
plt.legend()
plt.show()