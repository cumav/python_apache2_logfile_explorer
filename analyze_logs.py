import glob
import re
from collections import OrderedDict

from geoip import open_database


class Logcheck:

    def __init__(self, logfiles_folder, geoip_database_location='./db.mmdb'):
        self.countries = []
        self.ips = []
        self.files = glob.glob(logfiles_folder)
        self.ordered_log = [""] * len(self.files)
        self.db = open_database(geoip_database_location)
        self.sort_files()
        self.get_ip_date_n_location()

    def sort_files(self):
        '''
        sort logfiles from newest to oldest
        '''
        for item in self.files:
            try:
                val = item.split(".")
                self.ordered_log[int(val[-1])] = item
            except Exception:
                self.ordered_log[0] = item
        self.files = self.ordered_log

    def logs_to_array(self) -> list:
        '''
        gets IP
        :param filename: string of the path to the file
        :returns: converts logs to an array
        '''

        # make one long array from files, each entry is one line of the logfiles
        raw_log_dict = []
        for path in reversed(self.files):
            with open(path, "r") as temp_log_file:
                raw_log_dict.extend(temp_log_file.readlines())
        return raw_log_dict

    def get_ip_date_n_location(self):
        '''
        Generate array from logs. Each entry contains a dict in this format {"ip", "date", "country_code/location"}
        '''
        self.log_attributes = []
        logs_array = self.logs_to_array()
        for log_entry in logs_array:
            ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", log_entry)
            date_time = re.findall(r"\d{2}\/\w{3}\/\d{4}:\d\d:\d\d:\d\d", log_entry)
            location = "unlocated"
            match = self.db.lookup(ip[0])
            if match != None:
                location = match.country
            self.log_attributes.append({"ip": ip[0],
                                        "date": date_time[0],
                                        "location": location})

            # generate a list of all found locations and ips
            if location not in self.countries:
                self.countries.append(location)
            if ip[0] not in self.ips:
                self.ips.append(ip[0])

    def ranking_by_type(self, sort_type="location") -> list:
        '''
        For each country/IP get the number of log entries.
        :sort_type: Use either "location" or "date" to sort for the used key.
        :return: A list where each entry contains a tuple of ("County_code<str>", "number of entries<int>")
        '''
        ranking = {}
        for item in self.log_attributes:
            if item[sort_type] not in ranking.keys():
                ranking[item[sort_type]] = 1
            else:
                ranking[item[sort_type]] += 1
        return sorted(ranking.items(), key=lambda kv: kv[1])

    def plot_ranking(self, sort_type="location", top_n=None):
        '''
        plotting a graph using data returned from method "country_ranking"
        '''
        import numpy as np
        import matplotlib.pyplot as plt

        ranking = self.ranking_by_type(sort_type)
        values = list(map(lambda x: x[1], ranking))
        keys = list(map(lambda x: x[0], ranking))
        y_pos = np.arange(len(keys))

        if top_n is None:
            top_n = len(ranking)

        plt.bar(y_pos[-top_n:], values[-top_n:], align='center', alpha=0.5)
        plt.xticks(y_pos[-top_n:], keys[-top_n:],rotation='vertical')
        plt.ylabel('Usage')
        plt.title('Programming language usage')

        plt.show()

    def gen_daily(self, sort_type="location", return_default_list=False):
        '''
        generates a dictionary containing requests send for each day and country. Change sort_type to "ip" will give a
        list for each ip.
        :return: dictionary {day_1:{country_1: 0, country_2: 1, ... , country_n: 19}, ... ,
                 day_n:{country_1: 0, country_2: 1, ... , country_n: 19}}
        '''
        days = OrderedDict()
        if sort_type == "location":
            default_list = self.countries
        elif sort_type == "ip":
            default_list = self.ips
        item_count = {x: 0 for x in default_list}

        for entry in self.log_attributes:
            curr_date = entry["date"].split(":")[0]
            if curr_date in days.keys():
                days[curr_date][entry[sort_type]] += 1
            else:
                days[curr_date] = item_count.copy()
                days[curr_date][entry[sort_type]] += 1
        if return_default_list:
            return days, default_list
        return days

    def plot_daily(self, sort_type="location"):
        '''
        Plot Matplotlib. A chart to show where attacks are from on a daily basis
        :return:
        '''
        import matplotlib.pyplot as plt

        day_for_country = OrderedDict()
        days, search_type = self.gen_daily(sort_type, return_default_list=True)

        # For each country, put the daily count in a list
        for item in search_type:
            day_for_country[item] = [days[x][item] for x in days.keys()]

        for country in day_for_country:
            plt.plot(days.keys(), day_for_country[country])

        plt.ylabel('Usage')
        plt.legend(day_for_country.keys())
        plt.title('Programming language usage')
        plt.show()


if __name__ == "__main__":
    check = Logcheck(logfiles_folder=".\\Logfiles\\access*.log*")
    # x = check.get_ip_date_n_location()

    check.plot_ranking(sort_type="ip", top_n=50)
    print("test")
