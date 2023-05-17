import pandas as pd
import numpy as np
import os
from tkinter.filedialog import askdirectory , askopenfile

def ProcesarRetenciones():
    #Crear un DataFrame vacío
    Conslidado = pd.DataFrame()

    # cargar todos los XLS de la carpeta 'RET' en el DataFrame
    Retenciones = askdirectory(title="Selecionar Archivo de Retenciones")

    for file in os.listdir(Retenciones):
        if file.endswith('.xls'):
            df = pd.read_excel(f'{Retenciones}/{file}')
            # Crear columna 'CUIT contribuyente' con el cuarto elemento entre '-' del nombre del archivo y sacarle los espacios en blanco
            df['CUIT contribuyente'] = file.split('-')[3].strip()
            df['CUIT contribuyente'] = df['CUIT contribuyente'].astype('int64')
            #Crear columna de 'Cliente' con el quinto elemento entre '-' del nombre del archivo y sacarle los espacios en blanco y reemplazar los 'xls' por ''
            df['Cliente'] = file.split('-')[4].strip().replace('.xls', '')
            Conslidado = pd.concat([Conslidado, df], ignore_index=True)

    
    #del df, file

    # Crear una tabla dinámica con el CUIT y el 'Importe Ret./Perc.'
    Consolidado_TD = pd.pivot_table(Conslidado, values='Importe Ret./Perc.', index=['CUIT contribuyente' , 'Cliente'], aggfunc=np.sum)

    #reinicio el índice para que el 'CUIT' y 'Cliente' sea una columna
    Consolidado_TD = Consolidado_TD.reset_index()

    # Crear un archivo Excel con el resultado
    #Consolidado_TD.to_excel("Resultado.xlsx" , index=False)

    return Consolidado_TD

def SaldosIniciales():
    Saldos_iniciales = askopenfile(title="Selecionar Archivo de Saldos Iniciales")
    Saldos_iniciales = pd.read_excel(Saldos_iniciales.name)
    Saldos_iniciales = Saldos_iniciales.rename(columns={'Saldo Técnico':'ST Inicial' , 'SLD':'SLD Inicial'})
    Saldos_iniciales['CUIT contribuyente'] = Saldos_iniciales['CUIT contribuyente'].astype('int64')

    return Saldos_iniciales

