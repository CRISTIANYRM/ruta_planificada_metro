import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import streamlit as st
from statsmodels.tsa.statespace.sarimax import SARIMAX
import networkx as nx
import os # Para verificar si el archivo existe
import tkinter as tk
from tkinter import ttk, messagebox
# ==============================================================================
# MÓDULO 1: ANÁLISIS DE RED DEL METRO (TEORÍA DE GRAFOS Y MOVILIDAD)
# ==============================================================================

# Lista completa de estaciones sin acentos y con nombres consistentes
# Asegúrate de que esta lista sea EXACTAMENTE igual a los nombres en tu Excel
# si no, el sistema de adyacencia podría fallar.
estaciones = [
    'Acatitla', 'Agricola Oriental', 'Allende', 'Apatlaco', 'Aragon', 'Aculco','Aquiles Serdan','Atlalilco',
    'Auditorio', 'Autobuses del Norte', 'Azcapotzalco', 'Balbuena', 'Balderas', 'Barranca del Muerto',
    'Bellas Artes', 'Bondojito', 'Bosques de Aragon', 'Boulevard Puerto Aereo',
    'Buenavista', 'Calle 11', 'Camarones', 'Canal de San Juan', 'Canal del Norte',
    'Candelaria', 'Centro Medico', 'Cerro de la Estrella', 'Chabacano','Chapultepec',
    'Chilpancingo', 'Ciudad Deportiva', 'Ciudad Azteca', 'Colegio Militar',
    'Consulado', 'Constitucion de 1917', 'Constituyentes', 'Copilco',
    'Coyoacan', 'Coyuya', 'Cuatro Caminos', 'Cuauhtemoc', 'Culhuacan','Cuitlahuac',
    'Deportivo 18 de Marzo', 'Deportivo Oceanía', 'Division del Norte',
    'Doctores', 'Ecatepec', 'Eduardo Molina', 'Eje Central', 'Ermita',
    'Escuadron 201', 'Etiopia/Plaza de la Transparencia', 'Eugenia',
    'Ferreria', 'Fray Servando', 'Garibaldi', 'General Anaya', 'Gomez Farias',
    'Guelatao', 'Guerrero', 'Hangares', 'Hidalgo', 'Hospital 20 de Noviembre',
    'Hospital General', 'Impulsora', 'Indios Verdes', 'Insurgentes',
    'Insurgentes Sur', 'Instituto del Petroleo', 'Isabel la Catolica',
    'Iztacalco', 'Iztapalapa', 'Jamaica', 'Juanacatlan', 'Juarez', 'La Paz',
    'La Raza', 'La Viga', 'La Villa - Basilica', 'Lagunilla', 'Lazaro Cardenas',
    'Lindavista', 'Lomas Estrella', 'Los Reyes', 'Martin Carrera', 'Merced',
    'Mexicaltzingo', 'Miguel Angel de Quevedo','Misterios', 'Mixcoac', 'Mixiuhca',
    'Moctezuma', 'Morelos', 'Muzquiz', 'Nativitas', 'Nezahualcoyotl',
    'Niños Heroes', 'Nopalera', 'Norte 45', 'Normal', 'Observatorio',
    'Oceanía', 'Obrera', 'Olimpica', 'Olivos', 'Pantitlan', 'Panteones',
    'Parque de los Venados', 'Patriotismo', 'Peñon Viejo', 'Periferico Oriente',
    'Pino Suarez', 'Plaza Aragon', 'Polanco', 'Politecnico', 'Popotla',
    'Portales', 'Potrero', 'Puebla', 'Refineria', 'Revolucion',
    'Ricardo Flores Magon', 'Rio de los Remedios', 'Romero Rubio', 'Rosario',
    'Salto del Agua', 'San Andres Tomatlan', 'San Antonio', 'San Antonio Abad',
    'San Cosme', 'San Joaquin', 'San Juan de Letran', 'San Lazaro',
    'San Pedro de los Pinos', 'Santa Anita', 'Santa Marta', 'Sevilla',
    'Tacuba', 'Tacubaya', 'Talisman', 'Tasquena', 'Tepalcates', 'Tepito','Terminal Aerea',
    'Tezonco', 'Tezozomoc', 'Tlatelolco', 'Tlaltenco', 'Tlahuac', 'UAM I',
    'Universidad', 'Valle Gomez', 'Vallejo', 'Velodromo', 'Viaducto',
    'Villa de Aragon', 'Villa de Cortes', 'Viveros/Derechos Humanos',
    'Xola', 'Zapata', 'Zapotitlan', 'Zaragoza', 'Zocalo'
]

