#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#import pyspark
import os
import requests
from selenium.webdriver.common.by import By
from PIL import Image
#import geopandas as gpd
import folium
import datetime
import warnings
from selenium.webdriver.chrome.options import Options

from bokeh.models import VBar #, cat #bokeh.charts
from bokeh.io import output_file, show, reset_output, output_notebook, export_png
from bokeh.models import Range1d, FactorRange, ColumnDataSource, LabelSet, HoverTool, LinearAxis, CDSView, GroupFilter, Select
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Tabs, Panel, IntEditor, SelectEditor, StringEditor, TextInput
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.transform import factor_cmap
from bokeh.models.annotations import Label
from bokeh.plotting import save, figure
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.models import TMSTileSource, WheelZoomTool, PanTool, NumeralTickFormatter, CategoricalColorMapper, Div, Slider, Button, Select, CheckboxButtonGroup, TapTool, Dot, CustomJS
from bokeh.palettes import brewer
from bokeh.io import curdoc
#from bokeh.server.server import Server
from tornado.ioloop import IOLoop
#from bokeh.application.handlers import FunctionHandler, Application
from bokeh.client import push_session
from bokeh.models.ranges import FactorRange
from bokeh.core.properties import value
from bokeh.models import Div, DatetimeTickFormatter, CategoricalColorMapper
from bokeh.embed import components, file_html
from bokeh.palettes import Spectral6, RdBu3
from bokeh.transform import factor_cmap

import plotly.graph_objects as go
import holoviews as hv
import holoviews.plotting.bokeh
import seaborn as sns
import matplotlib.pyplot as plt
from holoviews import opts


# In[2]:


# otwarcie strony who z danymi dotyczącymi pandemi
#options = webdriver.ChromeOptions()
#options.add_argument("--headless")
#driver = webdriver.Chrome()
#driver.get("https://covid19.who.int/table");
#time.sleep(2)
#driver.maximize_window()

#link =  driver.current_url
    
#r=requests.get(link)
#c=r.content
#soup=BeautifulSoup(c,"html.parser")

# znalezienie przycisku do aktualizacji danych
#dataset = driver.find_element_by_xpath('//*[@id="gatsby-focus-wrapper"]/div/div[4]/div/div[1]/a')
#dataset.click()
#time.sleep(3)
#driver.close()


# In[3]:


# open file from path
path= "/Users/alubis/Downloads/"
data=pd.read_csv("" + path + "WHO-COVID-19-global-data.csv", sep=",")
data["Date_reported"]=pd.to_datetime(data["Date_reported"], format='%Y/%m/%d')
data["share_of_all"]= data[' Cumulative_cases']/sum(data[' Cumulative_cases'])
pop= pd.read_csv('population.csv', sep=";")
data= pd.merge(data, pop, left_on=' Country', right_on='name', how="left")
data.drop(['Unnamed: 0'], axis='columns', inplace=True)
data['share_of_all']= data['share_of_all'].round(decimals=3)
data['udzial_w_populacji'] = data[' Cumulative_cases']/data['pop']
data['udzial_w_populacji']=data['udzial_w_populacji'].round(decimals=3)


# In[4]:


result = data.loc[data["Date_reported"]==(data["Date_reported"].max()-datetime.timedelta(days=1)).strftime('%Y/%m/%d')]
result = result.sort_values(" Cumulative_cases", ascending=False)
yesterday = data.loc[data["Date_reported"]==(result['Date_reported'].max()-datetime.timedelta(days=1))]
yesterday =yesterday[[" Cumulative_cases", " Country"]]
yesterday = yesterday.rename(columns = {' Cumulative_cases': 'yesterday_cases'}, inplace = False)
result= pd.merge(result, yesterday, left_on=' Country', right_on=' Country', how="left")
result['dzienny_przyrost']= (result[' Cumulative_cases']-result['yesterday_cases'])/result[' Cumulative_cases']
result['dzienny_przyrost']= result['dzienny_przyrost'].round(decimals=3)


# In[5]:


