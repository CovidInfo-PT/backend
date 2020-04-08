import pygeohash as pgh
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


"""
This class opens a Selenium client on Firefox and searchs for a location on Google Maps.
Then, it gets the coordinates present in the url and computes their geohash.
"""
class Geocoding:

    """
    Geocoding constructor.
    It opens the Firefox browser with Selenium. Then, it calls the get_page() method.
    """
    def __init__(self):
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.set_headless()
        self._browser = webdriver.Firefox(firefox_options=fireFoxOptions)
        print("Browser opened!")
        self.get_page()
    
    """
    Method to close the browser.
    """
    def close_browser(self):
        print("Browser closed")
        self._browser.close()
    
    """
    This method opens the google maps page by default.

    @param url: page to be open
    @param title: title of the page
    """
    def get_page(self, url='https://www.google.pt/maps/', title='Google Maps'):
        try:
            self._browser.get(url)
            self._url = self._browser.current_url
            print(f"Current url: {self._url}")
            assert title in self._browser.title
        except Exception as e:
            raise e

    """
    This method finds an HTML element of the DOM.
    By default, it looks for the search box of Google Maps.

    @param elem_id: HTML element to be found
    """
    def get_element_by_id(self, elem_id='searchboxinput'):
        try:
            self._elem = self._browser.find_element_by_id(elem_id)
        except Exception as e:
            raise e
    
    """
    This method computes the geohash of a specific place, given its coordinates.

    @param lat: latitude
    @param lon: longitude
    """
    def compute_geohash(self, lat, lon):
        return pgh.encode(lat, lon)

    """
    This method gets the coordinates of a specific place present in a Google Maps url.

    @param url: Google Maps url of a specific place
    """
    def get_coordinates(self, url):
        try:
            return [float(coord) for coord in url.split('@')[1].split(',')[:2]]
        except Exception as e:
            print("WARNING: Street not found!")


    """
    This main method searchs for a given address on Google Maps and returns its coordinates.

    @param address: anything that could be searched on Google Maps
    """
    def search(self, address):
        
        self._browser.set_window_size(1120,550)
        print(f"Searching for {address}")
        # google maps url
        if 'goo' in address:
            return self.get_coordinates(requests.get(address).url)

        # opens google maps page with Selenium
        self.get_page()

        # gets the search box
        self.get_element_by_id()

        # searches for the given address on Google Maps, clicking on RETURN
        self._elem.send_keys(address + Keys.RETURN)
        
        # this loop is necessary due to Google Maps redirecting
        tries = 0
        while tries < 6:
            tries += 1
            
            if self._browser.current_url != self._url:
                return self.get_coordinates(self._browser.current_url)
            
            # if Google Maps has not been redirected yet, wait for 5 seconds
            time.sleep(5)