# Crear matriz de adyacencia R inicializada con ceros (no usada directamente para distancias)
n_estaciones = len(estaciones)
R = np.zeros((n_estaciones, n_estaciones), dtype=int)

# Función para obtener índice de estación (case-sensitive)
def get_estacion_idx(estacion_nombre):
    try:
        return estaciones.index(estacion_nombre)
    except ValueError:
        print(f"Error: Estación '{estacion_nombre}' no encontrada en la lista maestra.")
        raise

# Definición de las conexiones de las líneas del Metro
# (se mantiene el código original de las líneas)
lineas_metro = {
    'L1': ['Pantitlan', 'Zaragoza', 'Gomez Farias', 'Boulevard Puerto Aereo', 'Balbuena',
           'Moctezuma', 'San Lazaro', 'Candelaria', 'Merced', 'Pino Suarez',
           'Isabel la Catolica', 'Salto del Agua', 'Balderas', 'Cuauhtemoc',
           'Insurgentes', 'Sevilla', 'Chapultepec', 'Juanacatlan', 'Tacubaya', 'Observatorio'],
    'L2': ['Cuatro Caminos', 'Panteones', 'Tacuba', 'Cuitlahuac', 'Popotla',
           'Colegio Militar', 'Normal', 'San Cosme', 'Revolucion', 'Hidalgo',
           'Bellas Artes', 'Allende', 'Zocalo', 'Pino Suarez', 'San Antonio Abad',
           'Chabacano', 'Viaducto', 'Xola', 'Villa de Cortes', 'Nativitas',
           'Portales', 'Ermita', 'General Anaya', 'Tasquena'],
    'L3': ['Indios Verdes', 'Deportivo 18 de Marzo', 'Potrero', 'La Raza', 'Tlatelolco',
           'Guerrero', 'Hidalgo', 'Juarez', 'Balderas', 'Niños Heroes',
           'Hospital General', 'Centro Medico', 'Etiopia/Plaza de la Transparencia',
           'Eugenia', 'Division del Norte', 'Zapata', 'Coyoacan',
           'Viveros/Derechos Humanos', 'Miguel Angel de Quevedo', 'Copilco', 'Universidad'],
    'L4': ['Santa Anita', 'Jamaica', 'Fray Servando', 'Candelaria', 'Morelos',
           'Canal del Norte', 'Consulado', 'Bondojito', 'Talisman', 'Martin Carrera'],
    'L5': ['Politecnico', 'Instituto del Petroleo', 'Autobuses del Norte', 'La Raza',
           'Misterios', 'Valle Gomez', 'Consulado', 'Eduardo Molina', 'Aragon',
           'Oceanía', 'Terminal Aerea', 'Hangares', 'Pantitlan'],
    'L6': ['Rosario', 'Tezozomoc', 'Azcapotzalco', 'Ferreria', 'Norte 45',
           'Vallejo', 'Instituto del Petroleo', 'Lindavista', 'Deportivo 18 de Marzo',
           'La Villa - Basilica', 'Martin Carrera'],
    'L7': ['Rosario', 'Aquiles Serdan', 'Camarones', 'Refineria', 'Tacuba',
           'San Joaquin', 'Polanco', 'Auditorio', 'Constituyentes', 'Tacubaya',
           'San Pedro de los Pinos', 'San Antonio', 'Mixcoac', 'Barranca del Muerto'],
    'L8': ['Garibaldi', 'Bellas Artes', 'San Juan de Letran', 'Salto del Agua',
           'Doctores', 'Obrera', 'Chabacano', 'La Viga', 'Santa Anita', 'Coyuya',
           'Iztacalco', 'Apatlaco', 'Aculco', 'Escuadron 201', 'Atlalilco',
           'Iztapalapa', 'Cerro de la Estrella', 'UAM I', 'Constitucion de 1917'],
    'L9': ['Pantitlan', 'Puebla', 'Ciudad Deportiva', 'Velodromo', 'Mixiuhca',
           'Jamaica', 'Chabacano', 'Lazaro Cardenas', 'Centro Medico',
           'Chilpancingo', 'Patriotismo', 'Tacubaya'],
    'LA': ['Pantitlan', 'Agricola Oriental', 'Canal de San Juan', 'Tepalcates',
           'Guelatao', 'Peñon Viejo', 'Acatitla', 'Santa Marta', 'Los Reyes', 'La Paz'],
    'LB': ['Ciudad Azteca', 'Plaza Aragon', 'Olimpica', 'Ecatepec', 'Muzquiz',
           'Rio de los Remedios', 'Impulsora', 'Nezahualcoyotl', 'Villa de Aragon',
           'Bosques de Aragon', 'Deportivo Oceanía', 'Oceanía', 'Romero Rubio',
           'Ricardo Flores Magon', 'San Lazaro', 'Morelos', 'Tepito', 'Lagunilla',
           'Garibaldi', 'Guerrero', 'Buenavista'],
    'L12': ['Tlahuac', 'Tlaltenco', 'Zapotitlan', 'Nopalera', 'Olivos', 'Tezonco',
            'Periferico Oriente', 'Calle 11', 'Lomas Estrella', 'San Andres Tomatlan',
            'Culhuacan', 'Atlalilco', 'Mexicaltzingo', 'Ermita', 'Eje Central',
            'Parque de los Venados', 'Zapata', 'Hospital 20 de Noviembre',
            'Insurgentes Sur', 'Mixcoac']
}

