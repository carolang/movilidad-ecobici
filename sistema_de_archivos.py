class SistemaDeArchivos:
  carpeta_recorridos = 'RECORRIDOS'
  carpeta_recorridos_estandarizados = 'RECORRIDOS ESTANDARIZADOS'

  def __init__(self, path_to_folder):
    self._path_to_folder = path_to_folder

  def archivos_recorridos(self):
    return os.listdir(self.path_global(self.carpeta_recorridos))

  def path_a_diccionario_de_columnas(self):
    return self.path_global('diccionario_nombres_columnas_recorridos.csv')

  def path_global(self, path_local):
    return self._path_to_folder + '/' + path_local

  def path_a_archivo_crudo(self, anio):
    return self.path_global(self.carpeta_recorridos + '/' + self.nombre_archivo_crudo(anio))

  def path_a_archivo_estandarizado(self, anio):
    return self.path_global(self.carpeta_recorridos_estandarizados + '/' + self.nombre_archivo_estandarizado(anio))

  def nombre_archivo_crudo(self, anio):
    if 2010 <= int(anio) <= 2018:
      return 'recorridos-realizados-' + str(anio) + '.csv'
    elif 2019 <= int(anio) <= 2023:
      return 'trips_' + str(anio) + '.csv'
    elif int(anio) == 2024:
      return 'badata_ecobici_recorridos_realizados_2024.csv'
    elif 2025 <= int(anio) <= 2026:
      return 'Trips.csv'
    else:
      raise Exception('El año proporcionado (' + str(anio) + ') es inválido')

  def nombre_archivo_estandarizado(self, anio):
    return 'recorridos-' + str(anio) + '.csv'

  def guardar_tabla_estandar_de_recorridos_para_anio(self, tabla, anio):
    path = self.path_a_archivo_estandarizado(anio)
    print('Guardando la tabla correspondiente al año', anio, 'en', path, "...")
    tabla.to_csv(path, index=False)