# WYKRES 1
# wykres + tabela z danymi
# źródło danych
source = ColumnDataSource(data={
    'kraj': list(result[' Country'][0:20]),
    'kod': list(result[' Country_code'][0:20]),
    'cases': list(result[' Cumulative_cases'][0:20]),
    'new': list(result[' New_cases'][0:20]),
    'share': list(result['share_of_all'][0:20]),
    'deaths': list(result[' New_deaths'][0:20]),
    'increment': list(result['dzienny_przyrost'][0:20]),
    'in_pop': list(result['udzial_w_populacji'][0:20])
})

europa =['Portugal', 'Spain', 'France', 'Italy', 'Switzerland', 'Belgium', 'Netherlands', 'The United Kingdom', 'Ireland', 'Germany', 'Denmark', 'Austria', "Slovenia", 'Czechia', 'Poland', 'Sweden', 'Norway', 'Lithuania', 'Latvia', 'Estonia', 'Finland', 'Belarus', 'Ukraine', 'Republic od Moldavia', 'Slovakia', 'Hungary', 'Croatia', 'Romiania', 'Serbia', 'Bosnia and Herzegowina', 'Russian Federation', 'Kazakhstan', 'Kosovo[1]', 'Greece', 'Albania', 'Montenegro', 'North Macedonia', 'Bulgaria', 'Turkey']
reszta= list(set(list(result[' Country']))-set(europa)) 

TOOLS='pan, yzoom_in, yzoom_out, box_select, tap, reset, save'
plt= figure(plot_height=800,
            plot_width=1300,
            title='Covid incidence in individual countries',
            x_range = list(result[' Country_code'][0:20]),
            tools=TOOLS,
            x_axis_label='Country',
            y_axis_label='Cumulative cases'
            )

# wyświetlanie wartości - dynamicznie
tooltips = [
            ('Country', '@kraj'),
            ('Cumulative cases', '@cases'),
            ('New cases', '@new'),
            ('New deaths', '@deaths'),
            ('Share in population', '@in_pop{00.0%}')
            ]
plt.add_tools(HoverTool(tooltips=tooltips))

# dodatkowa oś y i jej format
plt.extra_y_ranges = {"procenty": Range1d(start=0.0, end=0.08 )}
plt.add_layout(LinearAxis(y_range_name="procenty", axis_label = '(%)'), 'right')
plt.yaxis[1].formatter = NumeralTickFormatter(format='00.0%')
plt.yaxis[0].formatter = NumeralTickFormatter(format='0')

# pochylenie nazw na osi x
plt.xaxis.major_label_orientation = np.pi/4
plt.xaxis.major_label_text_font_size = '18px'

# labels
labels = LabelSet(x='kod', y='cases', text='cases', level='glyph',
                 x_offset=-17.5, y_offset = 0, source=source,
                 text_font_size = '14pt', render_mode='canvas')
plt.add_layout(labels)

# plot
a=plt.vbar(x='kod', top='cases', width=0.8, source=source)
a.glyph.fill_color= '#084594'

r={}
r['in_pop']= plt.line(x='kod', y='in_pop', color='red', source=source, y_range_name='procenty', legend_label='share in the population')
r['increment']= plt.circle(x='kod', y='increment', size =20, color='green', source=source, y_range_name='procenty', legend_label='daily increment ')

# legenda 
plt.legend.location= 'top_right'
plt.legend.click_policy= 'hide'

# tabela do layout'u
table = result.copy()
table["Date_reported"]= table["Date_reported"].dt.strftime('%d/%m/%Y')
table = table[['Date_reported', ' Country', ' Country_code',' New_cases', ' Cumulative_cases', ' New_deaths', ' Cumulative_deaths', ' WHO_region', 'udzial_w_populacji']]
Columns = [TableColumn(field=Ci, title=Ci) for Ci in table.columns]
data_table_source=ColumnDataSource(table)
data_table = DataTable(columns=Columns, source=data_table_source, width=1250, height=800)

