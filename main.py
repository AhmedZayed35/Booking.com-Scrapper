import json
import extractionFunctions

from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


with open('hotels.json', 'r') as f:
    data = json.load(f)

with open('hotels_location.json', 'r') as f:
    loc_data = json.load(f)

with open('rooms_data.json', 'r') as f:
    rooms_data = json.load(f)

# Initialize variables
country = 'Paris'
city = 'France'
pages = 1
page_num = 1

# Launch the web driver
driver = webdriver.Chrome(ChromeDriverManager().install())
wait = WebDriverWait(driver, 40)
driver.get('https://www.booking.com/')

# Search for the hotels
extractionFunctions.innit_driver(driver, wait)
# Search for the hotels
extractionFunctions.city_to_scrape(driver, city)


while pages != 0:
    # Wait for the page to load
    wait.until(EC.visibility_of_element_located((By.ID, 'bodyconstraint-inner')))

    # Get the webpage content
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find all the hotels on the page
    hotels, cc_distance = extractionFunctions.filter_and_get_hotels(driver, page_num, soup)

    # Extract the required data from each hotel
    hotel_num = 0
    for hotel in hotels[:10]:
        hotel.click()
        driver.switch_to.window(driver.window_handles[1])

        # Get the webpage content
        hotel_html = driver.page_source
        hotel_soup = BeautifulSoup(hotel_html, 'html.parser')

        # Extract the hotel name
        name = extractionFunctions.extract_name(hotel_soup)

        # Extract the hotel address
        address = extractionFunctions.extract_address(driver)

        # Extract the hotel location coordinates
        hotel_location = extractionFunctions.extract_coordinates(hotel_soup)

        # Extract the amenities
        amenitiesList = extractionFunctions.extract_amenities(hotel_soup)

        # Extract nearby places
        placesList = extractionFunctions.extract_nearby_places(driver, wait)

        # Extract nearby restaurants
        restaurantsList = extractionFunctions.extract_restaurants(driver)

        # Extract nearby attractions
        attractionsList = extractionFunctions.extract_attractions(driver)

        # Extract the hotel rating
        rating = extractionFunctions.extract_rating(driver)

        # Extract the hotel price
        price = extractionFunctions.extract_price(hotel_soup)

        # Extract images links
        images = extractionFunctions.extract_images(hotel_soup)

        # Extract the description
        description = extractionFunctions.extract_description(hotel_soup)

        # Extract Rooms Information
        rooms_name, rooms_price, rooms_facilities, rooms_images, rooms_descriptions, rooms_sizes, rooms_beds, max_people = extractionFunctions.extract_rooms_data(driver, hotel_soup)

        # Add the data to files
        data.append({
            'name': name,
            'address': address,
            'distance from city center': cc_distance[hotel_num],
            'area_info': {
                'nearby places': placesList,
                'attractions': attractionsList,
                'restaurants': restaurantsList
            },
            'amenities': amenitiesList,
            'rating': rating,
            'price': price,
            'images': images,
            'city': city,
            'country': country,
            'description': description.strip()
        })

        loc_data.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': hotel_location,
            },
            'properties': {
                'name': name,
                'description': description.split(".", 1)[0]
            },
        })

        for r in range(len(rooms_images)):
            rooms_data.append({
                'name': rooms_name[r],
                'price': rooms_price[r],
                'max people': max_people[r],
                'facilities': rooms_facilities[r],
                'images': rooms_images[r],
                'description': rooms_descriptions[r],
                'size': rooms_sizes[r],
                'beds': rooms_beds[r],
                'hotel_name': name

            })

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        hotel_num += 1

    pages -= 1
    page_num += 1
    next_button = driver.find_element(By.CSS_SELECTOR, '#search_results_table > div:nth-child(2) > div > div > div.d7a0553560 > div.a826ba81c4.fa71cba65b.fa2f36ad22.afd256fc79.d08f526e0d.ed11e24d01.ef9845d4b3.b727170def > nav > div > div.f32a99c8d1.f78c3700d2 > button')
    next_button.click()
    break


# Store the data as a JSON file
with open('hotels.json', 'w') as f:
    json.dump(data, f)


with open('hotels_location.json', 'w') as f:
    json.dump(loc_data, f)


with open('rooms_data.json', 'w') as f:
    json.dump(rooms_data, f)


# Close the driver
driver.quit()