# Inicializar R para verificar conexiones de línea (sin transbordos aquí)
for linea, estaciones_linea in lineas_metro.items():
    for i in range(len(estaciones_linea) - 1):
        try:
            idx1 = get_estacion_idx(estaciones_linea[i])
            idx2 = get_estacion_idx(estaciones_linea[i+1])
            R[idx1, idx2] = 1
            R[idx2, idx1] = 1
        except ValueError:
            pass # Ya se manejó el error en get_estacion_idx

# Definición de distancias entre estaciones (en metros)
# Se asume bidireccionalidad en el diccionario de distancias.
distancias = {
    # Línea 1
    ('Pantitlan', 'Zaragoza'): 1320, ('Zaragoza', 'Gomez Farias'): 762,
    ('Gomez Farias', 'Boulevard Puerto Aereo'): 611, ('Boulevard Puerto Aereo', 'Balbuena'): 595,
    ('Balbuena', 'Moctezuma'): 703, ('Moctezuma', 'San Lazaro'): 478,
    ('San Lazaro', 'Candelaria'): 866, ('Candelaria', 'Merced'): 698,
    ('Merced', 'Pino Suarez'): 745, ('Pino Suarez', 'Isabel la Catolica'): 382,
    ('Isabel la Catolica', 'Salto del Agua'): 445, ('Salto del Agua', 'Balderas'): 458,
    ('Balderas', 'Cuauhtemoc'): 409, ('Cuauhtemoc', 'Insurgentes'): 793,
    ('Insurgentes', 'Sevilla'): 645, ('Sevilla', 'Chapultepec'): 501,
    ('Chapultepec', 'Juanacatlan'): 973, ('Juanacatlan', 'Tacubaya'): 1158,
    ('Tacubaya', 'Observatorio'): 1262,

    # Línea 2
    ('Cuatro Caminos', 'Panteones'): 1639, ('Panteones', 'Tacuba'): 1416,
    ('Tacuba', 'Cuitlahuac'): 637, ('Cuitlahuac', 'Popotla'): 620,
    ('Popotla', 'Colegio Militar'): 462, ('Colegio Militar', 'Normal'): 516,
    ('Normal', 'San Cosme'): 657, ('San Cosme', 'Revolucion'): 537,
    ('Revolucion', 'Hidalgo'): 587, ('Hidalgo', 'Bellas Artes'): 447,
    ('Bellas Artes', 'Allende'): 387, ('Allende', 'Zocalo'): 602,
    ('Zocalo', 'Pino Suarez'): 745, ('Pino Suarez', 'San Antonio Abad'): 817,
    ('San Antonio Abad', 'Chabacano'): 642, ('Chabacano', 'Viaducto'): 774,
    ('Viaducto', 'Xola'): 490, ('Xola', 'Villa de Cortes'): 698,
    ('Villa de Cortes', 'Nativitas'): 750, ('Nativitas', 'Portales'): 924,
    ('Portales', 'Ermita'): 748, ('Ermita', 'General Anaya'): 838,
    ('General Anaya', 'Tasquena'): 1330,

    # Línea 3
    ('Indios Verdes', 'Deportivo 18 de Marzo'): 1166, ('Deportivo 18 de Marzo', 'Potrero'): 966,
    ('Potrero', 'La Raza'): 1106, ('La Raza', 'Tlatelolco'): 1445,
    ('Tlatelolco', 'Guerrero'): 1042, ('Guerrero', 'Hidalgo'): 702,
    ('Hidalgo', 'Juarez'): 251, ('Juarez', 'Balderas'): 659,
    ('Balderas', 'Niños Heroes'): 665, ('Niños Heroes', 'Hospital General'): 559,
    ('Hospital General', 'Centro Medico'): 653, ('Centro Medico', 'Etiopia/Plaza de la Transparencia'): 1119,
    ('Etiopia/Plaza de la Transparencia', 'Eugenia'): 950, ('Eugenia', 'Division del Norte'): 715,
    ('Division del Norte', 'Zapata'): 794, ('Zapata', 'Coyoacan'): 1153,
    ('Coyoacan', 'Viveros/Derechos Humanos'): 908, ('Viveros/Derechos Humanos', 'Miguel Angel de Quevedo'): 824,
    ('Miguel Angel de Quevedo', 'Copilco'): 1295, ('Copilco', 'Universidad'): 1306,

    # Línea 4
    ('Santa Anita', 'Jamaica'): 758, ('Jamaica', 'Fray Servando'): 1033,
    ('Fray Servando', 'Candelaria'): 633, ('Candelaria', 'Morelos'): 1062,
    ('Morelos', 'Canal del Norte'): 910, ('Canal del Norte', 'Consulado'): 884,
    ('Consulado', 'Bondojito'): 645, ('Bondojito', 'Talisman'): 959,
    ('Talisman', 'Martin Carrera'): 1129,

    # Línea 5
    ('Politecnico', 'Instituto del Petroleo'): 1188, ('Instituto del Petroleo', 'Autobuses del Norte'): 1067,
    ('Autobuses del Norte', 'La Raza'): 975, ('La Raza', 'Misterios'): 892,
    ('Misterios', 'Valle Gomez'): 969, ('Valle Gomez', 'Consulado'): 679,
    ('Consulado', 'Eduardo Molina'): 815, ('Eduardo Molina', 'Aragon'): 860,
    ('Aragon', 'Oceanía'): 1219, ('Oceanía', 'Terminal Aerea'): 1174,
    ('Terminal Aerea', 'Hangares'): 1153, ('Hangares', 'Pantitlan'): 1644,

    # Línea 6
    ('Rosario', 'Tezozomoc'): 1257, ('Tezozomoc', 'Azcapotzalco'): 973,
    ('Azcapotzalco', 'Ferreria'): 1173, ('Ferreria', 'Norte 45'): 1072,
    ('Norte 45', 'Vallejo'): 660, ('Vallejo', 'Instituto del Petroleo'): 755,
    ('Instituto del Petroleo', 'Lindavista'): 1258, ('Lindavista', 'Deportivo 18 de Marzo'): 1075,
    ('Deportivo 18 de Marzo', 'La Villa - Basilica'): 570, ('La Villa - Basilica', 'Martin Carrera'): 1141,

    # Línea 7
    ('Rosario', 'Aquiles Serdan'): 1615, ('Aquiles Serdan', 'Camarones'): 1402,
    ('Camarones', 'Refineria'): 952, ('Refineria', 'Tacuba'): 1295,
    ('Tacuba', 'San Joaquin'): 1433, ('San Joaquin', 'Polanco'): 1163,
    ('Polanco', 'Auditorio'): 812, ('Auditorio', 'Constituyentes'): 1430,
    ('Constituyentes', 'Tacubaya'): 1005, ('Tacubaya', 'San Pedro de los Pinos'): 1084,
    ('San Pedro de los Pinos', 'San Antonio'): 606, ('San Antonio', 'Mixcoac'): 788,
    ('Mixcoac', 'Barranca del Muerto'): 1476,

    # Línea 8
    ('Garibaldi', 'Bellas Artes'): 634, ('Bellas Artes', 'San Juan de Letran'): 456,
    ('San Juan de Letran', 'Salto del Agua'): 292, ('Salto del Agua', 'Doctores'): 564,
    ('Doctores', 'Obrera'): 761, ('Obrera', 'Chabacano'): 1143,
    ('Chabacano', 'La Viga'): 843, ('La Viga', 'Santa Anita'): 633,
    ('Santa Anita', 'Coyuya'): 968, ('Coyuya', 'Iztacalco'): 993,
    ('Iztacalco', 'Apatlaco'): 910, ('Apatlaco', 'Aculco'): 534,
    ('Aculco', 'Escuadron 201'): 789, ('Escuadron 201', 'Atlalilco'): 1738,
    ('Atlalilco', 'Iztapalapa'): 732, ('Iztapalapa', 'Cerro de la Estrella'): 717,
    ('Cerro de la Estrella', 'UAM I'): 1135, ('UAM I', 'Constitucion de 1917'): 1137,

    # Línea 9
    ('Pantitlan', 'Puebla'): 1380, ('Puebla', 'Ciudad Deportiva'): 800,
    ('Ciudad Deportiva', 'Velodromo'): 1110, ('Velodromo', 'Mixiuhca'): 821,
    ('Mixiuhca', 'Jamaica'): 942, ('Jamaica', 'Chabacano'): 1031,
    ('Chabacano', 'Lazaro Cardenas'): 1000, ('Lazaro Cardenas', 'Centro Medico'): 1059,
    ('Centro Medico', 'Chilpancingo'): 1152, ('Chilpancingo', 'Patriotismo'): 955,
    ('Patriotismo', 'Tacubaya'): 1133,

    # Línea A
    ('Pantitlan', 'Agricola Oriental'): 1409, ('Agricola Oriental', 'Canal de San Juan'): 1093,
    ('Canal de San Juan', 'Tepalcates'): 1456, ('Tepalcates', 'Guelatao'): 1161,
    ('Guelatao', 'Peñon Viejo'): 2206, ('Peñon Viejo', 'Acatitla'): 1379,
    ('Acatitla', 'Santa Marta'): 1100, ('Santa Marta', 'Los Reyes'): 1783,
    ('Los Reyes', 'La Paz'): 1956,

    # Línea B
    ('Ciudad Azteca', 'Plaza Aragon'): 574, ('Plaza Aragon', 'Olimpica'): 709,
    ('Olimpica', 'Ecatepec'): 596, ('Ecatepec', 'Muzquiz'): 1485,
    ('Muzquiz', 'Rio de los Remedios'): 1155, ('Rio de los Remedios', 'Impulsora'): 436,
    ('Impulsora', 'Nezahualcoyotl'): 1393, ('Nezahualcoyotl', 'Villa de Aragon'): 1335,
    ('Villa de Aragon', 'Bosques de Aragon'): 784, ('Bosques de Aragon', 'Deportivo Oceanía'): 1165,
    ('Deportivo Oceanía', 'Oceanía'): 863, ('Oceanía', 'Romero Rubio'): 809,
    ('Romero Rubio', 'Ricardo Flores Magon'): 908, ('Ricardo Flores Magon', 'San Lazaro'): 907,
    ('San Lazaro', 'Morelos'): 1296, ('Morelos', 'Tepito'): 498,
    ('Tepito', 'Lagunilla'): 611, ('Lagunilla', 'Garibaldi'): 474,
    ('Garibaldi', 'Guerrero'): 757, ('Guerrero', 'Buenavista'): 521,

    # Línea 12
    ('Tlahuac', 'Tlaltenco'): 1298, ('Tlaltenco', 'Zapotitlan'): 1115,
    ('Zapotitlan', 'Nopalera'): 1276, ('Nopalera', 'Olivos'): 1360,
    ('Olivos', 'Tezonco'): 490, ('Tezonco', 'Periferico Oriente'): 1545,
    ('Periferico Oriente', 'Calle 11'): 1111, ('Calle 11', 'Lomas Estrella'): 906,
    ('Lomas Estrella', 'San Andres Tomatlan'): 1060, ('San Andres Tomatlan', 'Culhuacan'): 990,
    ('Culhuacan', 'Atlalilco'): 1671, ('Atlalilco', 'Mexicaltzingo'): 1922,
    ('Mexicaltzingo', 'Ermita'): 1805, ('Ermita', 'Eje Central'): 895,
    ('Eje Central', 'Parque de los Venados'): 1280, ('Parque de los Venados', 'Zapata'): 563,
    ('Zapata', 'Hospital 20 de Noviembre'): 450, ('Hospital 20 de Noviembre', 'Insurgentes Sur'): 725,
    ('Insurgentes Sur', 'Mixcoac'): 651
}

