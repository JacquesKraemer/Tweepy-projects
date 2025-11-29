import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import tweepy
import os


# Obtenemos las claves de acceso a la API
url = "https://api.invertironline.com/token"

iol_user_name = os.environ["iol_user_name"]
iol_contraseña = os.environ["iol_contraseña"]

payload = f'username={iol_user_name}&password={iol_contraseña}&grant_type=password'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Cookie': '1ea603=cI8fdW7UAhjB9Cv/Hrx8oG5/ffIsO8JuzoC7qQU2PLhtD5L1CDiBGxObOV0OysQUJyej7Wjf1QzIAW2VSUkqzxINEyzFDwlX9quDNEE4G+Ew+090qgNejY9B3uZ4300Fqf8oTSigpZ2F1H1lpXMGrrBjXOZ6owU9F8uwP/3j/HZf3uOu'
}

response = requests.request("POST", url, headers=headers, data=payload)
# Convertimos la respuesta a JSON
response_json = response.json()

# KEYS
bearer_token = response_json["access_token"]
refresh_token = response_json["refresh_token"]

# ---------------   PANEL ACCIONES ARGENTINAS  ----------------
List_panel_Acciones = ["Merval", "Panel General", "Merval 25", "Merval Argentina", "Burcap", "CEDEARs"]

panel_data = []

def obtener_panel(instrumento, panel, pais):
    
    url_panel2 = f"https://api.invertironline.com/api/Cotizaciones/{instrumento}/{panel}/{pais}"
    
    payload = {}
    headers = {
    'Authorization': f"Bearer {bearer_token}",
    'Cookie': 'i18n.langtag=es-AR; isMobile=0; 1ea603=2qWeR/Ko7fTv5qFwUUmajFxWKNKtMyB66jJlJwlyFgldqvfrivSOqffj72nSSQ8p18sxZLeNp+m5CDB+KmkD7BxBPsZzBlzrTNpk728p80GSm7j9dYAIvHBuX7tgmx5HVqjmBADYnrBeAlt9fjpu+dxROhkucWhAX8YWLux7ISiIj1gU'
    }

    response = requests.request("GET", url_panel2, headers=headers, data=payload)
    panel_data.append(response.json())

obtener_panel("Acciones", List_panel_Acciones[0], "argentina")

# panel_data_json = json.dumps(panel_data, indent=2)

ticket = []
volumen = []
precio_maximo = []
precio_minimo = []
ultimo_precio = []
var_porcentual = []

for titulo in panel_data[0]["titulos"]:
    
    ticket_t = titulo["simbolo"]
    ticket.append(ticket_t)
     
    volumen_t = titulo["volumen"]
    volumen.append(volumen_t)
    
    precio_maximo_t = titulo["maximo"]
    precio_maximo.append(precio_maximo_t)
    
    precio_minimo_t = titulo["minimo"]
    precio_minimo.append(precio_minimo_t)
    
    ultimo_precio_t = titulo["ultimoCierre"]
    ultimo_precio.append(ultimo_precio_t)
    
    var_porcentual_t = titulo["variacionPorcentual"]
    var_porcentual.append(var_porcentual_t)

data_relevante = pd.DataFrame({
    "ticket" : ticket, 
    "volumen" : volumen,
    "precio_maximo" : precio_maximo,
    "precio_minimo" : precio_minimo,
    "ultimo_precio" : ultimo_precio,
    "var_porcentual" : var_porcentual
})

data_relevante = data_relevante.sort_values(by="var_porcentual", ascending=False)

# Agregamos una columna para diferencias variaciones positivas y negativas
data_relevante['variación'] = data_relevante['var_porcentual'].apply(lambda x: 'Positivo' if x > 0 else 'Negativo')

colores = data_relevante['variación'].map(lambda x: 'green' if x == 'Positivo' else 'red')

# Crear gráfico de barras horizontales
plt.style.use('Solarize_Light2')
plt.figure(figsize=(12, 7))

# Gráfico principal
plt.barh(data_relevante['ticket'], data_relevante['var_porcentual'], color=colores)

