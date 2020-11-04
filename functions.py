import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def add_percentages(df, col):
    """
    Given a dataframe having an index and a list of column,
    returns the percentages observation for each each column
    """
    
    for l in col:
        col_name = l + "_%"
        df[col_name] = df[l] / df[l].sum() * 100
    return df


def clean(data):
    """
    Delete duplicates rows
    Delete meaningless products, i.e products with with having StockCode all in alphabetical
    Keep only products with positive UnitPrice
    """
    data = data.drop_duplicates()
    # PREPROCESSING

    data['CustomerID'] = data['CustomerID'].astype('str')
    data = data[data.CustomerID != "nan"]
    
    data['StockCode'] = data['StockCode'].astype('str')
    data['StockCode'] = data['StockCode'].fillna('')
    ## Spaces and special characters are not considered alphabetical
    data['StockCode'] = data['StockCode'].str.replace(' ', '')
    
    ## Delete rows containing StockCode with only alphabetical letters
    data = data[~data.StockCode.str.isalpha()]
    
    data = data[data.StockCode != "23843"]
    
    data = data[data.UnitPrice > 0]

    return data


def add_features(data):
    """
    Add month hour, day of week 
    Calculate total price for each observation
    Add a column 'status' to indicate if a product is purchased or returned
    
    This features are needed for the analysis
    """
    data['date'] = data['InvoiceDate'].dt.date
    data['month'] = data['InvoiceDate'].dt.month
    data['hour'] = data['InvoiceDate'].dt.hour
    data['day'] = data['InvoiceDate'].dt.day_name()
    data['day_num'] = data['InvoiceDate'].dt.dayofweek


    data['TotalPrice'] = data['UnitPrice'] * data['Quantity']
    
    data['status'] = np.where(data['Quantity'] < 0, "returned", "purchased")
    
    return data

def quantity_price_plots(data, StockCode):
    
    """
    
    
    returns two time series plots of sold quantity and price
    
    The results here exclude returns
    """
    data = data[data['status'] == "purchased"]
    
    data = data[data.InvoiceDate < "2011-12-01"]
    x = data[data.StockCode == StockCode].groupby(['month']).agg({'Quantity': 'sum',
                                                              'UnitPrice':'mean'})

    plt.rcParams['figure.dpi'] = 60
    from matplotlib import rcParams
    rcParams['axes.titlepad'] = 13

    f,ax = plt.subplots(nrows = 2, sharex=True)
    f.suptitle(f"Product {StockCode}") 

    x['UnitPrice'].plot(title = f"Price fluctuations", ax = ax[0], color = "coral", style='.-');
    ax[0].axhline(x['UnitPrice'].median(), color="peachpuff",  ls='dashed');

    x['Quantity'].plot(title = f"Quantity",ax = ax[1], color = "palevioletred", style='.-');
    return plt.show()

def quantity_over_price_plot(data, StockCode):
    
    """
    Returns a line graph showing quantity change over price change
    """
    data = data[data['status'] == "purchased"]
    
    data = data[data.InvoiceDate < "2011-12-01"]
    x = data[data.StockCode == StockCode].groupby(['UnitPrice']).agg({'Quantity': 'sum'})

    x.plot(title = f"Quantity over price for product: {StockCode}", color = "green", style='.-');

    
def plot_time_series(data, aggregation_level):
    
    """
    Returns time series data aggregated at the aggregation level selected
    
    """
    x = data[data.InvoiceDate < "2011-12-01"].groupby( aggregation_level).agg({'Quantity': 'sum',
                                                                               'TotalPrice': 'sum'})
    
    x.plot(title = f'Total Price and Product Quantity aggregated by {aggregation_level}, from 2010-12-01 to 2011-12-01', style='.-')
    plt.legend(loc='best', bbox_to_anchor=(1.2,1));
    
    
def barplot_invoices(data, aggregation_level):
    
    """
    Returns time series data aggregated at the aggregation level selected
    
    """
    x = data[data.InvoiceDate < "2011-12-01"].groupby( aggregation_level).agg({'InvoiceNo':'count'})
    sns.barplot(x = aggregation_level, y = 'InvoiceNo', data = x.reset_index())
    plt.title(f'Number of Invoices by {aggregation_level}, from 2010-12-01 to 2011-12-01');
    
def aggregation_level_statistics(data, aggregation_level):
    
    """
    Aggregated data by the given aggregation level
    Returns sorted dataframe by percentages of 'TotalPrice_%', 'InvoiceNo_%', 'Quantity_%'
    """
    x = data[data.InvoiceDate < "2011-12-01"].groupby(aggregation_level).agg({'InvoiceNo': 'count',
                                                                              'Quantity': 'sum',
                                                                              'TotalPrice': 'sum'})
    x = add_percentages(x, ['InvoiceNo','Quantity','TotalPrice'])
    return x.sort_values(['TotalPrice_%', 'InvoiceNo_%', 'Quantity_%'], ascending=False)