# Hacer conexiones bidireccionales automáticamente para distancias
distancias.update({(est2, est1): dist for (est1, est2), dist in list(distancias.items())}) # Usar list() para evitar RuntimeError si dict cambia de tamaño durante la iteración

# 2. CONSTRUIR MATRIZ DE ADYACENCIA CON DISTANCIAS
n_estaciones = len(estaciones)
matriz_distancias = np.full((n_estaciones, n_estaciones), np.inf)  # Inicializar con infinito

# Llenar la matriz con distancias reales
for (est1, est2), distancia in distancias.items():
    try:
        i, j = get_estacion_idx(est1), get_estacion_idx(est2)
        matriz_distancias[i, j] = distancia
        # matriz_distancias[j, i] = distancia  # Ya se maneja con .update() arriba
    except ValueError:
        pass # Error ya reportado por get_estacion_idx

np.fill_diagonal(matriz_distancias, 0) # Distancia de una estación a sí misma es 0

# 3. MATRIZ DE TRANSICIÓN BASADA EN INVERSA DE DISTANCIAS
def crear_matriz_transicion_prob(matriz_dist):
    # Invertir distancias (mayor peso = menor distancia)
    # Evitar división por cero o por infinito
    inverso_distancias = np.zeros_like(matriz_dist, dtype=float)
    non_inf_mask = (matriz_dist != np.inf) & (matriz_dist != 0)
    inverso_distancias[non_inf_mask] = 1 / matriz_dist[non_inf_mask]

    # Normalizar por filas para obtener probabilidades
    suma_filas = inverso_distancias.sum(axis=1, keepdims=True)
    # Evitar división por cero si una fila tiene solo ceros (estación sin conexiones)
    matriz_transicion = np.divide(inverso_distancias, suma_filas, where=suma_filas!=0)

    return np.nan_to_num(matriz_transicion) # Convertir NaN a 0 (para estaciones sin salida)

