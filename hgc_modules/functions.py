"""General functions that are used throughout the code on multiple occasions for loading/parsing/formatting etc."""

import pickle
import signal

def pickle_in(filename):
    dictionary=pickle.load(open(filename, 'rb'))
    open(filename, 'rb').close()
    return dictionary

def pickle_out(object, filename):
    pickle.dump(object, open(filename, 'wb'))
    open(filename, 'r').close()

def Handler(signum, frame):
    """Handler for the signal - executed when CTRL+C pressed; should inevitably lead to the 'finally' clause in the
    try-except-finally block, thus allowing for a civilized shutdown. Experimental at the moment."""
    print('shutting down...')

def db_table_and_column_proofer(name):
    """function used to format a string that should represent a database or a database column name in a manner that
    is suitable when it comes to synthax and uniformity"""
    symbol_dictionary={' ': '_', '-': '_', ':':'', '.': '', '/': '','\"': '','\'': ''}
    for k,v in symbol_dictionary.items():
        name = name.replace(k, v)
    name = name.lower()
    return name

def options_display(text, scope):
    """Used to loop until a legit input in the form of an integer in the specified scope is given. Takes two arguments
    - formatted text fragment showing the enumerated options, as well as the number of options available. Loops until
    a valid integer is entered, in which case that integer is returned and used as argument in other functions"""
    try:
        choice = int(input(text))
        while int(choice) not in list(range(1,scope+1)):
            choice = int(input(f'\nPlease enter the number of the desired option.\n{text}\n'))
        return choice
    except ValueError:
        print('\nPlease enter the number of the desired option.')
        return options_display(text, scope)

