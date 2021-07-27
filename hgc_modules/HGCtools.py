"""Functions written specifically for HomeGateCrawler webpage - mostly related to scraping + saving to database"""


from hgc_modules.selen import *

import time
import sqlite3
import datetime


main_page="https://www.homegate.ch/en"
matches_page="https://www.homegate.ch/{}/{}/{}/matching-list?o=dateCreated-desc"
path =''             #TODO a path to the (chrome)driver file needs to be entered
driver=webdriver.Chrome(path)
db_name='HomeGateCrawler'
db = sqlite3.connect(f"{db_name}.sqlite")
cursor = db.cursor()


# dictionary used to display different options - mostly prompts that offer different things to be done via the script,
# and based on the user input. These (mostly) predefined options are parsed and used for creating arguments via the
# 'site_traversing' function
prompter={
    'txt_a':'\nWhat do you want to do:\n1.Check for new ads\n2.Fill in the database\n3.'
            'Check if the url formatting has changed\n4.Exit\n',
    'txt_b':'\nWhich type of ads?\n1.Buy\n2.Rent\n3.Buy and Rent\n',
    'txt_c':'\nWhich places?\n1.Zuerich(recommended)\n2.Zuerich, Geneva and Basel(recommended)\n3.All places\n',
    'txt_d':'\nWhich typologies?\n',
    'txt_e':'\nWhich mode?\n1.Stop if ID exists\n2.Skip if ID exists\n3.Exit\n'
    }

dict_config=pickle_in('dict_config')

#dictionary containing the options for the cities/groups of cities to be checked for new ads
places_testing={
    1:['city-zurich'],
    2:['city-zurich', 'city-geneva', 'city-basel'],
    3:dict_config['cities']
    }

def ad_id_finder(url):
    """Function used to parse the ad reference number from the ad url"""

    url_len=len(url)
    url_id=''
    for a in range(url_len-1,0,-1):
        if url[a] == '/':
            break
        url_id+=url[a]

    return int(url_id[::-1])

def get_date():
    """Function used to get the info on when the ad has been uploaded to the webpage - which is not that directly
    available/visible on the webpage"""


    x=get_webelement(driver, [('exp', "//*[contains(text(), 'datePosted')]"), ('get', 'innerHTML')])
    first=x.find('datePosted')
    x = x[first - 1:]
    last = x.find('\n')
    x = x[:last]
    x = x.replace('"', '')
    x = x.split(': ')
    x[1] = x[1][:18]
    my_date = datetime.datetime.strptime(x[1], '%Y-%m-%dT%H:%M:%S')
    seconds = time.mktime(my_date.timetuple())
    dict = {}
    dict['date'] = str(int(seconds))
    return dict



def looper_mapping(url, element_list, sub_table_name, mode):
    """Function used to loop over the desired groups of urls, based on the user input, and to enter the basic/stable
    data into the database; this data will later on be used for a detailed scraping of the ad data, via 'ad_to_db'
    function"""
    global db_name; global db; global cursor

    links_webelement = [('ecss-s', 'a[class$="ListItem_3AwDq"]')]
    nextpage_webelement =[('ecss', 'a[aria-label="Go to next page"]'), ('get', 'href')]

    db_query = cursor.execute(f'SELECT * FROM {sub_table_name}')
    mapped_ads=[]

    for entry in list(db_query):
        if len(list(filter(lambda x: x != None, entry))) >= 3:   #see which ads were mapped or completely scraped
            mapped_ads.append(entry[1])

    driver.get(url)

    # check to see if the page containing the searched-for ads has no results
    try:
        no_matches = get_webelement(driver, [('ecss', 'p[class$="noMatchingProperties_2ooT5"]'), ('get', 'innerText')])
        if no_matches[:6] == 'Oh no!':
            print('no results found for the criteria')
    except:
        links = get_webelement(driver, links_webelement)
        links = list(map(lambda x: x.get_attribute('href'), links))
        halt_next_page=''
        for link in links:  # search ended if the user opted to find only the new ads (all other ads previously scraped)
            if mode == 1 and ad_id_finder(link) in mapped_ads:
                print('\nAll new ads were found\n')
                halt_next_page=1
                break

            else:
                try:        # if the ads are not in the db, they get added to it - key, url and ad reference
                    if ad_id_finder(link) not in mapped_ads:
                        cursor.execute(
                            f"INSERT INTO {sub_table_name} (ad_reference, url) VALUES(?, ?)",
                            (ad_id_finder(link), link))
                except Exception as e:
                    print(e)
                else:
                    cursor.connection.commit()
                    print('Added to the database: ', link)
        if halt_next_page!=1:   # gets the next page of the paginated results on the webpage
            try:
                nextpage = get_webelement(driver, nextpage_webelement)
            except (NoSuchElementException, AttributeError):
                nextpage =None
                print('looper finished for: ', sub_table_name)

            if nextpage != None:
                looper_mapping(nextpage, element_list, sub_table_name, mode)
        else:   # stops seeking paginated results if user opted to find only the new ads
            print('looper finished for: ', sub_table_name)