# działania dynamiczne
def update_x(attrname, old, new):
    list_of_active = [checkbox_button_group.labels[i] for i in checkbox_button_group.active]
    
    if select.value == 'latest':
        result = data.loc[data["Date_reported"]==(data["Date_reported"].max()-datetime.timedelta(days=1)).strftime('%Y/%m/%d')]
    else:
        result = data.loc[data["Date_reported"]== select.value]
    result = result.sort_values(" Cumulative_cases", ascending=False)
    yesterday = data.loc[data["Date_reported"]==(result['Date_reported'].max()-datetime.timedelta(days=1))]
    yesterday =yesterday[[" Cumulative_cases", " Country"]]
    yesterday = yesterday.rename(columns = {' Cumulative_cases': 'yesterday_cases'}, inplace = False)
    result= pd.merge(result, yesterday, left_on=' Country', right_on=' Country', how="left")
    result['dzienny_przyrost']= (result[' Cumulative_cases']-result['yesterday_cases'])/result[' Cumulative_cases']
    result['dzienny_przyrost']= result['dzienny_przyrost'].round(decimals=3)
    table = result.copy()
    table["Date_reported"]= table["Date_reported"].dt.strftime('%d/%m/%Y')
    table = table[['Date_reported', ' Country', ' Country_code',' New_cases', ' Cumulative_cases', ' New_deaths', ' Cumulative_deaths', ' WHO_region', 'udzial_w_populacji']]
    Columns = [TableColumn(field=Ci, title=Ci) for Ci in table.columns]
    data_table_source2=ColumnDataSource(table)
    data_table_source.data=dict(data_table_source2.data)
    plt.x_range.factors=[]
    
    if len(list_of_active)==len(opcje) or len(list_of_active)==0:
        result2=result.copy()
    if len(list_of_active)==1 and list_of_active[0]== opcje[0]:
        result2=result.loc[result[' Country'].isin(europa)]
    if len(list_of_active)==1 and list_of_active[0]== opcje[1]:
        result2=result.loc[result[' Country'].isin(reszta)]
        
    plt.x_range.factors= list(result2[' Country_code'][0:20])
    source2 = ColumnDataSource(data={
                'kraj': list(result2[' Country'][0:20]),
                'kod': list(result2[' Country_code'][0:20]),
                'cases': list(result2[' Cumulative_cases'][0:20]),
                'new': list(result2[' New_cases'][0:20]),
                'share': list(result2['share_of_all'][0:20]),
                'deaths': list(result2[' New_deaths'][0:20]),
                'increment': list(result2['dzienny_przyrost'][0:20]),
                'in_pop': list(result2['udzial_w_populacji'][0:20])
            })
    source.data=dict(source2.data)

def x_range(attrname, old, new):
    n= slider.value
    if select.value == 'latest':
        result4 = data.loc[data["Date_reported"]==(data["Date_reported"].max()-datetime.timedelta(days=1)).strftime('%Y/%m/%d')]
    else:
        result4 = data.loc[data["Date_reported"]== select.value]
    result4 = result4.sort_values(" Cumulative_cases", ascending=False)
    yesterday = data.loc[data["Date_reported"]==(result4['Date_reported'].max()-datetime.timedelta(days=1))]
    yesterday =yesterday[[" Cumulative_cases", " Country"]]
    yesterday = yesterday.rename(columns = {' Cumulative_cases': 'yesterday_cases'}, inplace = False)
    result4= pd.merge(result4, yesterday, left_on=' Country', right_on=' Country', how="left")
    result4['dzienny_przyrost']= (result4[' Cumulative_cases']-result4['yesterday_cases'])/result4[' Cumulative_cases']
    result4['dzienny_przyrost']= result4['dzienny_przyrost'].round(decimals=3)
    plt.x_range.factors=[]
    plt.x_range.factors= list(result4[' Country_code'][0:8+n])
    source2 = ColumnDataSource(data={
                    'kraj': list(result4[' Country'][0:8+n]),
                    'kod': list(result4[' Country_code'][0:8+n]),
                    'cases': list(result4[' Cumulative_cases'][0:8+n]),
                    'new': list(result4[' New_cases'][0:8+n]),
                    'share': list(result4['share_of_all'][0:8+n]),
                    'deaths': list(result4[' New_deaths'][0:8+n]),
                    'increment': list(result4['dzienny_przyrost'][0:8+n]),
                    'in_pop': list(result4['udzial_w_populacji'][0:8+n])
                })
    source.data=dict(source2.data)
    table = result4.copy()
    table["Date_reported"]= table["Date_reported"].dt.strftime('%d/%m/%Y')
    table = table[['Date_reported', ' Country', ' Country_code',' New_cases', ' Cumulative_cases', ' New_deaths', ' Cumulative_deaths', ' WHO_region', 'udzial_w_populacji']]
    Columns = [TableColumn(field=Ci, title=Ci) for Ci in table.columns]
    data_table_source2=ColumnDataSource(table)
    data_table_source.data=dict(data_table_source2.data)    

