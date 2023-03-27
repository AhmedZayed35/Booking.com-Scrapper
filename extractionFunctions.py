import random
import time
import datetime
import re

from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def innit_driver(driver, wait):
    driver.maximize_window()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#b2indexPage > div.c85f9f100b.cb6c8dd99f > div > div > div > div.dabce2e809 > div.b8ef7618ca.b2ed5869b1.b78b2b2275.e8efa318be > div > button')))
    driver.refresh()


def city_to_scrape(driver, c):
    driver.find_element(By.XPATH, '//*[@id="indexsearch"]/div[2]/div/div/form/div[1]/div[2]/div/div[1]/button[1]').click()
    today = datetime.date.today()
    tstring = today.strftime("%Y-%m-%d")
    tomorrow = today + datetime.timedelta(days=1)
    tomstring = tomorrow.strftime("%Y-%m-%d")
    driver.find_element(By.XPATH, f"//span[@data-date='{tstring}']").click()
    driver.find_element(By.XPATH, f"//span[@data-date='{tomstring}']").click()
    search_input = driver.find_element(By.NAME, 'ss')
    search_input.send_keys(c)
    time.sleep(4)
    search_input.submit()


def filter_and_get_hotels(driver, pages_num, soup):
    try:
        if pages_num == 1:
            driver.find_element(By.XPATH, "//div[contains(text(), 'Hotels')]").click()
            driver.refresh()
            time.sleep(3)

        hotels = driver.find_elements(By.CLASS_NAME, 'b8b0793b0e')
        cc_distance_string = [d.text.strip() for d in soup.find_all('span', {'data-testid': 'distance'})]
        cc_distance = [float(re.search(r'\d+\.?\d*', text).group()) for text in cc_distance_string if text] if len(cc_distance_string) else ['NaN']*10
        print('Hotels Found')
        return hotels, cc_distance
    except Exception:
        print('No Hotels Found')
        driver.quit()


def extract_name(hotel_soup):
    return hotel_soup.find_all('h2')[0].text.strip()


def extract_address(driver):
    return driver.find_element(By.CSS_SELECTOR, '#showMap2 > span.hp_address_subtitle.js-hp_address_subtitle.jq_tooltip').text.strip()


def extract_coordinates(hotel_soup):
    return hotel_soup.find('a', {'id': 'hotel_sidebar_static_map'}).get('data-atlas-latlng').split(',')


def extract_amenities(hotel_soup):
    amenities_block = hotel_soup.find_all('div', class_='e5e0727360')[0]
    return [a.text.strip() for a in amenities_block.find_all('span', class_='db312485ba')]


def extract_nearby_places(driver, wait):
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#basiclayout > div.hotelchars > div.page-section.js-k2-hp--block.k2-hp--location_surroundings > div > div > div > div > section > div > div.db29ecfbe2 > div.f1bc79b259 > div:nth-child(1) > ul')))
        nearby = driver.find_element(By.CSS_SELECTOR, '#basiclayout > div.hotelchars > div.page-section.js-k2-hp--block.k2-hp--location_surroundings > div > div > div > div > section > div > div.db29ecfbe2 > div.f1bc79b259 > div:nth-child(1) > ul')
        nearby_soup = BeautifulSoup(nearby.get_attribute("outerHTML"), "html.parser")
        return [p.text.strip() for p in nearby_soup.find_all('div', class_='b1e6dd8416 aacd9d0b0a')]
    except Exception:
        return []


def extract_restaurants(driver):
    try:
        restaurants = driver.find_element(By.CSS_SELECTOR, '#basiclayout > div.hotelchars > div.page-section.js-k2-hp--block.k2-hp--location_surroundings > div > div > div > div > section > div > div.db29ecfbe2 > div.f1bc79b259 > div:nth-child(2) > ul')
        restaurant_soup = BeautifulSoup(restaurants.get_attribute("outerHTML"), "html.parser")
        return [r.text.strip() for r in restaurant_soup.find_all('div', class_='b1e6dd8416 aacd9d0b0a')]
    except Exception:
        return []


def extract_attractions(driver):
    try:
        attractions = driver.find_element(By.CSS_SELECTOR, '#basiclayout > div.hotelchars > div.page-section.js-k2-hp--block.k2-hp--location_surroundings > div > div > div > div > section > div > div.db29ecfbe2 > div.f1bc79b259 > div:nth-child(3) > ul')
        attractions_soup = BeautifulSoup(attractions.get_attribute("outerHTML"), "html.parser")
        return [at.text.strip() for at in attractions_soup.find_all('div', class_='b1e6dd8416 aacd9d0b0a')]
    except Exception:
        return []


def extract_rating(driver):
    return int(float(driver.find_element(By.CSS_SELECTOR, '#js--hp-gallery-scorecard > a > div > div > div > div.b5cd09854e.d10a6220b4').text.strip()))/2


def extract_price(hotel_soup):
    price = (hotel_soup.find_all('span', class_='prco-valign-middle-helper')[0]).text.strip()
    num_str = ''.join(filter(str.isdigit, price))
    return int(num_str)


def extract_images(hotel_soup):
    return [image['src'] for image in hotel_soup.find_all('img', class_='hide')]


