import datetime, os, sys, math, Quandl
from PyQt5.QtWidgets import (QApplication, QAction, QCalendarWidget, QComboBox,
     QDockWidget, QInputDialog, QFileDialog, QGridLayout, QHBoxLayout, QLineEdit,
     QMainWindow, QMessageBox, QPushButton, QScrollArea, QInputDialog,
     QLabel, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import plotly
from plotly.graph_objs import Scatter, Layout

class Portfolio():
    class Stock:
        name = str()
        amount = float()
        price = float()
        prices = list()
        revenues = list()

        def __init__(self, setName, _amount, _price):
            self.name = setName
            self.amount = _amount
            self.price = _price
            self.revenues = list()
            self.prices = list()

    def cutNewLine(self, line):
        return line[0:len(line) - 1]

    def __init__(self, path):
        # Initialize main portfolio components
        self.path = path
        self.data = list()
        self.var = None
        self.stocks = list()

        #Adding stocks to self.stocks
        optionsFile = open(path + "options.txt", "r")
        next(optionsFile)
        for line in optionsFile:
            if len(line) > 2:
                asset_name = line[0:len(line) - 1]
                stockFile = open(path + asset_name + ".txt", "r")
                asset_info = stockFile.readline()
                asset_info = asset_info.split(" ")

                self.stocks.append(self.Stock(asset_name, float(asset_info[0]), float(asset_info[1])))

    def getName(self):
        f = open(self.path + "options.txt")
        name = f.readline()

        return name[0:len(name) - 1]

    def downloadOnlineData(self, period):
        #download enough history and add it to a stock file
        for stock in self.stocks:
            temp_data = Quandl.get("GOOG/" + stock.name, authtoken="iXqyWcLmzbBxo3h-Hh8M",
                                   rows=(534))["Close"]
            temp_data = temp_data.iloc[::-1]
            temp_data.to_csv(self.path + stock.name + ".txt", sep=" ", mode="a")

    def download_csv_data(self, path, ticker, amount):
        # upload data from the file to the programm
        readf = open(path, "r")
        data = list()
        for line in readf:
            line = line.split(",")
            date = line[2]
            date = date[0:4] + "-" + date[4:6] + "-" + date[6:8]
            data.append(date + " " + line[4] + "\n")
        readf.close()

        # create the stock info file
        writef = open(self.path + ticker + ".txt", "w")
        info_line = str(self.cutNewLine(data[len(data) - 1]))
        asset_price = info_line.split(" ")[1]
        writef.write(str(amount) + " " + asset_price)
        i = len(data) - 1
        while (i >= 0):
            writef.write(data[i])
            i = i - 1
        writef.close()

        # write ticker name in the options file
        optionf = open(self.path + "options.txt", "a")
        optionf.write(ticker + "\n")

        # add stock to stock list
        self.stocks.append(self.Stock(ticker, amount, float(asset_price)))

    def calculateVar(self, period, confidence):
        #upload data into program
        for stock in self.stocks:
            stock.prices = list()
            stock.revenues = list()
            f = open(self.path + stock.name + ".txt", "r")
            next(f)
            i = 0
            for line in f:
                line = self.cutNewLine(line)
                price = float(line.split(" ")[1])
                stock.prices.append(price)
                if (i >= period):
                    stock.revenues.append((stock.prices[i - period] - stock.prices[i])
                                          / stock.prices[i])
                i = i + 1

        #calculate weight revenues
        min_len = len(self.stocks[0].revenues)
        for stock in self.stocks:
            min_len = min(min_len, len(stock.revenues))

        revenues = list()
        totalPrice = self.getPortfolioPrice()
        mean = float(0)
        for i in range(min_len):
            add = float(0)
            for stock in self.stocks:
                add = add + (stock.price * stock.amount / totalPrice) * stock.revenues[i]
            mean = mean + add
            revenues.append(add)
        mean = mean / len(revenues)

        #calculate standart deviation
        sd = float(0)
        for revenue in revenues:
            sd = sd + (revenue - mean) * (revenue - mean)
        sd = sd / (len(revenues) - 1)
        sd = math.sqrt(sd)

        #calculate z-score
        if (confidence == 0.99):
            zscocre = 2.58
        elif (confidence == 0.975):
            zscocre = 2.25
        elif (confidence == 0.95):
            zscocre = 1.96
        else:
            zscocre = 1.65

        self.var = totalPrice * sd * zscocre
        ret = list()
        ret.append(round(self.var, 2))
        ret.append(round(self.var / totalPrice, 2))

        return ret

    def backtest(self, period, confidence):
        var = self.calculateVar(period, confidence)[1]
        #py.sign_in("Kredshow", "yk6njdcs8m")
        mainY = list()
        varY = list()
        last = float(0)
        for i in range(504):
            add = float(0)
            for stock in self.stocks:
                add = add + stock.prices[i] * stock.amount
            if (i == 0):
                varY.append(add * (1 - var))
            else:
                varY.append(last * (1 - var))
            last = add
            mainY.append(add)

        mainX = [i for i in range(504)]
        mainY = mainY
        plotly.offline.plot({
            "data": [
                Scatter(x=mainX, y=mainY),
                Scatter(x=mainX, y=varY)
            ],
            "layout": Layout(
                title="Backtest"
            )
        })

    def add_online_ticker(self, exchange, ticker, amount):
        try:
            data = Quandl.get("GOOG/" + exchange + "_" + ticker, authtoken="iXqyWcLmzbBxo3h-Hh8M",
                              rows = 1)["Close"]

            #writing ticker name in options
            f = open(self.path + "options.txt", "a")
            f.write(exchange + "_" + ticker + "\n")

            #creating ticker history file
            f = open(self.path + exchange + "_" + ticker + ".txt", "w")
            asset_price = data[0]
            f.write(str(amount) + " " + str(amount * asset_price) + "\n")

            #adding stock to stocks list
            self.stocks.append(self.Stock(exchange + "_" + ticker, amount, asset_price))

            return 0
        except Quandl.DatasetNotFound:
            return 1

    def getPortfolioPrice(self):
        ans = float(0)
        for stock in self.stocks:
            ans = ans + (stock.price * stock.amount)

        return ans

    def get_stocks_infos(self):
        ans = list()
        totalPrice = self.getPortfolioPrice()
        for stock in self.stocks:
            ans.append(stock.name + ": " +
                       str(round(stock.amount * stock.price / totalPrice * 100, 2)) + "%")

        return ans

class BacktestMode(QWidget):
    def __init__(self, var, stock_infos, period, confidence):
        super().__init__()
        self.var = var
        self.stock_infos = stock_infos
        self.initUI()
        self.period = period
        self.confidence = confidence

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)

        mainLayout.addWidget(QLabel("Set backtest period:"))

        setDateBox = QHBoxLayout()

        now = datetime.datetime.now()
        minimumDate = QLineEdit(str(now.date()))
        maximumDate = QLineEdit(str(now.date()))
        backtestButton = QPushButton("Backtest")
        backtestButton.clicked.connect(lambda: self.backtest(minimumDate.text(),
                                    maximumDate.text()))

        self.pentrationsActual = QLabel("Actual pentrations:-")
        self.pentrationsEstimated = QLabel("Estimated pentrations:-")

        setDateBox.addWidget(minimumDate)
        setDateBox.addWidget(maximumDate)
        setDateBox.addWidget(backtestButton)

        mainLayout.addLayout(setDateBox)
        mainLayout.addWidget(self.pentrationsActual)
        mainLayout.addWidget(self.pentrationsEstimated)
        self.setLayout(mainLayout)

        self.setGeometry(400, 200, 300, 200)
        self.setWindowTitle('Menubar')
        self.show()

    def backtest(self, minimumDate, maximumDate):
        prices = list()
        for info in self.stock_infos:
            data = Quandl.get("GOOG/" + info[0], authtoken="iXqyWcLmzbBxo3h-Hh8M",
                              trim_start=minimumDate, trim_end=maximumDate)["Close"]

            add = list()
            for i in range(len(data)):
                if (i % self.period == 0):
                    add.append(data[i])

            prices.append(add)

        minLen = len(prices[0])
        for price in prices:
            minLen = min(minLen, len(price))

        mainX = [i for i in range(minLen)]
        mainY = list()
        for i in range(minLen):
            add = float(0)
            for j in range(len(prices)):
                add = add + prices[j][i] * self.stock_infos[j][1]
            mainY.append(add)

        varY = list()
        varY.append(mainY[0] * (1 - self.var))
        for i in range(minLen - 1):
            varY.append(mainY[i] * (1 - self.var))

        deltaY = list()
        pentrations = int(0)
        for i in range(len(varY)):
            deltaY.append(mainY[i] - varY[i])
            if (deltaY[i] < 0):
                pentrations = pentrations + 1

        self.pentrationsActual.setText("Actual pentrations: " + str(pentrations))
        self.pentrationsEstimated.setText("Estimated pentrations: " +
                                          str(int(round((1 - self.confidence) * len(mainX), 0))))

        plotly.offline.plot({
            "data": [
                Scatter(x=mainX, y=mainY, name="Historical price"),
                Scatter(x=mainX, y=varY, name="VaR"),
                Scatter(x=mainX, y=deltaY, name="Delta"),
            ],
            "layout": Layout(
                title="Backtest"
            )
        })

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.openPortfolio)

        create_action = QAction("&Create", self)
        create_action.triggered.connect(self.createPortfolio)

        options_action = QAction("Options", self)

        self.statusBar()

        menubar = self.menuBar()
        option_menu = menubar.addMenu("Options")
        option_menu.addAction(open_action)
        option_menu.addAction(create_action)
        option_menu.addAction(options_action)

        self.setGeometry(300, 100, 450, 700)
        self.setWindowTitle('Menubar')
        self.show()

    def createPortfolio(self):
        name, ok = QInputDialog.getText(self, "Input dialog", "Enter new portfolio name")

        if ok:
            f = open("Properities", "r")
            path = f.readline()
            path = path[0:len(path) - 1]

            #Creating a portfolio folder starts here
            os.mkdir(path + name)
            f = open(path + name + "/" + "options.txt", "w")
            f.write(name + "\n")
            f.close()
            self.initCentralWidget(path + name + "/")

    def openPortfolio(self):
        path = QFileDialog.getExistingDirectory(self, "Choose portfolio folder", "/home")

        if len(path) > 0:
            self.initCentralWidget(path + "/")

    def initCentralWidget(self, path):
        self.portfolio = Portfolio(path)

        self.main_vboxLayout = QVBoxLayout()
        self.main_vboxLayout.setAlignment(Qt.AlignTop)

        self.create_topbox()

        self.create_toolbox()

        self.create_goog_box()

        self.create_csv_box()

        self.create_info_widget()

        mainWidget = QWidget(self)
        mainWidget.setLayout(self.main_vboxLayout)
        self.setCentralWidget(mainWidget)

    def create_topbox(self):
        name_font = QFont()
        name_font.setPointSize(20)
        name_label = QLabel(self.portfolio.getName())
        name_label.setFont(name_font)

        top_box_layout = QHBoxLayout()
        top_box_layout.addWidget(name_label)

        self.main_vboxLayout.addWidget(name_label)

    def create_toolbox(self):
        self.confidenceBox = QComboBox(self)
        self.confidenceBox.addItems(["99%", "97.5", "95%", "90%"])

        self.horizontBox = QComboBox(self)
        self.horizontBox.addItems(["1 day", "7 days", "15 days", "30 days"])

        var_button = QPushButton("Calculate VaR")
        var_button.clicked.connect(lambda: self.calculate_var(self.horizontBox.currentText(),
                                           self.confidenceBox.currentText()))

        backtest_button = QPushButton("Backtest mode")
        backtest_button.clicked.connect(lambda: self.backtest_var(self.horizontBox.currentText(),
                        self.confidenceBox.currentText()))

        toolbox = QGridLayout()
        toolbox.addWidget(QLabel("Horizont"), 0, 0)
        toolbox.addWidget(QLabel("Confidence"), 0, 1)
        toolbox.addWidget(self.horizontBox, 1, 0)
        toolbox.addWidget(self.confidenceBox, 1, 1)
        toolbox.addWidget(var_button, 1, 2)
        toolbox.addWidget(backtest_button, 2, 2)

        self.main_vboxLayout.addLayout(toolbox)

    def create_goog_box(self):
        title_label = QLabel("Download history from google finance:")
        exchange_label = QLabel("Exchange:")
        ticker_label = QLabel("Ticker:")
        amount_label = QLabel("Amount:")

        exchange_input = QLineEdit()
        ticker_input = QLineEdit()
        amount_input = QLineEdit()

        add_asset_button = QPushButton("Add asset")
        add_asset_button.clicked.connect(lambda: self.add_goog_ticker(exchange_input.text(),
                                                                        ticker_input.text(), amount_input.text()))

        download_history_button = QPushButton("Download history")
        download_history_button.clicked.connect(self.download_history)

        goog_box = QVBoxLayout()
        goog_box.addWidget(title_label)

        goog_grid = QGridLayout()
        goog_grid.addWidget(exchange_label, 1, 0)
        goog_grid.addWidget(exchange_input, 1, 1)
        goog_grid.addWidget(ticker_label, 1, 2)
        goog_grid.addWidget(ticker_input, 1, 3)
        goog_grid.addWidget(amount_label, 2, 0)
        goog_grid.addWidget(amount_input, 2, 1)
        goog_grid.addWidget(download_history_button, 3, 3)
        goog_grid.addWidget(add_asset_button, 2, 3)

        goog_box.addLayout(goog_grid)

        self.main_vboxLayout.addLayout(goog_box)

    def create_csv_box(self):
        title_label = QLabel("Download history from csv file:")
        path_label = QLabel("Path:")
        ticker_label = QLabel("Ticker:")
        amount_label = QLabel("Amount:")

        self.path_line = QLineEdit()
        ticker_line = QLineEdit()
        amount_line = QLineEdit()

        browse_file_button = QPushButton("Browse file")
        browse_file_button.clicked.connect(self.get_file_path)
        download_button = QPushButton("Download")
        download_button.clicked.connect(lambda: self.download_csv_file(ticker_line.text(),
                                        amount_line.text()))

        csv_box = QVBoxLayout()
        csv_box.addWidget(title_label)

        browse_file_box = QHBoxLayout()
        browse_file_box.addWidget(path_label)
        browse_file_box.addWidget(self.path_line)
        browse_file_box.addWidget(browse_file_button)

        setup_box = QHBoxLayout()
        setup_box.addWidget(ticker_label)
        setup_box.addWidget(ticker_line)
        setup_box.addWidget(amount_label)
        setup_box.addWidget(amount_line)
        setup_box.addWidget(download_button)

        csv_box.addLayout(browse_file_box)
        csv_box.addLayout(setup_box)

        self.main_vboxLayout.addLayout(csv_box)

    def create_info_widget(self): #not implemented
        self.infoLayout = QVBoxLayout()

        self.priceLabel = QLabel("Portfolio price: " + str(self.portfolio.getPortfolioPrice()))
        self.infoLayout.addWidget(self.priceLabel)
        self.portfolio_assets_grid = QGridLayout()
        self.infoLayout.addLayout(self.portfolio_assets_grid)

        self.main_vboxLayout.addLayout(self.infoLayout)
        self.update_info_box()

    def update_info_box(self):
        self.priceLabel.setText("Portfolio price: " + str(self.portfolio.getPortfolioPrice()))

        for i in reversed(range(self.portfolio_assets_grid.count())):
            self.portfolio_assets_grid.itemAt(i).widget().setParent(None)

        stocksInfos = self.portfolio.get_stocks_infos()
        i = int(0)
        j = int(0)
        for stockInfo in stocksInfos:
            self.portfolio_assets_grid.addWidget(QLabel(stockInfo), i, j)
            j = j + 1
            if j == 2:
                i = i + 1
                j = 0

    def add_goog_ticker(self, exchange, ticker, amount):
        exchange = exchange.upper()
        ticker = ticker.upper()
        amount = float(amount)

        self.statusBar().showMessage("Trying to find " + exchange + " " + ticker)
        code = self.portfolio.add_online_ticker(exchange, ticker, amount)
        if code == 0:
            self.statusBar().showMessage("Ticker added", 2000)
        elif code == 1:
            self.statusBar().showMessage("Ticker not found", 2000)

        self.update_info_box()

    def get_file_path(self):
        path = QFileDialog.getOpenFileName(self, "Get CSV file", "/home")[0]
        self.path_line.setText(path)

    def download_csv_file(self, ticker, amount):
        self.statusBar().showMessage("Downloading file")
        self.portfolio.download_csv_data(self.path_line.text(), ticker.upper(), float(amount))
        self.update_info_box()
        self.statusBar().showMessage("Downloading finished", 2000)

    def download_history(self):
        period = self.horizontBox.currentText()
        if (period == "1 day"):
            period = 1
        elif (period == "7 days"):
            period = 7
        elif (period == "15 days"):
            period = 15
        else:
            period = 30

        self.statusBar().showMessage("Download starting", 2000)
        self.portfolio.downloadOnlineData(period)
        self.statusBar().showMessage("Download finished", 2000)

    def convert_conf_period(self, period, confidence):
        if (period == "1 day"):
            period = 1
        elif (period == "7 days"):
            period = 7
        elif (period == "15 days"):
            period = 15
        else:
            period = 30

        if (confidence == "99%"):
            confidence = 0.99
        elif (confidence == "97.5%"):
            confidence = 0.975
        elif (confidence == "95%"):
            confidence = 0.95
        else:
            confidence = 0.9

        return [period, confidence]

    def calculate_var(self, period, confidence):
        converted_data = self.convert_conf_period(period, confidence)

        self.statusBar().showMessage("The calculation started", 2000)
        var = self.portfolio.calculateVar(converted_data[0], converted_data[1])
        self.statusBar().showMessage("The calculation finished", 2000)

        QMessageBox.about(self, 'Result of calculation',
            "Var is: " + str(var[0]) + " or " + str(round(var[1] * 100, 1)) + "%")

    def backtest_var(self, period, confidence):
        arguments = self.convert_conf_period(period, confidence)
        var = self.portfolio.calculateVar(arguments[0], arguments[1])[1]

        #get stock names and amounts
        stock_infos = list()
        for stock in self.portfolio.stocks:
            stock_infos.append([stock.name, stock.amount])

        self.backtesWidget = BacktestMode(var, stock_infos, arguments[0], arguments[1])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