def deaths():
    if select.value == 'latest':
        result4 = data.loc[data["Date_reported"]==(data["Date_reported"].max()-datetime.timedelta(days=1)).strftime('%Y/%m/%d')]
    else:
        result4 = data.loc[data["Date_reported"]== select.value]
    result4 = data.loc[data["Date_reported"]== select.value]
    result4 = result4.sort_values(" Cumulative_cases", ascending=False)
    yesterday = data.loc[data["Date_reported"]==(result4['Date_reported'].max()-datetime.timedelta(days=1))]
    yesterday =yesterday[[" Cumulative_cases", " Country"]]
    yesterday = yesterday.rename(columns = {' Cumulative_cases': 'yesterday_cases'}, inplace = False)
    result4= pd.merge(result4, yesterday, left_on=' Country', right_on=' Country', how="left")
    result4['dzienny_przyrost']= (result4[' Cumulative_cases']-result4['yesterday_cases'])/result4[' Cumulative_cases']
    result4['dzienny_przyrost']= result4['dzienny_przyrost'].round(decimals=3)
    plt.x_range.factors=[]
    plt.x_range.factors= list(result4[' Country_code'][0:20])
    source2 = ColumnDataSource(data={
                    'kraj': list(result4[' Country'][0:20]),
                    'kod': list(result4[' Country_code'][0:20]),
                    'cases': list(result4[' Cumulative_cases'][0:20]),
                    'new': list(result4[' New_cases'][0:20]),
                    'share': list(result4['share_of_all'][0:20]),
                    'deaths': list(result4[' New_deaths'][0:20]),
                    'increment': list(result4['dzienny_przyrost'][0:20]),
                    'in_pop': list(result4['udzial_w_populacji'][0:20])
                })
    source.data=dict(source2.data)
    table = result4.copy()
    table["Date_reported"]= table["Date_reported"].dt.strftime('%d/%m/%Y')
    table = table[['Date_reported', ' Country', ' Country_code',' New_cases', ' Cumulative_cases', ' New_deaths', ' Cumulative_deaths', ' WHO_region', 'udzial_w_populacji']]
    Columns = [TableColumn(field=Ci, title=Ci) for Ci in table.columns]
    data_table_source2=ColumnDataSource(table)
    data_table_source.data=dict(data_table_source2.data)
    b = result4.sort_values(" New_deaths", ascending=False)[0:20]
    b = b[0:3]
    lista = list(b[' Country_code'])
    mapper = CategoricalColorMapper(palette= ['red', 'red', 'red'], factors= list(result4.loc[result4[' Country_code'].isin(lista)][' Country'][0:3]))
    a.glyph.fill_color= dict(field='kraj', transform=mapper)
    
