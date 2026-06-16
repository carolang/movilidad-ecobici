import pandas as pd

class FormatoTablas:
  def __init__(self, sistema_de_archivos):
    self._sistema_de_archivos = sistema_de_archivos
    self._dataframe_de_columnas = self._inicializar_dataframe_de_columnas()

  def _inicializar_dataframe_de_columnas(self):
    path_a_archivo_columnas = self._sistema_de_archivos.path_a_diccionario_de_columnas()
    return pd.read_csv(path_a_archivo_columnas)

  def campo_genero_estandar(self, campo_genero_original):
    if pd.isna(campo_genero_original):
        return 'unknown'
    campo_genero_mayuscula = str(campo_genero_original).upper().strip()
    if campo_genero_mayuscula in ['F', 'FEMALE']:
        return 'female'
    elif campo_genero_mayuscula in ['M', 'MALE']:
        return 'male'
    elif campo_genero_mayuscula in ['O', 'OTHER']:
        return 'other'
    elif campo_genero_mayuscula in ['N', 'UNKNOWN', 'NÃO IDENTIFICADO']:
        return 'unknown'
    else:
        print("Género no reconocido:", campo_genero_original)
        return 'unknown'

  # Esto es para 2021 que tiene dos fuentes para el campo 'genero'
  def combinar_dos_fuentes_para_genero(self, valor1, valor2):
    valor_estandar1 = self.campo_genero_estandar(valor1)
    valor_estandar2 = self.campo_genero_estandar(valor2)

    if valor_estandar1 == 'unknown':
      return valor_estandar2
    else:
      return valor_estandar1

  def is_float_nan(e):
    return not isinstance(e, str) and math.isnan(e)

  def nombre_columna_estandar(self, nombre_columna):
    nombre_columna_en_minuscula = nombre_columna.lower()

    if nombre_columna_en_minuscula in self.columnas_originales():
      condicion = self._dataframe_de_columnas['nombre_original_lowcase'] == nombre_columna_en_minuscula
      return self._dataframe_de_columnas.loc[condicion]['nombre_nuevo'].item()
    else:
      # Si no aparece en el diccionario es que no hay transformación
      # Quizás habría que levantar un error
      return nombre_columna

  def columnas_estandar(self):
    return self._dataframe_de_columnas['nombre_nuevo'].unique().tolist()

  def columnas_originales(self):
    return self._dataframe_de_columnas['nombre_original_lowcase'].tolist()

  def tabla_original(self, anio):
    return pd.read_csv(self._sistema_de_archivos.path_a_archivo_crudo(anio))

  def nueva_tabla_con_los_nombres_traducidos(self, df_original):
    columnas_df_original = df_original.columns

    columnas_df_nuevo = self.columnas_estandar()
    df_nuevo = pd.DataFrame(columns=columnas_df_nuevo)

    for nombre_columna_original in columnas_df_original:
      nombre_columna_nueva = self.nombre_columna_estandar(nombre_columna_original)
      df_nuevo[nombre_columna_nueva] = df_original[nombre_columna_original]

    # Si el año es 2021 hay que unir las columnas 'Género' y 'género'.
    if anio == 2021:
      df_nuevo['genero'] = [
        self.combinar_dos_fuentes_para_genero(
            fila['Género'], fila['género']
        )
        for _, fila in df_original.iterrows()
      ]

    return df_nuevo

  def nueva_tabla_sin_columnas_espurias(self, df_original):
    posibles_columnas_espurias = ['x', 'X', 'Unnamed: 0']
    columnas_espurias = [nombre
                         for nombre in posibles_columnas_espurias
                         if (nombre in df_original.columns)]
    return df_original.drop(columns=columnas_espurias)

  def agregar_columna_con_anio(self, df_original, anio):
    df_original['anio_estandar'] = int(anio)
    return df_original

  def estandarizar_genero(self, df_original):
    df_original['genero_estandar'] = df_original['genero'].apply(self.campo_genero_estandar)
    return df_original

  def convertir_fechas_a_datetime_para_columna(self, df_original, nombre_columna):
    df_original[nombre_columna] = pd.to_datetime(
      df_original[nombre_columna],
      format='mixed',
      dayfirst=True,
      errors='coerce'
    )

  def convertir_fechas_a_timedelta_para_columna(self, df_original, nombre_columna):
    df_original[nombre_columna] = pd.to_timedelta(
      df_original[nombre_columna],
      errors='coerce'
    )

    return df_original

  def inferir_fecha_de_fin_desde_inicio_y_duracion_si_falta(self, df_original):
    nombre_columna_duracion = 'duracion_recorrido'
    nombre_columna_fecha_destino = 'fecha_destino'
    self.convertir_fechas_a_timedelta_para_columna(
      df_original,
      nombre_columna_duracion
    )
    df_original[nombre_columna_fecha_destino] = df_original[nombre_columna_fecha_destino].fillna(
      df_original['fecha_origen'] + df_original[nombre_columna_duracion]
    )

  def convertir_fechas_a_datetime(self, df_original, anio):
    nombres_columnas_a_convertir = ['fecha_origen', 'fecha_destino']
    for nombre_columna in nombres_columnas_a_convertir:
      self.convertir_fechas_a_datetime_para_columna(
        df_original,
        nombre_columna
      )

    # Si el año es 2016 o 2017 hay que inferir la fecha de fin en algunos casos
    #  a partir de la fecha de inicio del recorrido y su duración.
    if anio == 2016 or anio == 2017:
      self.inferir_fecha_de_fin_desde_inicio_y_duracion_si_falta(
        df_original
      )

    return df_original

  def tabla_estandar(self, anio):
    print("Generando tabla para el año", anio, "...")

    df = self.tabla_original(anio)
    df = self.nueva_tabla_sin_columnas_espurias(df)
    df = self.nueva_tabla_con_los_nombres_traducidos(df)
    df = self.agregar_columna_con_anio(df, anio)
    df = self.convertir_fechas_a_datetime(df, anio)
    df = self.estandarizar_genero(df)

    return df
