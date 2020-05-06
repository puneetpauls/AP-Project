"""
Created on Sun Apr 12 09:17:47 2018
@author: puneetpaul
"""
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from logger import Logger

log = Logger().get_logger()

sns.set(color_codes=True)


class EQPrediction():
    def __init__(self, config):
        self.base_url        = config.EARTHQUAKE_BASE_URL
        self.threadpool_size = config.THREADPOOL_SIZE
        self.timeout         = config.TIMEOUT
        self.start_date      = config.START_DATE
        self.end_date        = config.END_DATE
        self.const_bigdata = None

    def load_data(self, st, dt):
        """
        Load data for every 10 days in each call
        """
        url  = f"{self.base_url}&starttime={st}&endtime={dt}"
        log.info(f"processing url '{url}'")
        resp = requests.get(url)
        data = resp.json()
        self.check_attribute(data)

    def check_attribute(self, data):
        """
        To check for geographcal attributes for each line
        """
        dictattr = {}
        features = data.get('features')
        for feature in features:
            for prop in feature:
                if prop == "geometry" or prop == "properties":
                    value = feature[prop]
                    for attr in value:
                        if prop + "_" + attr in dictattr:
                            dictattr[prop + "_" + attr].append(value[attr])
                        else:
                            dictattr[prop + "_" + attr] = [value[attr]]

        df = pd.DataFrame(dictattr)

        if not df.empty and self.const_bigdata is None:
            self.const_bigdata = df
        elif not df.empty:
            self.const_bigdata.append(df)
        log.info("Done")

    def create_hist(self):
        """This module is used to create a statistical Histogram graph from the data"""
        dataframe = self.const_bigdata
        fig       = plt.figure()
        # Create one or more subplots using add_subplot, because you can't create blank figure
        axes      = fig.add_subplot(1, 1, 1)
        axes.hist(dataframe['properties_mag'].dropna(), bins=30)
        plt.title('properties_net')
        plt.xlabel('properties_mag')
        plt.ylabel('properties_rms')
        plt.show()

    def create_violin(self):
        """This module is used to create a statistical Violin graph from the data"""
        dataframe = self.const_bigdata
        sns.violinplot(dataframe['properties_mag'], dataframe['properties_rms'])  # Variable Plot
        sns.despine()

    def create_linechart(self):
        """This module is used to create a statistical Line Chart from the data"""
        dataframe = self.const_bigdata
        var       = dataframe.groupby('properties_sources').properties_sig.sum()
        fig       = plt.figure()
        ax1       = fig.add_subplot(1, 1, 1)
        ax1.set_xlabel('properties_sources')
        ax1.set_ylabel('Sum of properties_sig')
        ax1.set_title("properties_sources wise Sum of properties_sig")
        var.plot(kind='line')
