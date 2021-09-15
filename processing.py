def RSICalculation(input_data, rsi_qty):

    import yfinance as yf, pandas as pd, shutil, os, time, glob
    from IPython.display import HTML
    import requests

    # Stocks to be traded
    tickers = sorted(input_data.split())
    print("this is input data")
    print(input_data)
    print(len(tickers))


    #user = os.path.expanduser('~')

    # Removes and recreates StockData folder
    #shutil.rmtree(user + r"\First\.vscode\MomBday\StockData")
    #os.mkdir(user + r"\First\.vscode\MomBday\StockData")
    # Same as above but for StockDataRSI folder
    #shutil.rmtree(user + r"\First\.vscode\MomBday\StockDataRSI")
    #os.mkdir(user + r"\First\.vscode\MomBday\StockDataRSI")

    shutil.rmtree("/home/dustybroom/mysite/StockData")
    os.mkdir("/home/dustybroom/mysite/StockData")

    # Make less than 2,000 calls per hour or 48,000 calls per day
    Stock_Failure = 0
    Stocks_Not_Imported = 0
    Amount_of_API_Calls = 0
    i=0


    while (i < len(tickers)) and (Amount_of_API_Calls < 1800):
        try:
            stock = tickers[i]  # Gets the current stock ticker
            print(stock)
            temp = yf.Ticker(str(stock))
            Hist_data = temp.history(period="max")  # Finds the historical data
            Hist_data.to_csv("/home/dustybroom/mysite/StockData/" + stock + ".csv")  # Saves the historical data in csv format for further processing later
            #time.sleep(1)  # Pauses the loop for two seconds so we don't cause issues with Yahoo Finance's backend operations
            Amount_of_API_Calls += 1
            Stock_Failure = 0
            i += 1  # Goes to the next ticker
        except ValueError:
            print("Yahoo Finance Backend Error, Attempting to Fix")  # Yahoo Finance's backend did smth wrong so we're gonna try 5 more times
            if Stock_Failure > 5:  # Will move on after 5 tries
                i+=1
                Stocks_Not_Imported += 1
            Amount_of_API_Calls += 1
            Stock_Failure += 1
        # If there's a SSL error
        except requests.exceptions.SSLError as e:
            print("Yahoo Finance Backend Error, Attempting to Fix SSL")  # Yahoo Finance's backend did smth wrong so we're gonna try 5 more times
            if Stock_Failure > 5:  # Will move on after 5 tries
                i+=1
                Stocks_Not_Imported += 1
            Amount_of_API_Calls += 1
            Stock_Failure += 1



    # Get the path for each stock file in a list
    list_files = (glob.glob("/home/dustybroom/mysite/StockData/*.csv"))

    masterRSI = []


    # While loop to cycle through the stock paths
    for stock in list_files:
        # Dataframe to hold the historical data of the stock we are interested in.
        Hist_data = pd.read_csv(stock)
        # This list holds the closing prices of a stock
        prices = []
        c = 0
        # Add the closing prices to the prices list and make sure we start at greater than 2 dollars to reduce outlier calculations.
        while c < len(Hist_data):
            if Hist_data.iloc[c,4] > float(2.00):  # Check that the closing price for this day is greater than $2.00
                prices.append(Hist_data.iloc[c,4])
            c += 1
        i = 0
        upPrices=[]
        downPrices=[]
        #  Loop to hold up and down price movements
        while i < len(prices):
            if i == 0:
                upPrices.append(0)
                downPrices.append(0)
            else:
                if (prices[i]-prices[i-1])>0:
                    upPrices.append(prices[i]-prices[i-1])
                    downPrices.append(0)
                else:
                    downPrices.append(prices[i]-prices[i-1])
                    upPrices.append(0)
            i += 1
        x = 0
        avg_gain = []
        avg_loss = []
        #  Loop to calculate the average gain and loss
        while x < len(upPrices):
            if x <15:
                avg_gain.append(0)
                avg_loss.append(0)
            else:
                sumGain = 0
                sumLoss = 0
                y = x-14
                while y<=x:
                    sumGain += upPrices[y]
                    sumLoss += downPrices[y]
                    y += 1
                avg_gain.append(sumGain/14)
                avg_loss.append(abs(sumLoss/14))
            x += 1
        p = 0
        RS = []
        RSI = []
        #  Loop to calculate RSI and RS
        while p < len(prices):
            if p <15:
                RS.append(0)
                RSI.append(0)
            else:
                if avg_loss[p] == 0:
                    RS.append(-1)
                    RSI.append(100)
                else:
                    RSvalue = (avg_gain[p]/avg_loss[p])
                    RS.append(RSvalue)
                    RSI.append(100 - (100/(1+RSvalue)))
            p+=1


        rsi_qty = int(rsi_qty)

        # Creates a list of all stock RSIs from the past x days
        recentRSI = RSI[-rsi_qty:]
        for i in range(len(recentRSI)):
            masterRSI.append(round(recentRSI[i]))




    Output = pd.DataFrame(columns=["Ticker"])

    for i in range(rsi_qty):
        Output['RSI_' + str(i+1)] = ""

    for i in range(len(tickers)):
        add_output_row = {'Ticker' : tickers[i]}

        RSIcounter = i * rsi_qty

        for x in range(rsi_qty):

            add_output_row['RSI_' + str(x+1)] = masterRSI[RSIcounter + x]


        Output = Output.append(add_output_row, ignore_index = True)

    outputHTML = Output.to_html()

    outputCSV = Output.to_csv("Output.csv", index=False)

    return(HTML(Output.to_html(classes='table table-striped')))