matriz_transicion_prob = crear_matriz_transicion_prob(matriz_distancias)


# 4. SIMULACIÓN DE TRAYECTORIAS CON PROBABILIDADES POR DISTANCIA (CADENAS DE MARKOV)
def ruta_markov_simulacion(origen, destino, matriz_transicion_prob, estaciones, n_simulaciones=10000):
    try:
        idx_origen = get_estacion_idx(origen)
        idx_destino = get_estacion_idx(destino)
    except ValueError:
        return None # La estación no existe

    rutas_encontradas = []

    for _ in range(n_simulaciones):
        estado_actual = idx_origen
        ruta_simulada = [estaciones[estado_actual]]
        visitados = {estaciones[estado_actual]} # Usar set para verificación rápida de visitados

        max_pasos = len(estaciones) * 2 # Límite para evitar bucles infinitos
        pasos = 0

        while estado_actual != idx_destino and pasos < max_pasos:
            posibles_siguientes_estados = np.where(matriz_transicion_prob[estado_actual] > 0)[0]

            if len(posibles_siguientes_estados) == 0: # No hay salidas
                break

            # Filtrar estados ya visitados para evitar ciclos (si es una ruta simple)
            posibles_siguientes_validos_idx = [
                s_idx for s_idx in posibles_siguientes_estados
                if estaciones[s_idx] not in visitados
            ]

            if not posibles_siguientes_validos_idx: # No hay caminos no visitados
                # Si no hay caminos no visitados, pero aún no se llegó al destino,
                # permitir un paso aleatorio a cualquier conectado para intentar salir del ciclo,
                # o simplemente romper si la ruta no puede avanzar sin ciclos.
                # Para rutas cortas, a menudo es mejor romper.
                break

            # Normalizar probabilidades para los estados válidos
            probabilidades_validas = matriz_transicion_prob[estado_actual, posibles_siguientes_validos_idx]
            if np.sum(probabilidades_validas) == 0: # Evitar división por cero
                break
            probabilidades_validas = probabilidades_validas / np.sum(probabilidades_validas)

            proximo_estado = np.random.choice(posibles_siguientes_validos_idx, p=probabilidades_validas)

            ruta_simulada.append(estaciones[proximo_estado])
            visitados.add(estaciones[proximo_estado])
            estado_actual = proximo_estado
            pasos += 1

        if estado_actual == idx_destino:
            # Calcular distancia total de la ruta simulada
            distancia_total = 0
            ruta_valida = True
            for i in range(len(ruta_simulada) - 1):
                try:
                    d = matriz_distancias[get_estacion_idx(ruta_simulada[i]), get_estacion_idx(ruta_simulada[i+1])]
                    if d == np.inf: # Si no hay conexión directa, esta ruta no es válida
                        ruta_valida = False
                        break
                    distancia_total += d
                except ValueError:
                    ruta_valida = False
                    break # Estación no encontrada
            if ruta_valida:
                rutas_encontradas.append((ruta_simulada, distancia_total))

    # Devolver la ruta con menor distancia encontrada entre las simuladas válidas
    if not rutas_encontradas:
        return None
    return min(rutas_encontradas, key=lambda x: x[1])[0]

