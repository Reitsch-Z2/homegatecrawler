"""Piece of code used for creating the structure of the dict_config file, in which different type of data is
formatted and saved, and used later on for multiple actions """

from hgc_modules.functions import *

dict_config = {}
dict_config['real_estate_options'] = {1:['buy'], 2:['rent'], 3: ['buy', 'rent']}
dict_config['typologies'] = {'buy':{}, 'rent':{}}
dict_config['cities'] = []
dict_config['db_table_names'] = []

#create first dict_config structure, before doing an url update
# pickle_out(dict_config, 'D:\Python projects\HomeGateCrawler\dict_config')

dict_config=pickle_in('dict_config')

print(dict_config['real_estate_options'])
print(dict_config['typologies'])
print(dict_config['cities'])
print(dict_config['db_table_names'])

print(dict)