def period(attrname, old, new):
    a.glyph.fill_color= '#084594'
    if select.value == 'latest':
        result4 = data.loc[data["Date_reported"]==(data["Date_reported"].max()-datetime.timedelta(days=1)).strftime('%Y/%m/%d')]
    else:
        result4 = data.loc[data["Date_reported"]== select.value]
    result4 = result4.sort_values(" Cumulative_cases", ascending=False)
    yesterday = data.loc[data["Date_reported"]==(result4['Date_reported'].max()-datetime.timedelta(days=1))]
    yesterday =yesterday[[" Cumulative_cases", " Country"]]
    yesterday = yesterday.rename(columns = {' Cumulative_cases': 'yesterday_cases'}, inplace = False)
    result4= pd.merge(result4, yesterday, left_on=' Country', right_on=' Country', how="left")
    result4['dzienny_przyrost']= (result4[' Cumulative_cases']-result4['yesterday_cases'])/result4[' Cumulative_cases']
    result4['dzienny_przyrost']= result4['dzienny_przyrost'].round(decimals=3)
    plt.x_range.factors=[]
    plt.x_range.factors= list(result4[' Country_code'][0:20])
    source2 = ColumnDataSource(data={
                    'kraj': list(result4[' Country'][0:20]),
                    'kod': list(result4[' Country_code'][0:20]),
                    'cases': list(result4[' Cumulative_cases'][0:20]),
                    'new': list(result4[' New_cases'][0:20]),
                    'share': list(result4['share_of_all'][0:20]),
                    'deaths': list(result4[' New_deaths'][0:20]),
                    'increment': list(result4['dzienny_przyrost'][0:20]),
                    'in_pop': list(result4['udzial_w_populacji'][0:20])
                })
    source.data=dict(source2.data)
    table = result4.copy()
    table["Date_reported"]= table["Date_reported"].dt.strftime('%d/%m/%Y')
    table = table[['Date_reported', ' Country', ' Country_code',' New_cases', ' Cumulative_cases', ' New_deaths', ' Cumulative_deaths', ' WHO_region', 'udzial_w_populacji']]
    Columns = [TableColumn(field=Ci, title=Ci) for Ci in table.columns]
    data_table_source2=ColumnDataSource(table)
    data_table_source.data=dict(data_table_source2.data)

    
# 1. europa / świat
opcje=["Europa", "poza Europa"]
checkbox_button_group = CheckboxButtonGroup(labels=opcje, active=[])
checkbox_button_group.on_change('active', update_x)

# 2. button - najwięcej zgonów
button = Button(label='The highest number of deaths')
button.on_click(deaths)

# 3. slider po liczebności
slider = Slider(start=0, end=10, step=1, value=0, title= 'Change the range of the x axis')
slider.on_change('value', x_range)

# 4.select okres
select = Select(title='Choose a period:', value='latest', options=['latest', '2020-10-01', '2020-09-01', '2020-08-01', '2020-07-01', '2020-06-01', '2020-05-01', '2020-04-01', '2020-03-01', '2020-02-01'])
select.on_change('value', period)

html_1 = """ <h3> Covid incidence in individual countries </h><b><i></>"""
sup_title_1 = Div(text=html_1, width=800)

layout_1 = gridplot([ [select],[slider],[plt], [checkbox_button_group],[button], [data_table]])
raport_1=column(sup_title_1, layout_1)


# In[6]:


# WYKRES 2
# zmiana w czasie

czas= data[data[" Country"]=='Canada']
czas = czas.sort_values("Date_reported", ascending=False)

# źródło danych
source2 = ColumnDataSource(data={
    'time': list(czas['Date_reported'][0:20]),
    'kraj': list(czas[' Country'][0:20]),
    'kod': list(czas[' Country_code'][0:20]),
    'cases': list(czas[' Cumulative_cases'][0:20]),
    'deaths_c': list(czas[' Cumulative_deaths'][0:20]),
    'new': list(czas[' New_cases'][0:20]),
    'deaths': list(czas[' New_deaths'][0:20])
})

TOOLS2='pan, yzoom_in, yzoom_out, box_select, tap, reset, save'
plt2= figure(plot_height=800,
            plot_width=1250,
            title='Changes of cumulative cases in individual countries',
            x_axis_type='datetime',
            tools=TOOLS2,
            x_axis_label='Time',
            y_axis_label='Cumulative cases'
            )
