import requests
import csv
import os
from bs4 import BeautifulSoup

base_url = "https://books.toscrape.com/index.html"
response_ = requests.get(base_url)
soup_ = BeautifulSoup(response_.content, 'html.parser')

# Find categories
ul_category = soup_.find('ul', {'class': 'nav-list'}).find("ul")
lis_category = ul_category.find_all('li') # Correctly iterate over list items
print(lis_category)

# Prepare CSV file
csv_filename = 'output.csv'
file_exists = os.path.isfile(csv_filename)

# Open CSV file
with open(csv_filename, 'a', newline='', encoding='utf-8') as file_csv:
    writer = None
    
    # Iterate over each category link
    for li in lis_category:
        a_category = li.find('a')
        href = a_category.get('href')
        if href == "index.html":
            continue
        
        base_url_category = "https://books.toscrape.com/" + href
        
        page_number = 0
        has_next_page = True

        while has_next_page:
            # Construct the correct page URL based on page number
            page_url = base_url_category if page_number == 0 else base_url_category.replace("index.html", f"page-{page_number+1}.html")
            response_ = requests.get(page_url)

            if response_.status_code == 200:
                print(f"Collecting data from: {page_url}")
                soup = BeautifulSoup(response_.content, 'html.parser')
                articles = soup.find_all("article", {"class": "product_pod"})
                links = []

                # Collect product links
                for article in articles:
                    div_image = article.find('div', {"class": "image_container"})
                    link_a = div_image.find("a")
                    href = link_a.get('href')
                    if href == "index.html":
                        continue


                # Collect details for each product
                for link in links:
                    transform_product_urls = link.replace("../../", "")
#                    print(transform_product_urls )
                    product_page_details = "https://books.toscrape.com/catalogue/" + transform_product_urls
                    soup1 = BeautifulSoup(requests.get(product_page_details).content, 'html.parser')

                    result = {}
                    
                    # Extract product category
                    ul_li = soup1.find("ul", {"class": 'breadcrumb'}).find_all("li")
                    category_name = ul_li[2].text.strip() if len(ul_li) > 2 else 'Unknown'
                    result['Product Category'] = category_name

                    # Extract product details
                    product_title = soup1.find('h1').text.strip()
                    result['Product Title'] = product_title

                    product_image_url = soup1.find('div', {'class': 'item active'}).find("img").get('src').replace("../../", "https://books.toscrape.com/")
                    result['Product Image'] = product_image_url

                    product_description_parent = soup1.find("article", {'class': 'product_page'})
                    product_description = product_description_parent.find_all("p")[3].text.strip() if len(product_description_parent.find_all("p")) > 3 else 'No description'
                    result['Product Description'] = product_description

                    rating_container = soup1.find('p', class_='star-rating')
                    rating_class = rating_container['class'][1] if rating_container else 'No rating'
                    result['Rating Review'] = rating_class

                    # Extract additional information from the table
                    table = soup1.find('table', {'class': 'table table-striped'})
                    if table:
                        trs = table.find_all('tr')
                        for tr in trs:
                            th_element = tr.find('th')
                            td_element = tr.find('td')
                            if th_element and td_element:
                                result[th_element.get_text(strip=True)] = td_element.get_text(strip=True)

                    # Initialize CSV writer and write headers if not yet done
                    if writer is None:
                        writer = csv.DictWriter(file_csv, fieldnames=result.keys())
                        if not file_exists:
                            writer.writeheader()

                    # Write product details to CSV
                    writer.writerow(result)

                # Check for the next page
                next_page = soup.find('li', class_='next')
                if not next_page:
                    has_next_page = False
            else:
                print(f"Page not found (404): {page_url}")
                has_next_page = False

            # Increment page number for the next iteration
            page_number += 1

print("Scraping completed and data saved to output.csv")
