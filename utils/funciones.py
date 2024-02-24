# Librerías para manipulación de datos
import pandas as pd
import numpy as np

# Librerías para visualización
import plotly.express as px
import plotly.graph_objects as go

# Librerías para machine learning
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

#Librerías para la coneción con bigquery
from google.cloud import bigquery
from google.oauth2 import service_account

#Diccionario de datos con nombre y descripción de variables
DATA_DICT = {
    'Age': 'Edad del empleado',
    'Attrition': 'Si el empleado se abandono su empleo o no el año anterior',
    'BusinessTravel': 'Frecuencia con la que los empleados viajaron por motivos de trabajo en el último año',
    'Department': 'Departamento en la empresa',
    'DistanceFromHome': 'Distancia del domicilio en kms',
    'Education': 'Nivel de estudios',
    'EducationField': 'Ámbito de formación',
    'EmployeeCount': 'Número de empleados',
    'EmployeeID': 'Id de empleado',
    'Gender': 'Sexo del empleado',
    'JobLevel': 'Nivel del puesto en la empresa en una escala de 1 a 5',
    'JobRole': 'Nombre del puesto de trabajo en la empresa',
    'MaritalStatus': 'Estado civil del empleado',
    'MonthlyIncome': 'Ingresos mensuales en dólares al mes',
    'NumCompaniesWorked': 'Número total de empresas en las que ha trabajado el empleado',
    'Over18': 'Si el empleado es mayor de 18 años o no',
    'PercentSalaryHike': 'Porcentaje de aumento salarial en el último año',
    'StandardHours': 'Horas estándar de trabajo del empleado',
    'StockOptionLevel': 'Nivel de opciones sobre acciones del empleado',
    'TotalWorkingYears': 'Número total de años que el empleado ha trabajado hasta ahora',
    'TrainingTimesLastYear': 'Número de veces que se impartió formación a este empleado el año pasado',
    'YearsAtCompany': 'Número total de años que el empleado lleva en la empresa',
    'YearsSinceLastPromotion': 'Número de años desde el último ascenso',
    'YearsWithCurrManager': 'Número de años bajo el mando del jefe actual',
    'EnvironmentSatisfaction': 'Nivel de satisfacción del entorno de trabajo',
    'JobSatisfaction': 'Nivel de satisfacción laboral',
    'WorkLifeBalance': 'Nivel de conciliación de la vida laboral y familiar',
    'JobInvolvement': 'Nivel de implicación en el trabajo',
    'PerformanceRating': 'Valoración del rendimiento en el último año',
    'MeanTime': 'Tiempo promedio de trabajo al día del empleado en el último año',
    'retirementType': 'Tipo de retiro',
    'resignationReason': 'Razón de la renuncia',
    'retirementDate': 'Fecha de retiro'
}

# Se conecta a bigquery y trae la tabla que se le pase
def get_data(tabla):
    
    credentials_path = 'utils/clave_db.json' #Ruta del archivo json con credenciales de bigquery
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    project_id = 'aplicaciones-analitica' #Nombre del proyecto en bigquery
    client = bigquery.Client(credentials= credentials, project=project_id) # creacion del client para trabajar en python

    query = f'SELECT * FROM recursos_humanos.{tabla}' #Consultar para obtener los datos
    data = client.query(query).to_dataframe() #Obtener tabla completa y convertir en un dataframe
    
    return data

# Genera tabla de frecuencias para una variable
def tabla_frecuencias(df, col):
    
    n = df.shape[0]
    tabla = df.groupby([col])[['EmployeeID']].count().rename(columns={'EmployeeID':'Frecuencia Absoluta'}).reset_index()
    tabla['Frecuencia Relativa'] = tabla['Frecuencia Absoluta'].apply(lambda x: str(round(100*x/n, 3))+' %')
    
    return tabla.sort_values(by='Frecuencia Absoluta', ascending=False)

# Genera tabla de frecuencias y gráfico de barras para una variable
def univariado_barras(df, col, orientation='v'):
    
    if orientation=='v':
        x = col
        y = ['Frecuencia Absoluta']
    else:
        x = ['Frecuencia Absoluta']
        y = col
    
    tabla = tabla_frecuencias(df, col)
    
    fig = px.bar(tabla,
             x = x,
             y = y,
             text_auto = True,
             title = DATA_DICT[col],
             height = 400,
             labels = {'value': 'Total', col:col},
             text = 'Frecuencia Relativa', orientation=orientation)
    fig.layout.update(showlegend=False)
    fig.show()
    
    return tabla

# Genera tabla de frecuencias y gráfico de torta para una variable
def univariado_torta(df, col, hole=0):
    
    tabla = tabla_frecuencias(df, col)
    labels = tabla[col]
    values = tabla['Frecuencia Absoluta']

    fig = go.Figure(data=[go.Pie(labels=labels,
                                values=values,
                                textinfo = 'value+percent',
                                hole = hole
                                )])
    fig.update_layout(
        title_text = DATA_DICT[col],
        height = 400 )
    fig.show()
    
    return tabla

# Genera gráfico de barras vibariado
def analisisBivariado(df, variables, orient, mode, color=px.colors.qualitative.Plotly):
    
    contingency_table=pd.crosstab(df[variables[0]], df[variables[1]])
    contingency_table = contingency_table.div(contingency_table.sum(axis=1), axis=0)
    
    fig=px.bar(contingency_table,
               orientation = orient,
               barmode = mode,
               color_discrete_sequence = color)
    
    fig.update_layout(width = 800,
                      title = dict(text = DATA_DICT[variables[1]], x=0.5))
    fig.update_traces(texttemplate = '%{value:.2%}', textposition = 'outside')
    
    fig.show()
    print("Tabla de contingencia:")
    
    return contingency_table