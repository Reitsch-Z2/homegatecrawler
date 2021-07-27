"""A group of functions to check if the elements of the webpage structure and the relevant nomenclature and options
on the webpage have changed - and to update the configuration file dict_config with the new data"""

from hgc_modules.HGCtools import *
import pyautogui



def city_prompter():
    """Function used to scrape all the info on cities/locations that can be searched on the website. Since these
    elements seems to be inserted into the DOM after a keyboard event, i.e. they do not exist unless two letters
    are typed into the search field, the functions uses all two-letter alphabetical combinations in order to provoke
    the display of cities/locations and then get their names, format them, and save them to the dict_config file
    so that these could later be used to create urls to be visited and scraped"""

    print('\nPlease click onto the automated browser window, and do not use the keyboard or mouse until the update '
          'is finished\n')

    dict_config = pickle_in('dict_config')
    char_list = [chr(a) for a in range(97, 123)]
    letters_list = []

    for a in char_list:
        for b in char_list:
            letters_list.append(a + b)

    try:
        driver.get("https://www.homegate.ch/en")

        search_field=get_webelement(driver, [('ecss', 'div[data-cy="Locations_searchFieldOpener"]')])

        time.sleep(0.25)
        search_field.click()
        time.sleep(0.25)
        cities = []
        for a in letters_list:
            pyautogui.press(a[0])
            pyautogui.press(a[1])
            time.sleep(1)   #TODO Selenium Wait conditions to be implemented instead of the sleep method
            locations=get_webelement(driver, [('ec-s', 'Locations_slicedItem_1R5iF')])
            for location in locations:
                try:
                    location=location.find_elements_by_tag_name('span')
                except StaleElementReferenceException as e: #TODO - add all two-letter combinations for which the
                    print(e)                                #   queries were unsuccessful to a list and loop over the
                    continue                                #   elements of the list again, until the list is empty?

                try:    # getting the text out of the webelements and formatting so that it can be used for url creation
                    prefix = location[1].text
                    suffix = location[0].text
                    if prefix=='Zip':
                        suffix=suffix[:4]
                    suffix = suffix.replace(' ', '-')
                    city_name_url=prefix+'-'+suffix
                    if city_name_url not in dict_config['cities']:
                        dict_config['cities'].append(city_name_url)
                        print('Added:', city_name_url)
                    cities.append(city_name_url)
                except Exception as e:
                    print(e)
                    continue
            pyautogui.press('backspace')
            pyautogui.press('backspace')

    finally:
        print(cities)
        print(len(cities))
        pickle_out(dict_config, 'dict_config')
        time.sleep(1)



def get_realestate_options():
    """Scraping function that gets all the real estate typologies from the webpage, and maps them based on the rent,
    buy, or rent & buy search preferences (since the available typologies are not identical between the buy and rent
    options). It updates the dict_config file, and this data is later used to create different options for the user,
    via which he/she can decide which part of the website should be scraped, i.e. which category of ads"""

    print('\nPlease click onto the automated browser window, and do not use the keyboard or mouse until the update '
          'is finished\n')

    time.sleep(5)
    dict_config = pickle_in('dict_config')
    url_buy='https://www.homegate.ch/buy/'
    url_rent='https://www.homegate.ch/rent/'
    url_suffix='/city-zurich/matching-list'
    button_list = ['buy', 'rent']

    # code to choose Zürich - just as a city placeholder for parsing the rest of the URL structure
    search_field = get_webelement(driver, [('ecss', 'div[data-cy="Locations_searchFieldOpener"]')])
    search_field.click()
    pyautogui.press('z')
    pyautogui.press('u')
    time.sleep(1)  #TODO Selenium Wait conditions to be implemented instead of the sleep method
    clicker = get_webelement(driver, [('ec-s', 'Locations_slicedItem_1R5iF')])
    clicker[0].click()
    move_mouse = get_webelement(driver, [('ec', 'HomePage_headline_1UACD')])
    move_mouse.click()

    try:
        for button in button_list:
            if button == 'buy':
                radio = get_webelement(driver, [('ecss', 'label[class$="ButtonLabel_1K9gF"]')])

            if button == 'rent':
                radio = get_webelement(driver, [('ecss', 'label[class$="leftRadio_3p4pO"]')])

            radio.click()

            typology_list = get_webelement(driver, [('ecss', 'div[class$="SelectChooseType_searchField_1zyJ0"'),
                                                    ('etn-s', 'li')])

            typology_list = list(map(lambda x: x.get_attribute('textContent'), typology_list))

            for typology in typology_list:

                print(typology)
                typologies = get_webelement(driver, [('ecss', 'div[class$="SelectChooseType_searchField_1zyJ0"')])
                option = get_webelement(driver,
                                      [('ecss', 'div[class$="SelectChooseType_searchField_1zyJ0"'),
                                       ('exp', "//*[contains(text(), '{}')]".format(typology))])

                time.sleep(0.5)
                action = ActionChains(driver)
                action.move_to_element(typologies)
                action.click()
                action.move_to_element(option)
                action.click()
                time.sleep(0.5)
                search_button = get_webelement(driver, [('ecss', 'button[data-cy="SearchBar_button"')])
                action.move_to_element(search_button)
                action.click().perform()

                url = driver.current_url
                url = url.replace(url_suffix, '')

                if button == 'buy':
                    url = url.replace(url_buy, '')
                    dict_config['typologies']['buy'][typology] = url
                else:
                    url = url.replace(url_rent, '')
                    dict_config['typologies']['rent'][typology] = url
                print(url)
                driver.get("https://www.homegate.ch/en")
                time.sleep(0.75)
    finally:
        pickle_out(dict_config, 'dict_config')
    print(dict_config)


def table_name_checker():
    """Function used to update the dict_config file with the names of the sub-tables for the database. It takes
    the scraped info from the typologies dictionary in the dict_config file, an iterates through the buy and rent
    options and their relevant typologies - forming a three-part sub-table name that is later on used for creation
    of new tables in the database."""
    global db_name

    dict_config = pickle_in('dict_config')
    typologies = dict_config['typologies']
    db_table_names = dict_config['db_table_names']
    for key in typologies.keys():
        for value in typologies[key].values():
            table_name = db_table_and_column_proofer(('_').join([db_name, key, value]))
            if table_name not in db_table_names:
                dict_config['db_table_names'].append(table_name)
    pickle_out(dict_config, 'dict_config')

def url_format_revision():
    """Umbrella function for updating the dict_config file via three functions: it updates the real estate options
    available to be searched and scraped, it does a revision of the possible database sub-table names to be
    created based on the current rent/buy + real estate typology options, and it does a general update
    of the cities/locations from the website"""

    get_realestate_options()
    table_name_checker()
    city_prompter()




