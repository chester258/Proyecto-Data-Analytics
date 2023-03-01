import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import datetime 
import numpy as np
import plotly.graph_objs as go
import plotly.express  as  px
import yfinance as yf
import seaborn as sns


#SIDEBAR
#Ponemos en ina lista los indices del sp500 y de los sectores que lo conforman
tikers = ['^GSPC','XLE','XLB','XLI','XLY','XLP','XLV','XLF','XLK','XLC','XLU']
#Creamos un sidebar en Streamlit los diferentes tikers 
sectores = st.sidebar.multiselect('tikers',tikers)
#Creamos un sidebar en Streamlit con un rango de fechas
fecha_inicio = st.sidebar.date_input('Fecha inicio',datetime.date(2000, 1, 1)) 
fecha_fin = st.sidebar.date_input('Fecha fin',datetime.date(2022, 1, 1))
#Creamos un sidebar en Streamlit con una variable numerica con la que
#calcularemos cuanto hubiera generado una inversion en un lapso de tiempo determinado
dolares_inv = st.sidebar.number_input('Dolares inv',100)

#---------------------------------------------------------------------------------------

#Descargamos todos los datos de cada sector, para hacer 
#futuras comparaciones

todo = yf.download(tikers, start="2000-01-01",end='2022-01-01')
todo.reset_index(inplace=True)
#Trasformamos la columna 'Date'    
todo['Date'] = pd.to_datetime(todo['Date']).dt.date
    

#Procedemos obtener los datos de la rentabilidad de cada sector
#el ultimo año para compararlas
fecha_ren_i = datetime.date(2021, 1, 1)
fecha_ren_f = datetime.date(2022, 1, 1)
data_ult = todo[(todo['Date']>= fecha_ren_i) & (todo['Date'] <= fecha_ren_f)]  
lista_r = []
lista_s = []   
for i in todo['Close']:
    precio_fin = data_ult['Close'][i].values[-1]
    precio_in = data_ult['Close'][i].values[0]
        
    rentabilidad = (precio_fin - precio_in) / precio_in
    rentabilidad = (np.round(rentabilidad,2))

    lista_r.append(rentabilidad)
    lista_s.append(i)
    
lista_r =np.array(lista_r)*100   
bar = pd.DataFrame({
    'Sector': lista_s,
    'Cantidad': lista_r})




#---------------------------------------------------------------------------------------
#EXTRACCION DE DATOS Y CALCULOS DE INDICADORES POR EMPRESA

if len(sectores)==1:
    #Descargamos los datos en fechas predeterminadas
    data = yf.download(sectores,fecha_inicio,fecha_fin)
    #hacemos que el indice de fechas se vuelva una columna
    data.reset_index(inplace=True)
    #Pasamos los datos de fechas strings a datetime
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    #Calculamos el retorno diaria
    data['Daily Return'] = data['Close'].pct_change()
    # Calcular la media móvil de 100 y 300 dias
    data['SMA_100'] = data['Close'].rolling(window=100).mean()
    data['SMA_300'] = data['Close'].rolling(window=300).mean()

    # Calcular el drawdown desde el último máximo
    data["cummax"] = data["Close"].cummax()
    data["drawdown"] = ((data["cummax"] - data["Close"]) / data["cummax"])*100

    
    #calculamos los distintos indicadores que nos van a 
    #dar informacio acerca del indice y si es viable una inversion

    
    #definimos la funcion para calcular la tasa de retorno anual
    def tasa_retorno_anual(df):
        star_date = data.loc[data.index[0], "Date"]
        end_date = data.loc[data.index[-1], "Date"]
        start_price = data.loc[data.index[0], "Adj Close"]
        end_price = data.loc[data.index[-1], "Adj Close"]
        years_10y = (end_date - star_date).days / 365
        cagr_10y = (end_price / start_price) ** (1 / years_10y) - 1
        porcentaje = cagr_10y*100
        return round(porcentaje,2)
    
   
    #Calculamos la rentabilidad el ultimo año
    fecha_ren_i = datetime.date(2021, 1, 1)
    fecha_ren_f = datetime.date(2022, 1, 1)
    data_ult = data[(data['Date']>= fecha_ren_i) & (data['Date'] <= fecha_ren_f)]
    precio_fin = data_ult['Close'].values[-1]
    precio_in = data_ult['Close'].values[0]
    rentabilidad = (precio_fin - precio_in) / precio_in
    

    #Calculamos la tasa de retorno anual, la volatilidad anual,el drawdown máximo, 
    #el retorno acumulado, el valor final de la inversión, la rentabilidad y a 
    #cuanto cotiza hoy en dia el indice.  
    tra = tasa_retorno_anual(data)
    volatildiad_anual =round((data['Daily Return'].std() * (252**0.5))*100,2)
    cotizacion = round(data['Close'][data['Date'].index[-1]],2)
    max_drawdown = data["drawdown"].max()
    retorno_acum = (data['Daily Return'] + 1).cumprod()
    valor_fin = retorno_acum.values[-1] * dolares_inv
    rentabilidad = round(rentabilidad*100,2)


    #Dibujamos en stremlit las distintas variables que calculamos 
    left_column1, rigth_column1 = st.columns(2)

    with left_column1:
            st.subheader('Cotizacion:')
            st.subheader(str(cotizacion)+' USD')
            st.subheader('Tasa de Retorno Anual:')
            st.subheader(str(tra)+'%')
            st.subheader("Valor final de la inversión:")
            st.subheader(str(np.round(valor_fin, 2)) + ' USD')
    with rigth_column1:
        st.subheader('Volatilidad Anualizada')
        st.subheader(str(volatildiad_anual)+'%')
        st.subheader('Maximo drawdown:')
        st.subheader(str(round(max_drawdown,2))+'%')
        st.subheader('rentabilidad:')
        st.subheader(str(rentabilidad) + '%')
    

    
    st.subheader('##')
    st.subheader('##')
    #Graficamos los precios de cierre respecto al tiempo
    st.subheader('Grafico de Cierre')
    fig1 = px.line(data,x='Date',y =["Close","SMA_100","SMA_300"])
    st.write(fig1)

    
    #Graficamos el retorno diario respecto al tiempo
    st.subheader('Grafico de Retorno Diario')
    fig2 =  px.bar(data,x='Date',y='Daily Return')
    st.write(fig2)

    #Graficamos la rentabilida de cada sector el ultimo año
    st.subheader('Rentabilida de cada sector el ultimo año')
    st.bar_chart(bar.set_index('Sector'))


    st.dataframe(data)

    
#En caso de analizar mas de un sector a la ves podremos compara sus distintos
#graficos del precio de cierre
elif len(sectores)>1:
    data = yf.download(sectores,fecha_inicio,fecha_fin)['Close']
    
    st.subheader('Comparativa de Cierres de Multiples Empresas')
    st.line_chart(data)



    st.subheader('Rentabilida de cada sector el ultimo año')
    st.bar_chart(bar.set_index('Sector'))
         
    


