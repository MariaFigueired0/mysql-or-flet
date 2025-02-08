import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
import flet as ft
 
def extrair_titulos():
    url = 'https://g1.globo.com/'
    response = requests.get(url)
   
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        titulos = []
       
        for tag in soup.find_all('a', class_='feed-post-link'):
            titulo = tag.get_text(strip=True)
            data_tag = tag.find_previous('time', class_='content-publication-data')
            if data_tag:
                data_extracao = data_tag.get('datetime', datetime.now())  
            else:
                data_extracao = datetime.now()
               
            if titulo:  
                titulos.append((titulo, data_extracao))
       
        return titulos
    else:
        print("Erro ao acessar o site!")
        return []
 
def conectar_db():
    banco = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  
        database='noticias_db'  
    )
    return banco
 
def salvar_titulos(titulos):
    conn = conectar_db()
    cursor = conn.cursor()
   
    for titulo, data_extracao in titulos:
        query = "INSERT INTO noticias (titulo, data_extracao) VALUES (%s, %s)"
        cursor.execute(query, (titulo, data_extracao))
   
    conn.commit()
    cursor.close()
    conn.close()
 
def obter_titulos_db():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, data_extracao FROM noticias ORDER BY data_extracao DESC")
    resultados = cursor.fetchall()
    conn.close()
    return resultados



def main(page: ft.Page):
    page.title = "Notícias Extraídas"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll=ft.ScrollMode.AUTO
    page.window_width=500
    
    titulos = obter_titulos_db()
 
    lista_titulos = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True
    )
    page.add(
        ft.Row(controls=[
            ft.VerticalDivider(width=1),
            ft.Text("NOTICÍAS",style="font-weight:;", 
                    font_family="Arial")
        ],
        expand=True
        ), botton_navbar
    )
    
    for titulo, data_extracao in titulos:
        lista_titulos.controls.append(ft.Text(f"{titulo} - {data_extracao}", style="font-weight"))
   
    page.add(lista_titulos)
 
def rodar_scraping_e_salvar():
    titulos = extrair_titulos()
    if titulos:
        salvar_titulos(titulos)
    else:
        print("Nenhuma notícia encontrada!")
 
rodar_scraping_e_salvar()


botton_navbar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="explore", label="Noticias"),
            ft.NavigationBarDestination(icon=ft.icons.CALENDAR_MONTH, label="Data"),
            ft.NavigationBarDestination(icon=ft.icons.LOCK_CLOCK, label="Hora"),
        ]
    )
ft.app(target=main)
 