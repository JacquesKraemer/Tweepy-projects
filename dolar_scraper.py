import requests
from bs4 import BeautifulSoup
import pandas as pd
import tweepy
import os

url = "https://dolarhoy.com/"
dolar_hoy = requests.get(url)

if dolar_hoy.status_code == 200:
    soup = BeautifulSoup(dolar_hoy.content, 'html.parser')

    # Buscar todas las cotizaciones
    cotizaciones = soup.find_all("div", class_="tile is-child")

    actualizado = soup.find("div", class_="tile is-child")
    hora_cotización = actualizado.find("div", class_="tile update")
    hora_cotización = hora_cotización.text.strip().lower()

    # Lista para almacenar los datos
    datos_cotizaciones = []

    for cotizacion in cotizaciones:
        title = cotizacion.find("a", class_="title")
        values = cotizacion.find("div", class_="values")

        if values:
            venta = values.find("div", class_="venta")
            variacion = venta.find(
                "div", class_="var-porcentaje") if venta else None

            # Extraer valores de venta
            valor_venta = venta.find(
                "div", class_="val").text.strip() if venta else "No disponible"

            # Extraer variación como valor numerico
            try:
                valor_variacion = variacion.text.strip().replace('%', '')
                valor_variacion = float(valor_variacion)
            except Exception:
                valor_variacion = variacion.text.strip().replace('%', '').replace(',', '.')
                valor_variacion = float(valor_variacion)

            # Guardar datos en la lista si variación es distinto a cero
            if valor_variacion != 0:
                datos_cotizaciones.append({
                    "Nombre": title.text.strip() if title else "No disponible",
                    "Venta": valor_venta,
                    "Variación": valor_variacion
                })
            else:
                pass
else:
    print("Error al obtener el HTML")

df_cotizaciones = pd.DataFrame(datos_cotizaciones)
df_cotizaciones = df_cotizaciones.sort_values(by="Variación", ascending=False) 

lista_textos = []

for index, row in df_cotizaciones.iterrows():
    nombre = row['Nombre']
    
    if nombre == "Dólar MEP/Bolsa":
        nombre = "Dólar MEP"
    else:
        pass    
    
    venta = row['Venta']
    variacion = row['Variación']
    emoji = "📈" if variacion > 0 else "📉"
    
    texto = f"{nombre}, cotiza a {venta} |{emoji} {variacion}%"
    lista_textos.append(texto)

bloque_texto = "\n".join(lista_textos)

# Agregar la hora de cotización al inicio del bloque de texto
texto_cotizaciones = f"Dólar #Argentina 🇦🇷 \n{bloque_texto}"

# Crear un tweet
try:
    consumer_key = os.environ["consumer_key"]
    consumer_secret = os.environ["consumer_secret"]
    access_token = os.environ["access_token"]
    access_token_secret = os.environ["access_token_secret"]

    print("Keys encontradas, intentando subir el tweet")
    
    client = tweepy.Client(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret
    )

    response = client.create_tweet(text=texto_cotizaciones)
except KeyError:
    print("Error con las keys: NO SE PUDO ACCEDER A X")
    pass