plt2.y_range.start= min(list(czas[' Cumulative_cases'][1:19]))- 0.05*(min(list(czas[' Cumulative_cases'][1:19])))
plt2.y_range.end= max(list(czas[" Cumulative_cases"][1:19])) + 0.05*(max(list(czas[" Cumulative_cases"][1:19])))

# wyświetlanie wartości - dynamicznie
hover = HoverTool(
    tooltips = [
            ('Country', '@kraj'),
            ('Cumulative cases', '@cases'),
            ('New cases', '@new'),
            ('New deaths', '@deaths') ],
    #formatters={ 'time': 'datetime'},
                )
plt2.add_tools(hover)

# pochylenie nazw na osi x
plt2.xaxis.major_label_orientation = np.pi/4
plt2.xaxis.major_label_text_font_size = '18px'

# format osi x
plt2.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],)
plt2.yaxis.formatter = NumeralTickFormatter(format='0')

# dodatkowa oś y i jej format
plt2.extra_y_ranges = {"second": Range1d(start=min(list(czas[' New_cases'][1:20])), end=max(list(czas[" New_cases"][1:19])))}
plt2.add_layout(LinearAxis(y_range_name="second", axis_label = ''), 'right')

# labels
labels2 = LabelSet(x='time', y='cases', text='cases', level='glyph',
                 x_offset=-17.5, y_offset = 0, source=source2,
                 text_font_size = '14pt', render_mode='canvas')
plt2.add_layout(labels2)

# plot

g={}
g['country_cases']= plt2.line(x='time', y='cases', color='blue', source=source2, legend_label='cumulative cases')
#g['country_cases']= plt2.line(x='time', y='deaths_c', color='red', source=source2, y_range_name='second', legend_label='cumulative cases of deaths')
g['new_cases']= plt2.line(x='time', y='new', color='orange', source=source2, y_range_name='second', legend_label='new cases')


# legenda 
plt2.legend.location= 'top_right'
plt2.legend.click_policy= 'hide'

# działania dynamiczne

def country(attrname, old, new):
    selected= new
    szukaj_wartosci= list(filter(lambda k: selected in k, list(data[' Country'])))
    czas_n= data.loc[data[' Country'].isin(szukaj_wartosci)]
    czas_n = czas_n.sort_values("Date_reported", ascending=False)
    source3 = ColumnDataSource(data={
            'time': list(czas_n['Date_reported'][0:20]),
            'kraj': list(czas_n[' Country'][0:20]),
            'kod': list(czas_n[' Country_code'][0:20]),
            'cases': list(czas_n[' Cumulative_cases'][0:20]),
            'deaths_c': list(czas[' Cumulative_deaths'][0:20]),
            'new': list(czas_n[' New_cases'][0:20]),
            'deaths': list(czas_n[' New_deaths'][0:20])
        })
    source2.data=dict(source3.data)
    plt2.extra_y_ranges['second'].start = min(list(czas_n[' New_cases'][1:19])) - 0.05*(min(list(czas_n[' New_cases'][1:19])) )
    plt2.extra_y_ranges['second'].end = max(list(czas_n[" New_cases"][1:19])) + 0.05*(max(list(czas_n[" New_cases"][1:19])))
    plt2.y_range.start= min(list(czas_n[' Cumulative_cases'][1:19]))- 0.05*(min(list(czas_n[' Cumulative_cases'][1:19])))
    plt2.y_range.end= max(list(czas_n[" Cumulative_cases"][1:19])) + 0.05*(max(list(czas_n[" Cumulative_cases"][1:19])))
    table_3 = czas_n[['Date_reported',' New_cases', ' Cumulative_cases', ' New_deaths', ' Cumulative_deaths', ' WHO_region']][0:20]
    table_3["Date_reported"]= table_3["Date_reported"].dt.strftime('%d/%m/%Y')
    source_table2=ColumnDataSource(table_3)
    source_table.data=dict(source_table2.data)
    
# 1.select kraj
select2 = Select(title='Choose a country:', value='Canada', options= list(data[' Country'].unique()))
select2.on_change('value', country)