# Titulos
plt.xlabel('Variación %')
plt.ylabel('Tickets')
plt.title('Variación diaria - Cotización del MERVAL')

# Etiquetas personalizadas en las barras
for i, (valor, nombre) in enumerate(zip(data_relevante['var_porcentual'], data_relevante['ticket'])):
    plt.text(valor, i, f'{valor:.1f}%', va='center',
             ha='left' if valor >= 0 else 'right',
             color='black', fontsize=10)

#Modificar valores del eje X
xticks = plt.xticks()[0] 
plt.xticks(xticks, [f'{x:.0f}%' for x in xticks], fontsize=10, color='black')
#Modificar valores del eje Y
plt.yticks(range(len(data_relevante['ticket'])),
           [f'{ticker.upper()}' for ticker in data_relevante['ticket']], fontsize=10, color='black')


plt.tight_layout()
plt.savefig('merval_variacion.png', dpi=300, bbox_inches='tight')
plt.close()  # Cierra la figura para liberar memoria


# -------Lista de KEYS
consumer_key = os.environ["consumer_key"]
consumer_secret = os.environ["consumer_secret"]

access_token = os.environ["access_token"]
access_token_secret = os.environ["access_token_secret"]

api_key = os.environ["api_key"]
api_key_secret = os.environ["api_key_secret"]


# ------Auth V1 y subir la imagen para obtenet su ID
def get_twitter_conn_v1() -> tweepy.API:
    """Get twitter conn 1.1"""

    auth = tweepy.OAuth1UserHandler(api_key, api_key_secret)
    auth.set_access_token(
        access_token,
        access_token_secret,
    )
    return tweepy.API(auth)


def get_twitter_conn_v2() -> tweepy.Client:
    """Get twitter conn 2.0"""

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    return client


client_v1 = get_twitter_conn_v1()
client_v2 = get_twitter_conn_v2()

image_path = "merval_variacion.png"

post = client_v1.simple_upload(image_path)
payload = post.media_id

# Ordenar los datos por variación porcentual
top_subas = data_relevante[data_relevante['var_porcentual'] > 0].sort_values(by='var_porcentual', ascending=False).head(3)
top_bajas = data_relevante[data_relevante['var_porcentual'] < 0].sort_values(by='var_porcentual', ascending=True).head(3)

# Generación de texto dinamico
if not top_subas.empty:
    subas_text = "🔼 Top tres subas del día: " + ', '.join(
        f"{row['ticket'].upper()} {row['var_porcentual']:+.1f}%" for _, row in top_subas.iterrows())
else:
    subas_text = "📉 Top tres subas del día: Not Stonks"

if not top_bajas.empty:
    bajas_text = "🔽 Top tres bajas del día: " + ', '.join(
        f"{row['ticket'].upper()} {row['var_porcentual']:+.1f}%" for _, row in top_bajas.iterrows())
else:
    bajas_text = "📈 Top tres bajas del día: Stonks"

tweet_text = (
    f"Mercado argentino - MERVAL - 🇦🇷\n\n"
    f"{subas_text}\n"
    f"{bajas_text}\n\n"
    
    "#MERVAL #Bolsa #Inversiones #Argentina"
)

# Verifica si la imagen se ha creado y luego procede a publicarla
if os.path.exists(image_path):
    print("Publicando imagen desde:", image_path)

    try:
        tweet = client_v2.create_tweet(media_ids=[payload], text=tweet_text)
        print("Se subió la imagen correctamente!")

    except Exception as e:
        print(f"Error al subir el tweet con imagen: {e}")
else:
    print("No se encontró la imagen en el path:", image_path)


#
db_url = os.getenv("NEON_DB_URL")

engine = create_engine(db_url)

df_cotizaciones.to_sql(
    name="dolar",           # nombre de la tabla (la crea si no existe)
    con=engine,
    if_exists="append",         # o "replace" si quieres borrar y volver a crear
    index=False,
    method="multi",             # mucho más rápido
    chunksize=10_000            # obligatorio para tablas grandes en Neon
)

print("DataFrame subido correctamente")






