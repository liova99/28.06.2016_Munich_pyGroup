from flask import Flask, render_template, request

import datetime

# My password file
from app.passwords import *

import pandas as pd
import pandas.io.data as web

from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource as cds

import MySQLdb

app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'] )
def index():

    title = 'Munich PyGroup'

    # ========= Info Table =============================================
    def table_companies():
        # import companies, set and sort index, use only needed colums
        companies = pd.read_csv('static/data/companies.csv')
        companies = companies.set_index(['Symbol'])
        companies = companies.sort_index()
        companies = companies[['Name', 'IPOyear', 'Sector', 'Industry']]
        return companies

    # import info table from user input
    def info():
        if request.method == "POST":
            # 'chart' is the name of <input> tag in html file
            inf = request.form.get('chart')
        else:
            inf = 'CRME'

        companies = table_companies()

        # make max column with 150 (char?)
        pd.options.display.max_colwidth = 150
        #locate the company that user request
        info = pd.DataFrame(companies.loc[inf])

        return info

    # =============== Chart =============================================
    def finance():
        chart = 'CRME'

        if request.method == "POST":
            chart = request.form.get('chart')

        start = datetime.datetime(2010, 3, 1)

        # =========== Yahoo API ======================
        # df = web.get_data_yahoo( 'TSLA', start, end, interval='w' )
        df = web.get_data_yahoo(chart, start)

        # convert the dates for the hover tool
        dates = pd.Series(df.index)

        dates = dates.dt.strftime('%d-%m-%Y').tolist()

        # ========== Hover tools configuration ========

        # Make a list of strings for every value(the hover tool accepts only str)
        # open_p and close the _p is beqause open and close is  funcs in python
        open_p = [str(i) for i in df.Open]
        high = [str(i) for i in df.High]
        low = [str(i) for i in df.Low]
        close_p = [str(i) for i in df.Close]
        vol = [str(i) for i in df.Volume]
        adj = [str(i) for i in df['Adj Close']]

        TOOLS = 'pan,wheel_zoom,box_zoom,hover,crosshair,resize,reset'

        source1 = cds({
                          "Date": dates, "Open": open_p, "High": high,
                          "Low": low, "Close": close_p, "Volume": vol, "Adj": adj
                          })

        source2 = cds({
                          "Date": dates, "Open": open_p, "High": high,
                          "Low": low, "Close": close_p, "Volume": vol, "Adj": adj
                          })

        TOOLTIPS = [("Date", "@Date"), ("Open", "@Open"), ("High", "@High"),
                    ("Low", "@Low"), ("Close", "@Close"), ("Volume", "@Volume"), ("Adj Close*", "@Adj")]

        # Make the figure configuration
        f = figure(height = 270, x_axis_type = "datetime", tools = TOOLS, responsive = True)

        # Add title and label
        f.title = 'Historical Prices for ' + chart + " from 1.03.2010 until yesterday"
        f.xaxis.axis_label = 'Date'
        f.yaxis.axis_label = 'Open Prices'

        # make line and circle plots
        f.line(df.index, df.Open, source = source2, color = 'blue')
        # f.circle(df.index, df.Open, source = source1, color = 'navy', size = 0.5, alpha = 0.8)

        # other hover tool conf
        p_hover = f.select(HoverTool)
        p_hover.tooltips = TOOLTIPS

        return f

    # ======== MySQL ================================

    # === Make connection =============
    conn = MySQLdb.connect(host = host,
                           user = user,
                           passwd = passwd,
                           db = 'test')
    cur = conn.cursor()

    if request.method == "POST":
        fin = str(request.form.get('chart'))
        # cur, conn = mysql_connect('test')

        # MySQL command, for str don't forget the "" ( " %s " )
        # | finance is the db table, (search) is the column name |
        cur.execute( 'INSERT INTO finance (search) VALUES( "%s" )' %fin )
        conn.commit()
        print ( 'Connected!!!' )
        cur.close()
        conn.close()
        print ('connection closed')

    else:
        pass

    # ==== render template variables =============

    info = info()
    # pandas| make a html table
    info = info.to_html(classes='info_table')

    f = finance()

    # bokeh script and div for the chart
    script, div = components(f)

    return render_template('index.html', title = title, script = script, div = div, info = info)



if __name__ == '__main__':
    app.run()

# ===== Info ===================================
# if __name__ == '__main__':
#     print 'This program is being run by itself'
# else:
#     print 'I am being imported from another module'
# ==================================================