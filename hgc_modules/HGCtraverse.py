"""Mini module contains the main function for traversing/going through the website"""

from hgc_modules.HGCupdater import *


def site_traversing():
    """Function used to prompt the user what he/she wants to do - search for new ads, update existing ones,
    or scrape the general data from the site to update the dict_config while which is used for many things in
    the scraper"""

    # map new or update existing ads or check if the website changed names of main elements & save changes to dict_config

    dict_config = pickle_in('dict_config')
    next_step=options_display(prompter['txt_a'], 4)
    dict_real_estate_typologies=dict_config['typologies']

    if next_step==1:    # check for new ads
        global db_name; global db; global cursor

        mode=options_display(prompter['txt_e'], 3)  # prompt the user if he/she wants to find just the recent/new ads

        next_step_type=options_display(prompter['txt_b'], 3)    # prompt if buy, rent, or buy&rent options get searched
        url_path_type=dict_config['real_estate_options'][next_step_type]

        url_path_typologies=typology_parser(dict_real_estate_typologies, url_path_type) #prompt for real estate types

        next_step_places=options_display(prompter['txt_c'], 3)  # prompt for cities/locations to be searched
        url_path_places = places_testing[next_step_places]

        for a in url_path_type:  # create tables from all combinations of the 3 prompted values above & loop through ads
            for b in list(url_path_typologies[a].values()):
                db_table_name = db_table_and_column_proofer(('_').join([db_name, a, b]))
                print(db_table_name)
                cursor.execute("CREATE TABLE IF NOT EXISTS {} (id_ad INTEGER PRIMARY KEY NOT NULL, "
                               "ad_reference INTEGER, url TEXT, title TEXT, date TEXT)"
                               .format(db_table_name))
                for c in url_path_places:
                    looper_mapping(matches_page.format(a,b,c), [a,b], db_table_name, mode)

    if next_step==2:        # scrape and fill out the data for all the mapped & non-filled ads in the db
        ad_to_db()
        site_traversing()

    if next_step==3:        # check if the structure of the relevant data on the webpage has changed & save the changes
        url_format_revision()

    if next_step==4:
        sys.exit(0)