def typology_parser(dict_temp, next_step_type):
    """Function used to display the string containing the real estate typologies and options for scraping,
    based on the previous user input - rent, buy, or rent and buy. The function parses the options from
    dict_config file, and displays the requested combinations, and based on the user choice searches for a specific
    singular real estate type, or all matching typologies for rent, buy, or rent & buy. It uses values from the
    'prompter' dictionary to prompt the user, and to display formatted options, with an addition of the 'All' option.
    It returns a dictionary - either with a single value, or half of the dictionary (if the choice is either buy or
    rent), or the complete dictionary (if the choice was rent & buy)"""

    if len(next_step_type) == 2:
        shared_keys = list(dict_temp['rent'].keys() & dict_temp['buy'].keys())
        print(shared_keys)
        combined_dict = {**dict_temp['rent'], **dict_temp['buy']}
        combined_dict = {k: v for k, v in combined_dict.items() if k in shared_keys}
        print(combined_dict)
        combined_list = list(combined_dict.keys())

    if len(next_step_type) == 1:
        combined_list=list(dict_temp[next_step_type[0]].keys())

    formatter = prompter['txt_d']
    for item in range(0, len(combined_list)):
        formatter += str(item + 1) + '.' + combined_list[item] + '\n'
    formatter = formatter + str(len(combined_list)+1)+'.'+ ' All '+ '\n'
    next_step_typologies = options_display(formatter, len(combined_list)+1)

    option=options_formatting(formatter, next_step_typologies)


    if 'All' in option and len(next_step_type) == 2:    # return whole dictionary
        return dict_temp
    if len(next_step_type) == 2:
        return {
                next_step_type[0]:{option:dict_temp[next_step_type[0]][option]},
                next_step_type[1]: {option:dict_temp[next_step_type[1]][option]}
                }
    elif 'All' in option and len(next_step_type) == 1:  # return half of the dictionary - either buy or rent options
        print(next_step_type)
        if next_step_type[0] == 'buy':
            del dict_temp['rent']
            print(dict_temp)
            return dict_temp
        else:
            del dict_temp['buy']
            print(dict_temp)
            return dict_temp
    else:

        return {next_step_type[0]:{option:dict_temp[next_step_type[0]][option]}}    # return a single-value dictionary