# tabela do layout'u
table_2 = czas[['Date_reported',' New_cases', ' Cumulative_cases', ' New_deaths', ' Cumulative_deaths', ' WHO_region']][0:20]
table_2["Date_reported"]= table_2["Date_reported"].dt.strftime('%d/%m/%Y')
Columns_2 = [TableColumn(field="Date_reported", title="Date_reported"),
           TableColumn(field=" New_cases", title="New_cases"),
           TableColumn(field=" Cumulative_cases", title="Cumulative_cases"),
           TableColumn(field=" New_deaths", title="New_deaths"),
           TableColumn(field=" Cumulative_deaths", title="Cumulative_deaths"),
           TableColumn(field=" WHO_region", title="WHO_region")]
source_table=ColumnDataSource(table_2)
data_table_2 = DataTable(columns=Columns_2, source=source_table, width=1250, height=800, editable=True)

html_2 = """ <h3> Covid incidence in individual countries </h><b><i></>"""
sup_title_2 = Div(text=html_2, width=800)

layout_2 = gridplot([[select2],[plt2], [data_table_2]])
raport_2=column(sup_title_2, layout_2)


# In[7]:


# WYKRES 3
# mapa świata z zakażeniami

def run():
    country_geo = 'world-countries.json'

    mapa = folium.Figure(width=1000, height=500)
    mapp = folium.Map(location=[20, 0], zoom_start=1.5).add_to(mapa)

    result['name']=result[' Country']
    data_to_plot = result[['name',' Cumulative_cases']]

    choropleth = (folium.Choropleth(geo_data=country_geo, data=data_to_plot,
                 columns=['name',' Cumulative_cases'],
                 key_on='properties.name',
                 fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2,
                 legend_name="Covid incidence in individual countries",
                 highlight = True )).add_to(mapp)

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['name'],labels=False)
    )
    
    
    WIDTH = 700
    HEIGHT = 700

    div = Div(
        text=mapa._repr_html_(),
        width= WIDTH,
        height=HEIGHT
    )

    return row(div)

bokeh_layout = run()

#mapa.save('' + path + 'map.html')
#mapa_2 = Div(text="<iframe src="r'/Users/alubis/Downloads/map.html'" style='min-width:calc(80vw - 20px); height: 500px'><iframe>")

html_3 = """ <h3> World map - number of infections </h><b><i></>"""
sup_title_3 = Div(text=html_3, width=300)

raport_3=column(sup_title_3, bokeh_layout, sizing_mode='scale_both')


# In[243]:


# Wykres 4
# Symptomy

path= "/Users/alubis/Downloads/"
sym=pd.read_csv("" + path + "COVID_symptoms.csv", sep=",")
sym= sym.sample(n=10000, random_state=1)
#sym['Dry.Cough'] = sym['Dry.Cough'].astype(int)

sym_grouped = sym.groupby(by=["Age", "Gender"]).sum()[["Dry.Cough",'Difficulty.in.Breathing', 'Fever', 'None_Sympton']]
sym_grouped = sym_grouped.reset_index()
var = ["female", "male"]
sym_fin = sym_grouped[sym_grouped.Gender.isin(var)]

hv.extension('bokeh')
sankey=hv.Sankey(data=sym_fin, kdims=["Age", "Gender"], vdims=['Dry.Cough'])
sankey.opts(cmap='Colorblind',label_position='left',
                                 edge_color='Gender', edge_line_width=0,
                                 node_alpha=1.0, node_width=40, node_sort=True,
                                 width=1000, height=800, bgcolor="snow",
                                 title="Distribution of the population of people with a dry cough")
#show(hv.render(sankey))
heatmap = hv.HeatMap(sym_fin, vdims=['Dry.Cough']).sort().aggregate(function=np.sum)
heatmap.opts(opts.HeatMap(tools=['hover'], colorbar=True, width=400, height=500, toolbar='above'))

