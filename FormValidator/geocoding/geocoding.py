import pygeohash as pgh
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Geocoding:

    def __init__(self):
        self._browser = webdriver.Firefox()
        self.get_page()
    
    def close_browser(self):
        self._browser.close()
    
    def get_page(self, url='https://www.google.pt/maps/', title='Google Maps'):
        try:
            self._browser.get(url)
            self._url = self._browser.current_url
            assert title in self._browser.title
        except Exception as e:
            raise e

    def get_element_by_id(self, elem_id='searchboxinput'):
        try:
            self._elem = self._browser.find_element_by_id(elem_id)
        except Exception as e:
            raise e
    
    def compute_geohash(self, lat, lon):
        return pgh.encode(lat, lon)

    def get_coordinates(self, url):
        try:
            return [float(coord) for coord in url.split('@')[1].split(',')[:2]]
        except Exception as e:
            print("WARNING: Street not found!")

    def search(self, address):

        if 'goo' in address:
            return self.get_coordinates(requests.get(address).url)

        self.get_page()
        self.get_element_by_id()
        self._elem.send_keys(address + Keys.RETURN)

        while True:
            if self._browser.current_url != self._url:
                return self.get_coordinates(self._browser.current_url)
            
            time.sleep(5)

