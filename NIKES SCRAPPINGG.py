from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def scrapear_rapido(genero, categoria, url_base, paginas=6):  # Aumentamos páginas a 6
    opciones = Options()
    opciones.add_argument("--headless")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")

    navegador = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)
    datos = []

    for pag in range(1, paginas + 1):
        url = f"{url_base}?page={pag}"
        print(f"Scrapeando {categoria} - {genero} - Página {pag}")
        navegador.get(url)
        time.sleep(2)

        productos = navegador.find_elements(By.CSS_SELECTOR, "div.product-card__body")

        for p in productos:
            try:
                nombre = p.find_element(By.CLASS_NAME, "product-card__title").text.strip()
            except:
                nombre = "Sin nombre"

            try:
                precio_texto = p.find_element(By.CLASS_NAME, "product-price").text.strip()
                precio = float(precio_texto.replace("$", "").replace(",", "").split()[0])
            except:
                precio = None

            try:
                link = p.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                link = ""

            datos.append({
                "nombre": nombre,
                "precio": precio,
                "genero": genero,
                "categoria": categoria,
                "url_producto": link
            })

    navegador.quit()
    return datos

if __name__ == "__main__":
    categorias = {
        # Hombre
        "playeras_h": ("Hombre", "playeras", "https://www.nike.com/mx/w/hombres-playeras-y-tops-9om13znik1"),
        "sudaderas_h": ("Hombre", "sudaderas", "https://www.nike.com/mx/w/hombres-sudaderas-con-y-sin-gorro-6riveznik1"),
        "chamarras_h": ("Hombre", "chamarras", "https://www.nike.com/mx/w/hombres-chamarras-y-chalecos-50r7yznik1"),
        "zapatos_h": ("Hombre", "zapatos", "https://www.nike.com/mx/w/hombres-zapatos-nik1zy7ok"),
        "pants_h": ("Hombre", "pants", "https://www.nike.com/mx/w/hombres-pants-mallas-2kq19znik1"),
        "shorts_h": ("Hombre", "shorts", "https://www.nike.com/mx/w/hombres-shorts-38fphznik1"),

        # Mujer
        "playeras_m": ("Mujer", "playeras", "https://www.nike.com/mx/w/mujeres-playeras-y-tops-5e1x6z9om13"),
        "sudaderas_m": ("Mujer", "sudaderas", "https://www.nike.com/mx/w/mujeres-sudaderas-con-y-sin-gorro-6rivez5e1x6"),
        "chamarras_m": ("Mujer", "chamarras", "https://www.nike.com/mx/w/mujeres-chamarras-y-chalecos-50r7yz5e1x6"),
        "zapatos_m": ("Mujer", "zapatos", "https://www.nike.com/mx/w/mujeres-zapatos-5e1x6zy7ok"),
        "pants_m": ("Mujer", "pants", "https://www.nike.com/mx/w/mujeres-pants-mallas-5e1x6z6tpi6"),
        "shorts_m": ("Mujer", "shorts", "https://www.nike.com/mx/w/mujeres-shorts-5e1x6z6ymx6"),

        # Unisex
        "mochilas": ("Unisex", "mochilas", "https://www.nike.com/mx/w/mochilas-y-bolsas-9xy71znik1")
    }

    total = []

    for clave, (gen, cat, link) in categorias.items():
        productos = scrapear_rapido(gen, cat, link, paginas=6)
        total.extend(productos)

    df = pd.DataFrame(total)
    df.to_csv("nike_datos_rapido_mas.csv", index=False)
    print(f"✅ Total productos extraídos: {len(df)}")