def ProcesarTXT():
    #leer el archivo Formato.xlsx
    Alicuota_C = pd.read_excel('Formato.xlsx', sheet_name='Alicuota_C')
    Alicuota_V = pd.read_excel('Formato.xlsx', sheet_name='Alicuota_V')

    #leer todos lor achivos .txt no vacíos de la carpeta Consolidar
    path = askdirectory(title="Seleccionar Carpeta con TXT de LID")
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
        #Dividir la columna 'Archivo' con el separador '-' y crear columnas con los valores obtenidos como 'Fin Cuit', 'CUIT contribuyente', 'Periodo' y 'Cliente' y eliminar los espacios en blanco al inicio y al final de cada valor
        ALIC['Fin Cuit'] = ALIC['Archivo'].str.split('-').str[0].str.strip().astype(int)
        ALIC['CUIT contribuyente'] = ALIC['Archivo'].str.split('-').str[1].str.strip().astype('int64')
        ALIC['Periodo'] = ALIC['Archivo'].str.split('-').str[3].str.strip()
        ALIC['Cliente'] = ALIC['Archivo'].str.split('-').str[4].str.strip().str.replace(' Alicuota SOS.txt', '' , regex=False)
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
        #Dividir la columna 'Archivo' con el separador '-' y crear columnas con los valores obtenidos como 'Fin Cuit', 'CUIT contribuyente', 'Periodo' y 'Cliente' y eliminar los espacios en blanco al inicio y al final de cada valor
        ALIC['Fin Cuit'] = ALIC['Archivo'].str.split('-').str[0].str.strip().astype(int)
        ALIC['CUIT contribuyente'] = ALIC['Archivo'].str.split('-').str[1].str.strip().astype('int64')
        ALIC['Periodo'] = ALIC['Archivo'].str.split('-').str[3].str.strip()
        ALIC['Cliente'] = ALIC['Archivo'].str.split('-').str[4].str.strip().str.replace(' Alicuota SOS.txt', '' , regex=False)
        #Eliminar la columna 'Archivo'
        ALIC = ALIC.drop(['Archivo'], axis=1)
        Consolidado_ALIC_V = pd.concat([Consolidado_ALIC_V, ALIC], axis=0)
    del Alicuota_desc_V, Alicuota_V, ALIC , Alicuota_txt_V , i
    #Dividir las columnas 'Importe neto gravado' y 'Impuesto liquidado' por 100
    Consolidado_ALIC_V['Importe neto gravado'] = Consolidado_ALIC_V['Importe neto gravado']/100
    Consolidado_ALIC_V['Impuesto liquidado'] = Consolidado_ALIC_V['Impuesto liquidado']/100
    #Si el Tipo de comprobante es igual a (3 , 8 , 13 , 21 , 38 , 43 , 44 , 48 , 50 , 53 , 70 , 90 , 110 , 112 , 113 , 114 , 119 , 203 , 208 , 213) entonces multiplica el valor de las columnas 'Importe neto gravado' y 'Impuesto liquidado' por -1
    Consolidado_ALIC_V.loc[Consolidado_ALIC_V['Tipo de comprobante'].isin([3 , 8 , 13 , 21 , 38 , 43 , 44 , 48 , 50 , 53 , 70 , 90 , 110 , 112 , 113 , 114 , 119 , 203 , 208 , 213]) , ['Importe neto gravado' , 'Impuesto liquidado']] *= -1

    #crear Tablas dinamicas para todos los dataframe en base a la columnas 'Fin Cuit', 'CUIT contribuyente', 'Periodo' , 'Cliente' y eliminar las columnas que no se necesitan


    Consolidado_ALIC_CP = Consolidado_ALIC_C.pivot_table(index=['Fin Cuit', 'CUIT contribuyente', 'Periodo' , 'Cliente'], 
                                                        aggfunc='sum')

    #Eliminar columnas 'Código de documento del vendedor' , 'Número de comprobante' , 'Número de identificación del vendedor' , 'Punto de venta'
    Consolidado_ALIC_CP = Consolidado_ALIC_CP[['Impuesto liquidado']]
    del Consolidado_ALIC_C

    Consolidado_ALIC_VP = Consolidado_ALIC_V.pivot_table(index=['Fin Cuit', 'CUIT contribuyente', 'Periodo' , 'Cliente'], 
                                                        aggfunc='sum')

    #Eliminar columnas 'Número de comprobante' , 'Punto de venta'
    Consolidado_ALIC_VP = Consolidado_ALIC_VP[['Impuesto liquidado']]
    del Consolidado_ALIC_V

    # Renombrar las columnas de 'Impuesto liquidado' de Consolidado_ALIC_CP, Consolidado_ALIC_VP por 'Impuesto liquidado CF' y ' Impuesto liquidado DF'
    Consolidado_ALIC_CP = Consolidado_ALIC_CP.rename(columns={'Impuesto liquidado':'Impuesto liquidado CF'})
    Consolidado_ALIC_VP = Consolidado_ALIC_VP.rename(columns={'Impuesto liquidado':'Impuesto liquidado DF'})

    # Consolidar los dataframes Consolidado_CBTE_CP y Consolidado_ALIC_VP en base a la columna 'index' en un nuevo dataframe llamado 'Saldo'
    Saldo = pd.merge(Consolidado_ALIC_CP, 
                    Consolidado_ALIC_VP, 
                    on=['Fin Cuit', 'CUIT contribuyente', 'Periodo' , 'Cliente'], 
                    how='outer')

    # Reemplazar los valores nulos por 0
    Saldo = Saldo.fillna(0)

    #transformar los index en columnas
    Saldo.reset_index(inplace=True)

    return Saldo

