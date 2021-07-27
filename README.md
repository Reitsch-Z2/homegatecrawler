HomeGateCrawler

The aim of the scraper is to allow for scraping data from the website "Homegate.ch" in a relatively customizable
way, and to add the data to an SQLite database.

Program is run via HomeGateCrawler.py in Powershell, in a virtual environment, while using Chrome driver for Selenium.

It is necessary to download Chrome driver (other ones may be optional) and to set the variable "path" in
"hgc_modules\HGCtools.py" to the path where the Chrome driver has been downloaded/copied to.

The scraper has three main goals/phases in its operation:

1. URL revisions
2. Ad mapper
3. Ad scraper

The goal of the URL revisions phase is to download all the existing places/locations from the webpage, as well as
all the typologies that can be rented/bought. This data is then saved to a pickled config dictionary, which is later
on used for creating/defining urls to be scraped. If the dict_config file does not exist, it is necessary first to
run configurator.py, and the to check/update the urls (option available when the scraper is started), because the
scraped info is entered into the dict_config file and used later on in all phases of the ad scraping.

The goal of Ad mapper is to ask the user which type of ads he/she wants to check, and to sequentially go to these
pages and get all the urls and ad reference numbers, and insert them into the database - thus allowing for subsequent
scraping of these ads (Ad mapper does not go to the ad pages themselves, it just gets the links from the search results
page). There is mode where the user is asked if he/she wants to "skip if the ad is already in the db",
which is useful when the previous mapping of the urls was not finished, and also if the user wants to "stop if the
ad is already in the db", which is used when the user mapped/got all the existing ads in a previous session, and just
wants to check for the new ones.

The Ad scraper uses the ad reference numbers and urls from the database to visit the specific ad url, and get the
standard info from it. Some general/common data is added to the same table where the Ad mapper inserted ad reference
numbers and urls, but some of the more specific pieces of data are inserted into new "child tables", thus allowing
for an easier overview (less columns in the main tables), and the option for custom queries of the database via JOIN
methods, connecting the main tables to the desired column in the children tables.

The are multiple elements which may seem superflous, but I wanted to integrate some of the micro-tools, whose function
would be either to prompt/lead the user through the scraping process, or to check if the site structure/element
nomenclature has changed over time, and to be flexible in some of those cases. Some functionalities like logging would
be planned here, but for now - I tried keeping track of the issues/exceptions by printing them out in the console.

The data available and its structuring varies a lot between the ads, and therefore, only the "non-changing" info
is entered into the main database table... All the varying data, both in structure/content, is added into a number of
sub-tables, so that the necessary data can be obtained later on via JOINS - for instance, price naming and structure
for rented real estate can be defined as per week, per year, per month, so if one wants to get all the data for a
certain type of real estate in city, he/she can use wildcards to get all columns that contain have "rent" in their name,
and all the columns that contain either the postcode or the requested city name - as wildcards.

There is additional refactoring to be done, possible increasing of modularity, as well as adding new options - this
is the first stage that could be optimized, and new functionalities can be added.