# Comparación con Dijkstra (ruta más corta exacta)
def ruta_dijkstra(origen, destino, matriz_distancias, estaciones):
    G = nx.Graph()
    for i in range(n_estaciones):
        for j in range(n_estaciones):
            if matriz_distancias[i, j] != np.inf and i != j: # Asegurar que no sea np.inf y no auto-loop
                G.add_edge(estaciones[i], estaciones[j], weight=matriz_distancias[i, j])

    try:
        ruta = nx.shortest_path(G, source=origen, target=destino, weight='weight')
        distancia = nx.shortest_path_length(G, source=origen, target=destino, weight='weight')
        return ruta, distancia
    except nx.NetworkXNoPath:
        return None, np.inf
    except nx.NodeNotFound as e:
        print(f"Error: Una de las estaciones '{origen}' o '{destino}' no se encontró en el grafo. {e}")
        return None, np.inf

# ==============================================================================
# MÓDULO 3: INTEGRACIÓN Y ANÁLISIS DE RIESGO / MOVILIDAD
# (Aquí es donde combinarías los resultados de ambos módulos)
# ==============================================================================

from streamlit_lottie import st_lottie
import requests
import streamlit as st

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        st.error("❌ No se pudo cargar la animación")
        return None
    return r.json()

# Cargar la animación
lottie_tren = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_0yfsb3a1.json")

