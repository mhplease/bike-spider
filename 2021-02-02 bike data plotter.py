# this script plots the bike database data

import pandas as pd
import sqlite3
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import seaborn as sns


def add_median_labels(ax):
    lines = ax.get_lines()
    # determine number of lines per box (this varies with/without fliers)
    boxes = [child for child in ax.get_children() if type(child).__name__ == 'PathPatch']
    lines_per_box = int(len(lines) / len(boxes))
    # iterate over median lines
    for median in lines[4:len(lines):lines_per_box]:
        # display median value at center of median line
        x, y = (data.mean() for data in median.get_data())
        text = ax.text(x, y, f'{y:.1f}', ha='center', va='center',
                       fontweight='bold', color='white')
        # create median-colored border around white text for contrast
        text.set_path_effects([
            path_effects.Stroke(linewidth=3, foreground=median.get_color()),
            path_effects.Normal(),
        ])

#connect to sqlite database
con = sqlite3.connect("bikes3.sqlite")

# Load the data into a DataFrame - do not include "other" brands
bike_db = pd.read_sql_query("SELECT * from Listings WHERE brand <> 'other'", con)
bike_db_other = pd.read_sql_query("SELECT * from Listings", con)

print(bike_db.info())
print(bike_db.head(10))


#try a combined list of brand count and avg price
brand_price_vol=bike_db.groupby('brand').agg(['mean','count','median']).price.sort_values('median')
print(brand_price_vol)
brand_price_vol.to_csv("brand_price_vol.csv", encoding='utf-8')

#get a list of brands ordered by median price
blist=brand_price_vol.sort_values('median').index.values.tolist()

#get the top N markets by number of branded listings
market_size=bike_db.groupby('location').size().sort_values().nlargest(75)
print(market_size)
market_size.to_csv("market_size.csv", encoding='utf-8')


#filter main data to only include top 50 markets
top_market_listsings=bike_db[bike_db['location'].isin(market_size.index)]

#do a box plot of the prices
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (35, 15),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)


#price vs location plot for the top markets
plt.figure(figsize=(120, 15))
sns_plot=sns.boxplot(x='location', y='price', data=top_market_listsings, showfliers=False)
plt.xlabel("Location")
plt.xticks(rotation=75, ha="right")
plt.ylabel("Bike Prices")
plt.title("Bike Prices by Location")

add_median_labels(sns_plot.axes)

fig=sns_plot.get_figure()
fig.savefig("pricevlocation.png")


# plt.figure(figsize=(20, 20))
# sns_plot=sns.scatterplot(x='mean', y='count', hue='mean', palette='summer', x_jitter=True, y_jitter=True, s=125, data=brand_price_vol)
# plt.legend(fontsize=12)
# plt.xlabel("Avg Price", fontsize=18)
# plt.ylabel("Number Available", fontsize=18);
# plt.title("Price vs. Availabilty", fontsize=18);

# fig=sns_plot.get_figure()
# fig.savefig("bikescatter.png")

# # bike brand boxplot
# # compute median per group and find index after sorting
# sorted_index = top_market_listsings.median().sort_values().index
# sorted_data=top_market_listsings[sorted_index]


#boxplot of brand vs price
plt.figure(figsize=(120, 15))
sns_plot=sns.boxplot(x='brand', y='price', data=bike_db, showfliers=False, order=blist)
plt.xlabel("Brand")
plt.xticks(rotation=75, ha="right")
plt.ylabel("Bike Prices")
plt.title("Bike Prices by Brand")

add_median_labels(sns_plot.axes)


fig=sns_plot.get_figure()
fig.savefig("bikepricebox.png")



