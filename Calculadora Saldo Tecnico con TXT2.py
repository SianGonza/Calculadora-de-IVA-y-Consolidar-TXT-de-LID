import pandas as pd
import numpy as np
import os
from tkinter.filedialog import askdirectory

#leer el archivo Formato.xlsx
Alicuota_C = pd.read_excel('Formato.xlsx', sheet_name='Alicuota_C')
Alicuota_V = pd.read_excel('Formato.xlsx', sheet_name='Alicuota_V')

#leer todos lor achivos .txt no vacíos de la carpeta Consolidar
path = askdirectory()
Archivos = os.listdir(path)
Archivos_txt = [f for f in Archivos if (os.stat(path + "/" + f).st_size != 0 and f.endswith(".txt"))]
del Archivos


#crear una nueva variable con los Archivos_txt que contengan la palabra 'Alicuota'
Alicuota_txt = [i for i in Archivos_txt if 'Alicuota' in i]
Alicuota_txt_C = [i for i in Alicuota_txt if '- LIC -' in i]
Alicuota_txt_V = [i for i in Alicuota_txt if '- LIV -' in i]


#Eliminar Variables no usadas
del Archivos_txt

#convertir las Columna 'Descripcion' de los dataframes Comprobante y Alicuota en listas
Alicuota_desc_C = Alicuota_C['Descripcion'].tolist()
Alicuota_desc_V = Alicuota_V['Descripcion'].tolist()

#convertir las Columna 'Ancho' de los dataframes Comprobante y Alicuota en listas
Alicuota_C = Alicuota_C['Ancho'].tolist()
Alicuota_V = Alicuota_V['Ancho'].tolist()


#crear un dataframe vacio para conslidar
Consolidado_ALIC_C = pd.DataFrame()

#crear un loop para leer y consolidar todos los archivos de la variable Alicuota_txt_C de tipo FWF en base a la variable Alicuota
for i in Alicuota_txt_C:
    ALIC = pd.read_fwf(path + '/' + i, widths=Alicuota_C, header=None , encoding=("latin1") , names = Alicuota_desc_C)
    ALIC['Archivo'] = i
    #Dividir la columna 'Archivo' con el separador '-' y crear columnas con los valores obtenidos como 'Fin Cuit', 'CUIT contribuyente', 'Periodo' y 'Nombre del contribuyente' y eliminar los espacios en blanco al inicio y al final de cada valor
    ALIC['Fin Cuit'] = ALIC['Archivo'].str.split('-').str[0].str.strip()
    ALIC['CUIT contribuyente'] = ALIC['Archivo'].str.split('-').str[1].str.strip()
    ALIC['Periodo'] = ALIC['Archivo'].str.split('-').str[3].str.strip()
    ALIC['Nombre del contribuyente'] = ALIC['Archivo'].str.split('-').str[4].str.strip().str.replace(' SOS.txt', '' , regex=False)
    #Eliminar la columna 'Archivo'
    ALIC = ALIC.drop(['Archivo'], axis=1)
    Consolidado_ALIC_C = pd.concat([Consolidado_ALIC_C, ALIC], axis=0)
del Alicuota_desc_C, Alicuota_C, ALIC , Alicuota_txt_C
#Dividir las columnas 'Importe neto gravado' y 'Impuesto liquidado' por 100
Consolidado_ALIC_C['Importe neto gravado'] = Consolidado_ALIC_C['Importe neto gravado']/100
Consolidado_ALIC_C['Impuesto liquidado'] = Consolidado_ALIC_C['Impuesto liquidado']/100
#Si el Tipo de comprobante es igual a (3 , 8 , 13 , 21 , 38 , 43 , 44 , 48 , 50 , 53 , 70 , 90 , 110 , 112 , 113 , 114 , 119 , 203 , 208 , 213) entonces multiplica el valor de las columnas 'Importe neto gravado' y 'Impuesto liquidado'
Consolidado_ALIC_C.loc[Consolidado_ALIC_C['Tipo de comprobante'].isin([3 , 8 , 13 , 21 , 38 , 43 , 44 , 48 , 50 , 53 , 70 , 90 , 110 , 112 , 113 , 114 , 119 , 203 , 208 , 213]) , ['Importe neto gravado' , 'Impuesto liquidado']] *= -1


#crear un dataframe vacio para conslidar
Consolidado_ALIC_V = pd.DataFrame()

#crear un loop para leer y consolidar todos los archivos de la variable Alicuota_txt_V de tipo FWF en base a la variable Alicuota
for i in Alicuota_txt_V:
    ALIC = pd.read_fwf(path + '/' + i, widths=Alicuota_V, header=None , encoding=("latin1") , names = Alicuota_desc_V)
    ALIC['Archivo'] = i
    #Dividir la columna 'Archivo' con el separador '-' y crear columnas con los valores obtenidos como 'Fin Cuit', 'CUIT contribuyente', 'Periodo' y 'Nombre del contribuyente' y eliminar los espacios en blanco al inicio y al final de cada valor
    ALIC['Fin Cuit'] = ALIC['Archivo'].str.split('-').str[0].str.strip()
    ALIC['CUIT contribuyente'] = ALIC['Archivo'].str.split('-').str[1].str.strip()
    ALIC['Periodo'] = ALIC['Archivo'].str.split('-').str[3].str.strip()
    ALIC['Nombre del contribuyente'] = ALIC['Archivo'].str.split('-').str[4].str.strip().str.replace(' SOS.txt', '' , regex=False)
    #Eliminar la columna 'Archivo'
    ALIC = ALIC.drop(['Archivo'], axis=1)
    Consolidado_ALIC_V = pd.concat([Consolidado_ALIC_V, ALIC], axis=0)
del Alicuota_desc_V, Alicuota_V, ALIC , Alicuota_txt_V , i
#Dividir las columnas 'Importe neto gravado' y 'Impuesto liquidado' por 100
Consolidado_ALIC_V['Importe neto gravado'] = Consolidado_ALIC_V['Importe neto gravado']/100
Consolidado_ALIC_V['Impuesto liquidado'] = Consolidado_ALIC_V['Impuesto liquidado']/100
#Si el Tipo de comprobante es igual a (3 , 8 , 13 , 21 , 38 , 43 , 44 , 48 , 50 , 53 , 70 , 90 , 110 , 112 , 113 , 114 , 119 , 203 , 208 , 213) entonces multiplica el valor de las columnas 'Importe neto gravado' y 'Impuesto liquidado' por -1
Consolidado_ALIC_V.loc[Consolidado_ALIC_V['Tipo de comprobante'].isin([3 , 8 , 13 , 21 , 38 , 43 , 44 , 48 , 50 , 53 , 70 , 90 , 110 , 112 , 113 , 114 , 119 , 203 , 208 , 213]) , ['Importe neto gravado' , 'Impuesto liquidado']] *= -1

#crear Tablas dinamicas para todos los dataframe en base a la columnas 'Fin Cuit', 'CUIT contribuyente', 'Periodo' , 'Nombre del contribuyente' y eliminar las columnas que no se necesitan


Consolidado_ALIC_CP = Consolidado_ALIC_C.pivot_table(index=['Fin Cuit', 'CUIT contribuyente', 'Periodo' , 'Nombre del contribuyente'], aggfunc='sum')
#Eliminar columnas 'Código de documento del vendedor' , 'Número de comprobante' , 'Número de identificación del vendedor' , 'Punto de venta'
Consolidado_ALIC_CP = Consolidado_ALIC_CP[['Impuesto liquidado']]
del Consolidado_ALIC_C

Consolidado_ALIC_VP = Consolidado_ALIC_V.pivot_table(index=['Fin Cuit', 'CUIT contribuyente', 'Periodo' , 'Nombre del contribuyente'], aggfunc='sum')
#Eliminar columnas 'Número de comprobante' , 'Punto de venta'
Consolidado_ALIC_VP = Consolidado_ALIC_VP[['Impuesto liquidado']]
del Consolidado_ALIC_V

# Renombrar las columnas de 'Impuesto liquidado' de Consolidado_ALIC_CP, Consolidado_ALIC_VP por 'Impuesto liquidado CF' y ' Impuesto liquidado DF'
Consolidado_ALIC_CP = Consolidado_ALIC_CP.rename(columns={'Impuesto liquidado':'Impuesto liquidado CF'})
Consolidado_ALIC_VP = Consolidado_ALIC_VP.rename(columns={'Impuesto liquidado':'Impuesto liquidado DF'})

# Consolidar los dataframes Consolidado_CBTE_CP y Consolidado_ALIC_VP en base a la columna 'index' en un nuevo dataframe llamado 'Saldo'
Saldo = pd.merge(Consolidado_ALIC_CP, Consolidado_ALIC_VP, on=['Fin Cuit', 'CUIT contribuyente', 'Periodo' , 'Nombre del contribuyente'], how='outer')
# Reemplazar los valores nulos por 0
Saldo = Saldo.fillna(0)
#Crear la columna de 'Saldo Técnico' como la resta de las columnas 'Impuesto liquidado' y 'Crédito Fiscal Computable'
Saldo['Saldo Técnico'] = Saldo['Impuesto liquidado CF'] - Saldo['Impuesto liquidado DF']

#transformar los index en columnas
Saldo.reset_index(inplace=True)

#Exportar los dataframes consolidados a un archivo excel
# Archivo_final = pd.ExcelWriter('Consolidado.xlsx', engine='openpyxl')
# Consolidado_CBTE_C.to_excel(Archivo_final, sheet_name='CBTE_C' , index=False)
# Consolidado_CBTE_CP.to_excel(Archivo_final, sheet_name='CBTE_C TD')
# Consolidado_ALIC_C.to_excel(Archivo_final, sheet_name='ALIC_C' , index=False)
# Consolidado_ALIC_CP.to_excel(Archivo_final, sheet_name='ALIC_C TD')
# Consolidado_CBTE_V.to_excel(Archivo_final, sheet_name='CBTE_V' , index=False)
# Consolidado_CBTE_VP.to_excel(Archivo_final, sheet_name='CBTE_V TD')
# Consolidado_ALIC_V.to_excel(Archivo_final, sheet_name='ALIC_V' , index=False)
# Consolidado_ALIC_VP.to_excel(Archivo_final, sheet_name='ALIC_V TD')
# Archivo_final.save()