def ad_to_db():
    """Function used to check which ads have been 'mapped', i.e. which ads have the most basic info saved into the
    database, and then to visit the urls of those ads and to scrape more detailed data from those adds, but also
    to create additional tables and relevant database entries; these child-tables that are created would be used to
    query the necessary data later on via JOIN. Flexible table creation is here used mostly to tackle the issue of
    variable ad data on the relevant webpages, creating child-tables only for the available info."""

    global db_name; global db; global cursor

    dict_config = pickle_in('dict_config')['db_table_names']
    for sub_table in dict_config:
        try:
            db_query = cursor.execute(f'SELECT * FROM {sub_table}')
        except sqlite3.OperationalError as e:  # table not created yet, but will be - during scraping
            continue
        mapped_ads=[]

        for entry in list(db_query):
            if len(list(filter(lambda x: x != None, entry))) == 3:
                mapped_ads.append(entry[2])

        for url in mapped_ads:  # loop for scraping data from the webpage and into the db - main & childred tables
            driver.get(url)
            ad_reference=ad_id_finder(url)
            try:
                dictionary_main=ad_scraper(         # date and title for the main table
                    list_to_dict(
                        get_webelement(
                            driver, [('ecss', 'div[class$="_2w_d-"]'), ('etn', 'h1'),
                            ('get', 'textContent')]),'title'),
                    get_date())
                dictionary_joins=ad_scraper(        # variable ad data for sub-tables
                    two_lists_to_dict(
                        get_webelement(
                            driver, [('ecss', 'ul[id^="spotlight-at"]'), ('ec-s', 'SpotlightAttributes_label_3ETFE')]),
                        get_webelement(
                            driver, [('ecss', 'ul[id^="spotlight-at"]'), ('ec-s', 'SpotlightAttributes_value_2njuM')])),
                    list_to_dict(
                        get_webelement(driver, [('ecss', 'address[class$="_3Uq1m"]')]), 'Address'),
                    list_to_dict(
                        get_webelement(
                            driver, [('exp', "//*[contains(text(), 'Available from')]//following-sibling::dd")]),
                            'Availability'),
                    two_lists_to_dict(
                        get_webelement(driver, [('ecss', 'div[data-test="costs"]'), ('etn-s', 'dt')]),
                        get_webelement(driver, [('ecss', 'div[data-test="costs"]'), ('etn-s', 'dd')])),
                    two_lists_to_dict(
                        get_webelement(driver, [('ecss', 'div[class$="_2UrTf"]'), ('etn-s', 'dt')]),
                        get_webelement(driver, [('ecss', 'div[class$="_2UrTf"]'), ('etn-s', 'dd')])),
                    list_to_dict(get_webelement(driver, [('ecss', 'ul[class$="_1HzQj"]'), ('etn-s', 'li')])),
                    list_to_dict(
                        get_webelement(driver, [('ecss', 'p[class$="2wGwE"]'), ('get', 'textContent')]), 'Description'))
                try:    # date and ad title added to the main table
                    cursor.execute(f"UPDATE {sub_table} SET title = ?, date = ? WHERE ad_reference = ?",
                        (dictionary_main['title'], dictionary_main['date'], ad_reference))

                    for key,value in dictionary_joins.items():  # sub-tables created and filled out
                        micro_table_name = db_table_and_column_proofer(sub_table+'_'+key)
                        key=db_table_and_column_proofer(key)
                        id_ad=list(cursor.execute(
                                        f"SELECT id_ad FROM {sub_table} where ad_reference = ?", (ad_reference,)))[0][0]
                        cursor.execute(
                            f"CREATE TABLE IF NOT EXISTS {micro_table_name} "
                            f"(id_ad INTEGER PRIMARY KEY NOT NULL, {key} TEXT)")

                        cursor.execute(f"INSERT INTO {micro_table_name} (id_ad, {key}) VALUES(?, ?)", (id_ad, value))
                except Exception as e:
                    print(e)
                    continue
                else:
                    cursor.connection.commit()
                    print('Updated the data for:' + url)
            except Exception as e:
                if str(e) == "'NoneType' object has no attribute 'find'":
                    print('this is a no-longer active add: ', url)  #TODO fill the db fields with placeholder data
                                                                    #   so that it seems finished and doesn't get
                continue                                            #   selected again in the loop; or just delete it

        print('\nAd updating complete for: {}\n'.format(sub_table))






