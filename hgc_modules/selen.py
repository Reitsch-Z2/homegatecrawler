"""General selenium functions that are used throughout the code on multiple occasions - non-related to the website"""

from hgc_modules.functions import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


#dictionary used for chain-searches of web_elements within the 'get_webelement' function via the 'getattr' method
query_functions={
    'ec':'find_element_by_class_name',
    'ec-s':'find_elements_by_class_name',
    'exp':'find_element_by_xpath',
    'eid':'find_element_by_id',
    'ecss':'find_element_by_css_selector',
    'ecss-s':'find_elements_by_css_selector',
    'get':'get_attribute',
    'etn':'find_element_by_tag_name',
    'etn-s':'find_elements_by_tag_name'
    }



def options_formatting(text, position):
    """Used to parse the option from the relevant 'prompter' dictionary string value"""
    start_index = text.find(str(position))
    end_index = text.find(str(position+1))
    text = text[:end_index-1]
    text = text[start_index+2:]
    return text

def get_webelement(base_element, arg_chain):
    """Finds the parent webelement and optionally (depending on the number of args) creates a child/succession/chain of
    sub-webelements. First argument should be webdriver by default, could be a webelement also. Arguments are 2 element
    tuples (strings) - first element describes the method for finding the webelement, second element is a string
    to be searched for"""

    element = base_element

    for arg in arg_chain:
        try:
            element = getattr(element,query_functions[arg[0]])(arg[1])
        except NoSuchElementException:
            return None
        except Exception as e:
            print(e)

    return element

def text_extract(webelement):
    """Gets the text out of a webelement; in case the element is already a string, it returns it without getting 
    the text from it; in case there is no text or the webelement cannot hold text, it returns a string that is
    searchable afterwards via a double exclamation mark prefix"""

    try:
        if type(webelement) != str:
            text = getattr(webelement, 'text')
            return text
        else:
            return webelement
    except Exception as e:
        return '!! ' + str(webelement)

    #***(to be checked - probably textContent should be used as an alternative attribute to be extracted)#TODO

def list_to_dict(webelement, key='unsorted'):
    """"Takes a list (in the form of found webelements) and creates a dictionary from it - list items are keys,
    all values are equal to 'yes'... In case it is a singular element, an additional argument 'key' is needed,
    which acts as a dictionary key for the value taken from the singular webelement... default key value is 
    'unsorted', which is used for elements for which it was not possible to extract text*** """

    lst=[]; dct={}
    try:
        if isinstance(webelement, list):
            for element in webelement:
                lst.append(text_extract(element))
            for element in lst:
                dct[element] = 'yes'
        else:
            dct[key]=text_extract(webelement)
    except Exception as e:
        print(e)
        return None
    return dct


def two_lists_to_dict(a,b):
    """Takes two lists (webelements) and returns a dictionary from the zipped values, while extracting the text via
    the text_extract function... In case of a scenario where there is no text to extract, nested function text_extract
    will return a proofing string with two exclamation marks"""
    dict = {}
    for x, y in zip(a, b):
        dict[text_extract(x)] = text_extract(y)
    return dict

def ad_scraper(*args):
    """While on a webpage, it takes arguments which both get the webelements and parse them into mini dictioniaries.
    These dictionaries are combined into a master dictionary, which is returned and used for database entries -
    dictionary keys are column names, dictionary values are values for the relevant database entries"""

    test_dict={}
    end_dict={}
    for arg in args:
        test_dict={**test_dict, **arg}

    for key,value in test_dict.items():
        end_dict[db_table_and_column_proofer(key)]=value
    return end_dict

def zoom(driver, zoom=100):
    """Takes the webdriver argument + an argument of integer type, the value of which will define how much we zoom in
    or out on the webpage that is active at the moment; default is 100 = zoom 100%"""
    driver.execute_script("document.body.style.zoom='{}%'".format(zoom))

def scroll(driver, webelement, ydif=0):
    """Takes the webdriver + two other arguments - the webelement to which to scroll to, and the pixels
    for the subsequent scrolling adjustment along the y-axis - positive or negative, relative to the webelement"""
    driver.execute_script("arguments[0].scrollIntoView();", webelement)
    driver.execute_script("window.scrollBy({},{})".format(0, ydif), "")