def CalculaSaldos():

    Saldo = ProcesarTXT()
    Saldos_iniciales = SaldosIniciales() 
    Retenciones = ProcesarRetenciones()

    Saldo = pd.merge(left=Saldo,
                    right=Saldos_iniciales[['CUIT contribuyente' , 'Cliente' , 'ST Inicial' , 'SLD Inicial']],
                    how='outer',
                    on='CUIT contribuyente'
                    )

    # si existen las columnas clinete_x y cliente_y, combinarlas en una sola columna llamada 'Cliente'
    Saldo['Cliente'] = Saldo['Cliente_x'].fillna(Saldo['Cliente_y'])
    # Eliminar las columnas 'Cliente_x' y 'Cliente_y'
    Saldo = Saldo.drop(['Cliente_x', 'Cliente_y'], axis=1)

    Saldo = pd.merge(left=Saldo,
                    right=Retenciones[['CUIT contribuyente', 'Cliente' , 'Importe Ret./Perc.']],
                    on='CUIT contribuyente',
                    how='outer')
    
    # si existen las columnas clinete_x y cliente_y, combinarlas en una sola columna llamada 'Cliente'
    Saldo['Cliente'] = Saldo['Cliente_x'].fillna(Saldo['Cliente_y'])
    # Eliminar las columnas 'Cliente_x' y 'Cliente_y'
    Saldo = Saldo.drop(['Cliente_x', 'Cliente_y'], axis=1)

    Saldo = Saldo.fillna(0)

    #Calculo de Saldos

    #Crear la columna de 'Saldo Técnico' como la resta de las columnas 'Impuesto liquidado' y 'Crédito Fiscal Computable'
    Saldo['IVA a pagar'] = Saldo['Impuesto liquidado DF'] -  Saldo['Impuesto liquidado CF']

    # Calculos en Resultados

    # Sumar las columnas de 'SLD' y 'RET IVA' en la columan 'SLD'
    Saldo['SLD'] = Saldo['SLD Inicial'] + Saldo['Importe Ret./Perc.']
    Saldo['Saldo Técnico'] = Saldo['ST Inicial']

    ## Si el 'IVA a pagar' < 'Saldo Técnico', se paga la totalidad del 'IVA a pagar' con el 'Saldo Técnico'
    # Crear columna temporal 'Temp Pagar < 1P'
    Saldo['Temp Pagar < 1P'] = False

    # Si el 'IVA a pagar' < 'Saldo Técnico', 'Temp Pagar < 1P' es igual a Verdadero
    Saldo.loc[Saldo['IVA a pagar'] < Saldo['ST Inicial'], 'Temp Pagar < 1P'] = True

    # Si 'Temp Pagar < 1P' es Verdadero, el 'Saldo Técnico' = 'Saldo Técnico' - 'IVA a pagar'
    Saldo.loc[Saldo['Temp Pagar < 1P'] == True, 'Saldo Técnico'] = (Saldo.loc[Saldo['Temp Pagar < 1P'] == True, 'Saldo Técnico'] - 
                                                                    Saldo.loc[Saldo['Temp Pagar < 1P'] == True, 'IVA a pagar'])

    # Si 'Temp Pagar < 1P' es Verdadero, el 'IVA a pagar' = 0
    Saldo.loc[Saldo['Temp Pagar < 1P'] == True, 'IVA a pagar'] = 0

    # Si 'Temp Pagar < 1P' es Falso, el 'IVA a pagar' = 'IVA a pagar' - 'Saldo Técnico'
    Saldo.loc[Saldo['Temp Pagar < 1P'] == False, 'IVA a pagar'] = (Saldo.loc[Saldo['Temp Pagar < 1P'] == False, 'IVA a pagar'] -
                                                                Saldo.loc[Saldo['Temp Pagar < 1P'] == False, 'Saldo Técnico'])

    # Si 'Temp Pagar < 1P' es Falso, el 'Saldo Técnico' = 0
    Saldo.loc[Saldo['Temp Pagar < 1P'] == False, 'Saldo Técnico'] = 0

    # Eliminar columna temporal 'Temp Pagar < 1P'
    del Saldo['Temp Pagar < 1P']


    ## Si el 'IVA a pagar' < 'SLD', se paga la totalidad del 'IVA a pagar' con el 'SLD'
    # Crear columna 'Temp Pagar < 2P'
    Saldo['Temp Pagar < 2P'] = False

    #Si el 'IVA a apgar' < 'SLD', 'Temp Pagar < 2P' es Verdadero
    Saldo.loc[Saldo['IVA a pagar'] < Saldo['SLD'], 'Temp Pagar < 2P'] = True

    #si 'Temp Pagar < 2P' es Verdadero, el 'SLD' = 'SLD' - 'IVA a pagar'
    Saldo.loc[Saldo['Temp Pagar < 2P'] == True, 'SLD'] = (Saldo.loc[Saldo['Temp Pagar < 2P'] == True, 'SLD'] - 
                                                        Saldo.loc[Saldo['Temp Pagar < 2P'] == True, 'IVA a pagar'])

    #si 'Temp Pagar < 2P' es Verdadero, el 'IVA a pagar' = 0
    Saldo.loc[Saldo['Temp Pagar < 2P'] == True, 'IVA a pagar'] = 0

    #si 'Temp Pagar < 2P' es Falso, el 'IVA a pagar' = 'IVA a pagar' - 'SLD'
    Saldo.loc[Saldo['Temp Pagar < 2P'] == False, 'IVA a pagar'] = (Saldo.loc[Saldo['Temp Pagar < 2P'] == False, 'IVA a pagar'] -
                                                                Saldo.loc[Saldo['Temp Pagar < 2P'] == False, 'SLD'])

    #si 'Temp Pagar < 2P' es Falso, el 'SLD' = 0
    Saldo.loc[Saldo['Temp Pagar < 2P'] == False, 'SLD'] = 0

    # Eliminar columna temporal 'Temp Pagar < 2P'
    del Saldo['Temp Pagar < 2P']

    Saldo = Saldo[['Fin Cuit' , 'CUIT contribuyente' , 'Periodo' , 'Cliente' , 'ST Inicial' , 'SLD Inicial' , 'Impuesto liquidado DF' , 'Impuesto liquidado CF' , 'Importe Ret./Perc.' , 'IVA a pagar' , 'Saldo Técnico' , 'SLD']]

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

    return Saldo

SaldoIVA = CalculaSaldos()

#SaldoIVA = SaldoIVA.sort_values(by=["Fin Cuit" , "CUIT contribuyente"])
#SaldoIVA.to_excel("Resultados Calculadora de IVA.xlsx" , index=False)

SaldoIVA.to_excel('SaldoIVA.xlsx', index=False)