#hv_ds = hv.Dataset(data=sym_fin, kdims=["Age", "Gender"], vdims=['Difficulty.in.Breathing'])
#sankey.data=hv_ds.data
#hv_ds.to(hv.Sankey)

hv_ds = hv.Dataset(data=sym_fin, kdims=["Age", "Gender"], vdims=['Difficulty.in.Breathing'])
sankey2=hv_ds.to(hv.Sankey)
sankey2.opts(cmap='Colorblind',label_position='left',
                                 edge_color='Gender', edge_line_width=0,
                                 node_alpha=1.0, node_width=40, node_sort=True,
                                 width=1000, height=800, bgcolor="snow", title="Distribution of the population of people with difficulty in breathing")
heatmap2 = hv.HeatMap(sym_fin, vdims=['Difficulty.in.Breathing']).sort().aggregate(function=np.sum)
heatmap2.opts(opts.HeatMap(tools=['hover'], colorbar=True, width=400, height=500, toolbar='above'))

hv_ds2 = hv.Dataset(data=sym_fin, kdims=["Age", "Gender"], vdims=['Fever'])
sankey3=hv_ds2.to(hv.Sankey)
sankey3.opts(cmap='Colorblind',label_position='left',
                                 edge_color='Gender', edge_line_width=0,
                                 node_alpha=1.0, node_width=40, node_sort=True,
                                 width=1000, height=800, bgcolor="snow",
                                 title="Distribution of the population of people with fever")
#table = sym_fin.pivot("Age", "Gender", 'Fever')
# Draw a heatmap with the numeric values in each cell
#f, ax = plt.subplots(figsize=(9, 6))
#a=sns.heatmap(table, annot=True, fmt="d", linewidths=.5, ax=ax)
#fig = a.get_figure()
heatmap3 = hv.HeatMap(sym_fin, vdims=['Fever']).sort().aggregate(function=np.sum)
heatmap3.opts(opts.HeatMap(tools=['hover'], colorbar=True, width=400, height=500, toolbar='above'))

hv_ds3 = hv.Dataset(data=sym_fin, kdims=["Age", "Gender"], vdims=['None_Sympton'])
sankey4=hv_ds3.to(hv.Sankey)
sankey4.opts(cmap='Colorblind',label_position='left',
                                 edge_color='Gender', edge_line_width=0,
                                 node_alpha=1.0, node_width=40, node_sort=True,
                                 width=1000, height=800, bgcolor="snow",
                                 title="Distribution of the population of people with none sympton")
heatmap4 = hv.HeatMap(sym_fin, vdims=['None_Sympton']).sort().aggregate(function=np.sum)
heatmap4.opts(opts.HeatMap(tools=['hover'], colorbar=True, width=400, height=500, toolbar='above'))

raport_11=column(row(hv.render(sankey), hv.render(heatmap)))
raport_22=column(row(hv.render(sankey2), hv.render(heatmap2)))
raport_33=column(row(hv.render(sankey3), hv.render(heatmap3)))
raport_44=column(row(hv.render(sankey4), hv.render(heatmap4)))


panel_11 = Panel(child=raport_11, title = 'Dry Cough')
panel_22 = Panel(child=raport_22, title = 'Difficulty in Breathing')
panel_33 = Panel(child=raport_33, title = 'Fever')
panel_44 = Panel(child=raport_44, title = 'None_Sympton')

tabb= Tabs(tabs=[panel_11, panel_22, panel_33, panel_44], width=400)

raport_4=tabb


# In[244]:


# wyświetlenie trzech paneli 
panel_1 = Panel(child=raport_1, title = 'Countries')
panel_2 = Panel(child=raport_2, title = 'Variation in time')
panel_3 = Panel(child=raport_3, title = 'Map')
panel_4 = Panel(child=raport_4, title = 'Symptoms')

#panel_3 = Panel(child=bokeh_layout, title = 'Map')

tabs= Tabs(tabs=[panel_1, panel_2, panel_3, panel_4])
#show(tabs)
curdoc().add_root(tabs)


# In[246]:


#show(tabs)


# In[ ]:




