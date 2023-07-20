import streamlit as st
from datetime import date
from datetime import timedelta
import pandas as pd
import plotly.express as px
import numpy as np

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
        #data_growth=(data.pct_change().fillna(0)+1).cumprod()
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

    stock_growth=(data["Adj Close"].pct_change().fillna(0)+1).cumprod()
    index_growth=(data1["Adj Close"].pct_change().fillna(0)+1).cumprod()

    #st.subheader('Raw Data')
    #st.write(data)

    def plot_raw_data():
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'],y=data['Adj Close'],name=selected_stock))
        if selected_etf:
            fig.add_trace(go.Scatter(x=data1['Date'],y=data1['Adj Close'],name=selected_etf,yaxis='y2'))
        fig.layout.update(title_text="Time Series Data",xaxis_rangeslider_visible=False)
        fig.update_layout(yaxis2=dict(overlaying='y',side='right'))
        st.plotly_chart(fig,use_container_width=True)

    def plot_growth_data():
        fig=go.Figure()
        fig.add_trace(go.Line(x=data.index,y=stock_growth,name=selected_stock))
        fig.add_trace(go.Line(x=data1.index,y=index_growth,name=selected_etf))
        fig.layout.update(title_text="Growth Comparison",xaxis_rangeslider_visible=False)
        st.plotly_chart(fig,use_container_width=True)

    def plot_box_plot():
        fig = px.box(data_frame=data, x='YQ', y='Adj Close', title=selected_stock +'- Adj Close')
        st.plotly_chart(fig,use_container_width=True)
    
    if Time_Frame== "1wk" or Time_Frame=="1mo" or Time_Frame == "3mo":
        trading_days=252
    else:
        trading_days=52
    
    
    def CAGR(data):
        df = data.copy()
        df['daily_returns'] = df['Adj Close'].pct_change()
        df['cumulative_returns'] = (1 + df['daily_returns']).cumprod()
        #trading_days = 252
        n = len(df)/ trading_days
        cagr = (df['cumulative_returns'].iloc[-1])**(1/n) - 1
        return cagr

    def volatility(data):
        df = data.copy()
        df['daily_returns'] = df['Adj Close'].pct_change()
        #trading_days = 252
        vol = df['daily_returns'].std() * np.sqrt(trading_days)
        return vol

    def sharpe_ratio(data, rf):
        df = data.copy()
        sharpe = (CAGR(df) - rf)/ volatility(df)
        return sharpe 

    col1,col2,col3,col4=st.columns([6.25,1.25,1.25,1.25])
    with col1:
        plot_growth_data()

    with col2:
        stock_name=f"**{selected_stock}** **_CAGR**"
        st.markdown(stock_name)
        st.subheader(f'{round(CAGR(data)*100,1)}%')
        st.markdown("------")
        comp_name=f"**{selected_etf}** **_CAGR**"
        st.markdown(comp_name)
        st.subheader(f'{round(CAGR(data1)*100,1)}%')
        
    with col3:
        stock_name=f"**{selected_stock}** **_VOL**"
        st.markdown(stock_name)
        st.subheader(f'{round(volatility(data) * 100,1)}%')
        st.markdown("------")
        comp_name=f"**{selected_etf}** **_VOL**"
        st.markdown(comp_name)
        st.subheader(f'{round(volatility(data1) * 100,1)}%')
              
    with col4:
        stock_name=f"**{selected_stock}** **_SHRP**"
        st.markdown(stock_name)
        st.subheader(round(sharpe_ratio(data,0.06) * 100,1))
        st.markdown("------")
        comp_name=f"**{selected_etf}** **_SHRP**"
        st.markdown(comp_name)
        st.subheader(round(sharpe_ratio(data1,0.06) * 100,1))
        
        #metric("**:red[Correlation Coefficient]**",round(corr_coeff,2))

    st.markdown("------")
    
    col1,col2=st.columns(2)
    with col1:
        plot_raw_data()

    corr_coeff=data["Adj Close"].corr(data1["Adj Close"])
    
    with col2:
        plot_box_plot()
