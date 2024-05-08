from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import re
import time

allLounges = []

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

with open('hoildayExtraLink.txt', 'r') as file:
    urls = file.readlines()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        for url in urls:
            try:
                url = url.strip()
                airport_code_match = re.search(r'(?<=depart=)[A-Z]+', url)
                if airport_code_match:
                    airport_code = airport_code_match.group()
                else:
                    print(f"No airport code found for URL: {url}")
                    continue
                    
                print('-'*50)
                print("Airport :",airport_code)
                context = browser.new_context(user_agent=user_agent)
            
                page = context.new_page()

                page.goto(url)
                content = page.inner_html('main.products', timeout=2000)
                soup = BeautifulSoup(content, 'html.parser')
                lounges = soup.select('li.product-item.product-lounge.block-md') 
                
                if not lounges:
                    print(f"No lounges found for URL: {url}")
                    continue

                for lounge in lounges:
                    try:
                        name_elem = lounge.find('h2', class_='h3')
                        image_elem = lounge.find('img', class_='img-responsive mx-auto d-block')
                        terminal_elem = lounge.find('div', class_='product-terminal')
                        description_heading_elem = lounge.find('strong', class_='summaryString')
                        price_elem = lounge.find('div', class_='css-1lxbtr9')
                        rating_elem = lounge.find('span', class_='css-1fzcwnz')
                        flextras_elem = lounge.find('span', class_='css-nfquzx')
                        description_elem = lounge.find('div', class_='product-selling-point')
                        time_elem = lounge.find('div', class_='product-opening-times')

                        if name_elem:
                            name = name_elem.text.strip()
                            image = 'https:' + image_elem.get('src') if image_elem else ''
                            terminal = terminal_elem.text.strip() if terminal_elem else ''
                            description_heading = description_heading_elem.text.strip() if description_heading_elem else ''
                            price = price_elem.text.strip() if price_elem else ''
                            rating = rating_elem.find('p', class_='css-1xubqqs').text.strip() if rating_elem else ''
                            rating += rating_elem.find('span', class_='css-oubmfw').text.strip() if rating_elem else ''
                            flextras_text = flextras_elem.text.strip() if flextras_elem else ''
                            flextras = flextras_text.split(": ")[1] if flextras_text else ''
                            description = description_elem.text.strip() if description_elem else ''
                            time_str = time_elem.text.strip() if time_elem else ''

                            # print(name," ",image," ", airport_code," ", terminal," ", description_heading," ", price," ", rating," ", flextras," ", description," ", time_str)
                            allLounges.append([name, image, airport_code, terminal, description_heading, price, rating, flextras, description, time_str])

                            time.sleep(1)
                    except Exception as e:
                        print(f"Error occurred while processing lounge: {str(e)}")

                context.close()
            except Exception as e:
                    print(f"Error occurred while processing Page: {str(e)}")

        browser.close()
    

with open('hoildayLoungeData.tsv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['Lounge', 'image', 'AirportCode', 'Terminal', 'Description_heading', 'Price','Rating', 'Flextras','Description','Time'])
    writer.writerows(allLounges)
