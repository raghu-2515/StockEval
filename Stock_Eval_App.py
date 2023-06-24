import streamlit as st
from datetime import date
from datetime import timedelta
import pandas as pd
import plotly.express as px

import yfinance as yf
from plotly import graph_objs as go

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

TODAY=date.today().strftime("%Y-%m-%d")

st.title("Stock Evaulation App")


selected_stock=st.sidebar.text_input("Enter Ticker Symbol","SPY")
selected_etf=st.sidebar.text_input("Enter ETF/Index/Ticker Symbol to Compare",'NONE')
Time_Period=("1wk","1mo","3mo","1y","3y","5y")
Time_Frame=st.sidebar.selectbox("**Select Timeframe**",Time_Period,index=1)
Time_Interval="1d"
if Time_Frame== "1wk" or Time_Frame=="1mo" or Time_Frame == "3mo":
    Time_Interval="1d"
else:
    Time_Interval="1wk"

if selected_stock:
    
    #@st.cache
    def load_data(ticker):
        data=yf.download(ticker,period=Time_Frame,interval=Time_Interval)
        data.reset_index(inplace=True)
        return data

    data_load_state=st.text("Load data...")
    data=load_data(selected_stock)
    data = data.rename(columns = {'index':'Date'})
    data['Date'] = pd.to_datetime(data['Date'])
    data['Year']=data['Date'].dt.year
    data['Qtr']=data['Date'].dt.quarter
    data['YQ']="Q"+data['Qtr'].astype(str)+"/"+data['Year'].astype(str)
    data1=load_data(selected_etf)
    data_load_state.text("Loading data...done!")

    st.subheader('Raw Data')
    st.write(data.head())

    def plot_raw_data():
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'],y=data['Adj Close'],name=selected_stock))
        if selected_etf:
            fig.add_trace(go.Scatter(x=data1['Date'],y=data1['Adj Close'],name=selected_etf))
        fig.layout.update(title_text="Time Series Data",xaxis_rangeslider_visible=False)
        st.plotly_chart(fig)

    def plot_box_plot():
        fig = px.box(data_frame=data, x='YQ', y='Adj Close', title=selected_stock +'- Adj Close')
        st.plotly_chart(fig)

    col1,col2=st.columns(2)
    with col1:
        plot_raw_data()
    
    with col2:
        plot_box_plot()