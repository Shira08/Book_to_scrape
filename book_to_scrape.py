import requests
import csv
from bs4 import BeautifulSoup

# URL de la page principale
url = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
page = requests.get(url)

# Analyse de la page principale
soup = BeautifulSoup(page.content, 'html.parser')

# Trouver tous les articles
articles = soup.find_all("article", {"class": "product_pod"})

# Extraire les liens vers les pages des produits
links = []
for article in articles:
    div_image = article.find('div', {"class": "image_container"})
    link_a = div_image.find("a")
    href = link_a.get('href')
    links.append(href)

# Détails du premier produit
product_one_url = links[0]
transform_product_urls = product_one_url.replace("../../../", "")
product_head = ['Product Url', "Product Category", "Product Title", "Product Image", "Product Description", "Rating Review"]
result = {}

product_page_details = "https://books.toscrape.com/catalogue/" + transform_product_urls
soup1 = BeautifulSoup(requests.get(product_page_details).content, 'html.parser')

# Extraire la catégorie
ul_li = soup1.find("ul", {"class": 'breadcrumb'}).find_all("li")
category_name = ul_li[2].text.strip()
result[product_head[1]] = category_name

# Extraire le titre
product_title = soup1.find('h1').text.strip()
result[product_head[2]] = product_title

# Extraire l'URL de l'image
product_image_url = soup1.find('div', {'class': 'item active'}).find("img").get('src').replace("../../", "https://books.toscrape.com/")
result[product_head[3]] = product_image_url

# Extraire la description
product_description_parent = soup1.find("article", {'class': 'product_page'})
product_description = product_description_parent.find_all("p")[3].text.strip()
result[product_head[4]] = product_description

# Extraire la note
rating_container = soup1.find('p', class_='star-rating')
rating_class = rating_container['class'][1]
result[product_head[5]] = rating_class

# Trouver la table et extraire les en-têtes et valeurs
table = soup1.find('table', {'class': 'table table-striped'})
headers = []
values = []
if table:
    trs = table.find_all('tr')
    for tr in trs:
        th_element = tr.find('th')
        td_element = tr.find('td')
        if th_element and td_element:
            headers.append(th_element.get_text(strip=True))
            values.append(td_element.get_text(strip=True))

    # Mettre à jour le dictionnaire avec les données de la table
    result.update(dict(zip(headers, values)))

# Écrire les données dans un fichier CSV
with open('output.csv', 'w', newline='', encoding='utf-8') as file_csv:
    writer = csv.DictWriter(file_csv, fieldnames=result.keys())
    writer.writeheader()  # Écrire les en-têtes
    writer.writerow(result)  # Écrire les données

# Afficher le résultat
print(result)