# Mostrar la animación en Streamlit
if lottie_tren:
    st_lottie(lottie_tren, speed=1, height=300, key="tren")



import streamlit as st
from PIL import Image
import base64

def crear_interfaz_adaptada(estaciones):
    # 👉 Cargar el logo local (asegúrate de que esté en la misma carpeta)
    with open("metro_logo.png", "rb") as f:
        logo_data = f.read()
    logo_base64 = base64.b64encode(logo_data).decode()

    # 👉 Encabezado con fondo naranja y logo local embebido
    st.markdown(
        f"""
        <div style="background-color:#FF5C00; padding:15px; border-radius:10px; display:flex; align-items:center;">
            <img src="data:image/png;base64,{logo_base64}" width="50" style="margin-right:20px;" />
            <h1 style="color:white; margin:0;">Planificador de Rutas del Transporte Colectivo Metro</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color: #333;'>Selecciona origen, destino y descubre la mejor ruta</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 👉 Controles de entrada
    col1, col2 = st.columns(2)
    with col1:
        origen = st.selectbox("📍 Estación de Origen:", sorted(estaciones))
    with col2:
        destino = st.selectbox("🎯 Estación de Destino:", sorted(estaciones))

    simulaciones = st.slider("🔁 Número de simulaciones (Markov)", 10000, 200000, 50000, step=10000)

    if origen == destino:
        st.warning("⚠️ Las estaciones de origen y destino deben ser diferentes.")
        return

    if st.button("🚀 Calcular Rutas"):
        st.markdown("---")
        st.markdown("### 🔍 Resultados del análisis de rutas")

        ruta_markov = ruta_markov_simulacion(origen, destino, matriz_transicion_prob, estaciones, simulaciones)
        ruta_dijk, dist_dijk = ruta_dijkstra(origen, destino, matriz_distancias, estaciones)

        with st.expander("📈 Ruta Simulada con Markov"):
            if ruta_markov:
                dist_markov = sum(
                    matriz_distancias[get_estacion_idx(ruta_markov[i]), get_estacion_idx(ruta_markov[i+1])]
                    for i in range(len(ruta_markov) - 1)
                )
                st.success("✅ Ruta simulada encontrada")
                st.write(" → ".join(ruta_markov))
                st.write(f"📏 Distancia total: {dist_markov:,.0f} metros")
                st.write(f"🛑 Número de estaciones: {len(ruta_markov)}")
            else:
                st.error("❌ No se encontró una ruta válida usando simulación.")

        with st.expander("🧭 Ruta Óptima con Dijkstra"):
            if ruta_dijk:
                st.success("✅ Ruta óptima encontrada")
                st.write(" → ".join(ruta_dijk))
                st.write(f"📏 Distancia total: {dist_dijk:,.0f} metros")
                st.write(f"🛑 Número de estaciones: {len(ruta_dijk)}")
            else:
                st.error("❌ No existe conexión entre estas estaciones.")

        if ruta_markov and ruta_dijk:
            diferencia = dist_markov - dist_dijk
            eficiencia = (dist_dijk / dist_markov) * 100 if dist_markov > 0 else 0
            st.info(f"🔍 Comparación: La ruta óptima es {diferencia:,.0f} metros más corta ({eficiencia:.1f}% de eficiencia).")

        st.markdown("---")
        st.success("✅ ¡Análisis completado!")




# Ejecutar la interfaz
crear_interfaz_adaptada(estaciones)
