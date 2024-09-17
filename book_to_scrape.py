import requests
import csv
import os
from pathlib import Path
from bs4 import BeautifulSoup

# function to download image and save in right path
def download_image(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

# Base URL of the books site
base_url = "https://books.toscrape.com/index.html"
response_ = requests.get(base_url)
soup_ = BeautifulSoup(response_.content, 'html.parser')
csv_filename="output"
# Find categories
ul_category = soup_.find('ul', {'class': 'nav-list'}).find("ul")
lis_category = ul_category.find_all('li')  # Iterate over list items

# Prepare dictionary to store results by category
results_by_category = {}

# Function for creating a new CSV file and writing results
def create_and_write_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# Iterate over each category link
for li in lis_category:
    a_category = li.find('a')
    href = a_category.get('href')

    # Skip the main index.html
    if href == "index.html":
        continue

    base_url_category = "https://books.toscrape.com/" + href

    page_number = 0
    has_next_page = True

    while has_next_page:
        # Construct the correct page URL based on page number
        page_url = base_url_category if page_number == 0 else base_url_category.replace("index.html",
                                                                                        f"page-{page_number + 1}.html")
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
                links.append(href)

            # Collect details for each product
            for link in links:
                transform_product_urls = link.replace("../../../", "")
                product_page_details = "https://books.toscrape.com/catalogue/" + transform_product_urls
                soup1 = BeautifulSoup(requests.get(product_page_details).content, 'html.parser')
                result = {}

                # Extract product category
                ul_li = soup1.find("ul", {"class": 'breadcrumb'}).find_all("li")
                category_name = ul_li[2].text.strip()
                result['Product Category'] = category_name

                # Extract product title
                product_title = soup1.find('h1').text.strip()
                result['Product Title'] = product_title

                # Extract product image URL
                product_image_url = soup1.find('div', {'class': 'item active'}).find("img").get('src').replace("../../",
                                                                                                               "https://books.toscrape.com/")
                result['Product Image'] = product_image_url
              

                # Extract product description
                product_description_parent = soup1.find("article", {'class': 'product_page'})
                product_description = product_description_parent.find_all("p")[3].text.strip() if len(
                    product_description_parent.find_all("p")) > 3 else 'No description'
                result['Product Description'] = product_description

                # Extract rating review
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
                save_folder = 'images'
                folder_name = f'{category_name}_images'
                folder_path = Path(os.path.join(save_folder, folder_name))
                #create sub folder if not exists and create images if not exists
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f'The folder name {folder_path} created or already exists.')

                # Determine the next image index using 
                existing_files = list(folder_path.glob('images_*.jpg'))
                i = len(existing_files) + 1
                img_name = f'images_{i}.jpg'
                img_path = folder_path / img_name
                
                # Download image
                download_image(result['Product Image'], img_path)
                print(f"Image saved to {img_path}")
              
                if base_url_category not in results_by_category:
                    results_by_category[base_url_category] = []
                results_by_category[base_url_category].append(result)

            # Check for the next page
            next_page = soup.find('li', class_='next')
            if not next_page:
                has_next_page = False

        else:
            print(f"Page not found (404): {page_url}")
            has_next_page = False

        # Increment page number for the next iteration
        page_number += 1

    # Write results for the current category to a CSV file
    if base_url_category in results_by_category:
        category_name_clean = category_name.replace(" ", "_").lower()
        filename = f"{csv_filename}_{category_name_clean}.csv"
        create_and_write_csv(filename, results_by_category[base_url_category])
        print(f"Results saved to {filename}")

        # Clear results for the next category
        del results_by_category[base_url_category]

print("Scraping completed and data saved to CSV files.")