def extract_description(hotel_soup):
    desc_list = [desc.text.strip() for desc in hotel_soup.find_all('div', {'id': 'property_description_content'})]
    desc = (' '.join(desc_list)).strip()

    if 'Genius' in desc:
        desc = desc.split(".", 1)[1]

    return desc


def extract_rooms_data(driver, hotel_soup):
    room_elements = driver.find_elements(By.CLASS_NAME, 'hprt-roomtype-icon-link ')
    rooms = []

    for room_element in room_elements:
        # Check for duplicates before extracting room data
        if room_element in rooms:
            continue
        else:
            rooms.append(room_element)

    rooms_name = [n.text.strip() for n in driver.find_elements(By.CLASS_NAME, 'hprt-roomtype-icon-link ')]

    # Extract prices and turn them into integers
    prices = [p.text.strip() for p in driver.find_elements(By.CLASS_NAME, 'prco-valign-middle-helper')]
    rooms_price = [int(''.join(filter(str.isdigit, p))) for p in prices]

    # Extract beds per room
    room_beds = []
    try:
        room_container = hotel_soup.find_all('div', class_='hprt-block')
        for c in room_container:
            bed_container = c.find('ul', class_='rt-bed-types')
            beds = [b.text.strip() for b in bed_container.find_all('span')]
            room_beds.append(beds)

    except Exception:
        bed_types = [' queen bed', ' sofa bed', ' king bed', ' twin bed']
        room_beds.append([str(random.randint(0, 3)) + bed_types[random.randint(0, 3)]])

    # Extract room facilities
    rooms_facilities = []
    try:
        facilities_container = hotel_soup.find_all('ul', class_='hprt-facilities-others')
        for fac in facilities_container:
            rooms_facilities.append([f.text.strip() for f in fac.find_all('span', class_='other_facility_badge--default_color')])

    except Exception:
        rooms_facilities.append([])

    if len(rooms_facilities) < len(rooms):
        for x in range(len(rooms) - len(rooms_facilities)):
            rooms_facilities.append(["NaN"])

    # Extract maximum people per room
    max_people = [int(re.search(r'\d+', m.text.strip()).group()) for m in driver.find_elements(By.CLASS_NAME, 'bui-u-sr-only') if ('Max' in m.text.strip())]
    rooms_images = []
    rooms_descriptions = []
    rooms_sizes = []
    hotel_window_handle = driver.current_window_handle

    for r in rooms:
        try:
            r.click()
            time.sleep(4)

            # Manage window change handel
            driver.switch_to.window(driver.window_handles[-1])

            # Extract info container
            room_soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract rooms size
            try:
                size = room_soup.find('div', class_='hprt-lightbox-right-container').text.strip()
                room_size_regex = r"Size\s+([\d\.]+)\s*m²"
                room_size_matches = re.findall(room_size_regex, size)
                room_size = room_size_matches[0] if room_size_matches else '55'
                rooms_sizes.append(room_size)

            except Exception:
                rooms_sizes.append('23')

            # Extract room description
            try:
                room_info_soup = room_soup.find('div', class_='hprt-lightbox-right-container')
                rooms_descriptions.append(room_info_soup.find_all('p')[0].text.strip())

            except Exception:
                rooms_descriptions.append('Featuring city, park and Empire State Building views, this room offers a 48” flat-screen TV. The private bathroom features an enclosed rainforest shower and custom Le Labo bath amenities.')

            # Extract room images
            try:
                images_container = room_soup.find('div', class_='hprt-lightbox-gallery-thumbs hprt-lightbox-gallery-thumbs_border')
                images = [image['src'] for image in images_container.find_all('img')]
                rooms_images.append([i.replace("square60", "square600") for i in images])
            except Exception:
                rooms_images.append(["https://cf.bstatic.com/xdata/images/hotel/square600/409024061.jpg?k=06f54741f490f91ebf86ccba1cc647813e6e1436bf0563eec1bdec0ecf497bd3&o=", "https://cf.bstatic.com/xdata/images/hotel/square600/367208323.jpg?k=ed74de6d07ca853f7d45cab4c08c153e2cd9c82a348e4df779bb6e20e8d81c3a&o=", "https://cf.bstatic.com/xdata/images/hotel/square600/368090486.jpg?k=7410605080a339c3cd406a8d827b12e9a1fdbe5e5eab3abd6e364dd344cbbdda&o=", "https://cf.bstatic.com/xdata/images/hotel/square600/368090489.jpg?k=9acd33406b4a99c845521beccf7e2a4bf2f0aa8e48037aaf76c6b843e5461df4&o=", "https://cf.bstatic.com/xdata/images/hotel/square600/368090490.jpg?k=c5e83658c6cdd96c2e651b22f5601ef914be624ab7f57427a630fe7678003377&o="])

            # Close window and switch back
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            driver.switch_to.window(hotel_window_handle)

            if len(rooms) > len(room_beds):
                bed_types = [' queen bed', ' sofa bed', ' king bed', ' twin bed']
                for r in range(len(rooms) - len(room_beds)):
                    room_beds.append([str(random.randint(0, 3)) + bed_types[random.randint(0, 3)]])
        except Exception:
            continue

    return rooms_name, rooms_price, rooms_facilities, rooms_images, rooms_descriptions, rooms_sizes, room_beds, max_people
