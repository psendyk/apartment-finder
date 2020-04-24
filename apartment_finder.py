import json
import time
import csv
import http.client, urllib
from craigslist import CraigslistHousing

class ApartmentFinder():
    """
    Each apartment is represented as a json object with following properties:
    "loc" as coordinates, "url", "bed", "neigh", "price", "name"
    """
    def __init__(self, config_file):
        with open(config_file) as config:
            self.config = json.load(config)
        # Store already seen apartments
        self.apartments = {}
        # Get already listed data to only send new postings
        with open('apartments.csv', 'w') as file:
            output = csv.writer(file, delimiter='\t')
            output.writerow(["name", "price", "location", "url"])
        self.fetch_old_data()

    def apartment_filter(self, apt):
        if apt["bed"] != self.config["bed"]:
            return False
        if apt["price"] > self.config["max_price"]:
            return False
        if apt["loc"] is None:
            return False
        if len(self.config["bounding_boxes"]) > 0:
            inside = False
            for neigh, coords in self.config["bounding_boxes"].items():
                if ((coords[0][0] <= apt["loc"][1] <= coords[1][0]) and
                        (coords[0][1] <= apt["loc"][0] <= coords[1][1])):
                    inside = True
                    apt["neigh"] = neigh
                    break
            return inside
        return True

    def filter(self, apts):
        return [apt for apt in apts if self.apartment_filter(apt)]

    def write_csv(self, apts):
        apts_csv = [[apt["name"], apt["price"], apt["neigh"], apt["url"]] for apt in apts]
        with open('apartments.csv', 'a') as file:
            output = csv.writer(file, delimiter='\t')
            output.writerows(apts_csv)

    def fetch_old_data(self):
        old_data = []
        old_data.extend(self.fetch_craigslist_data())
        for apt in old_data:
            self.apartments[apt["loc"]] = apt
        print("Found {} apartments.".format(len(old_data)))
        self.write_csv(old_data)

    def fetch_new_data(self):
        new_data = []
        current_data = []
        current_data.extend(self.fetch_craigslist_data())
        for apt in current_data:
            if apt["loc"] not in self.apartments:
                new_data.append(apt)
        new_data = self.filter(new_data)
        return new_data

    def fetch_craigslist_data(self):
        cl = CraigslistHousing(site=self.config["craigslist_site"],
                area=self.config["craigslist_area"],
                category="apa",
                filters={
                    "max_price": self.config["max_price"],
                    "min_bedrooms": self.config["bed"],
                    "max_bedrooms": self.config["bed"]
                    }
                )
        res = cl.get_results(sort_by='newest', geotagged=True, limit=1000)
        apts = []
        for apt in res:
            apts.append({
                "loc": apt["geotag"],
                "name": apt["name"],
                "url": apt["url"],
                "price": apt["price"],
                "neigh": apt["where"],
                "bed": self.config["bed"]
                })
        apts_filtered = self.filter(apts)
        return apts_filtered

    def notify(self, apt):
        msg = "<a href='{}'>{}<a/> in {} for {}".format(apt["url"],
            apt["name"], apt["neigh"], apt["price"])
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": self.config["pushover_API_token"],
                "user": self.config["pushover_user_key"],
                "title": "New apartment found!",
                "message": msg,
                "html": 1
            }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        self.apartments[apt["loc"]] = apt

    def loop(self):
        while True:
            try:
                new_data = self.fetch_new_data()
                print("Found {} new apartments".format(len(new_data)))
                for apt in new_data:
                    self.notify(apt)
                self.write_csv(new_data)
                time.sleep(30 * 60)
            except:
                continue

if __name__ == "__main__":
    apt_finder = ApartmentFinder("config_private.json")
    apt_finder.loop()
