### Что это за проект? ###

Разработана программа, которая, по портфелю заданных активов (Акции) рассчитывает показатель VaR, который является стоимостной мерой рыночного риска заданного портфеля. То есть этот продукт может сказать, что завтра, через неделю или через месяц ваши убытки на заданном наборе акций с вероятностью 99% не превысят какое-то n-ое количество процентов. 
  
Продукт удовлетворяет следующим свойствам:

* Программа, осуществляющая расчет показателя VaR параметрическим методом
* Программа может загружать историю цен активов из базы данных Google Finance или из CSV файла
* Реализован режим бэктестинга VaR с построением графика бэктестинга (То есть можно удостовериться в корректности прогноза на исторических данных)
* Программа работает исключительно с акциями 
* Подразумевается, что стоимость активов указана в одинаковой валюте

Разработанный продукт не подразумевает:

* Анализ инструментов, отличных от акций
* Загрузки данных в форматах аналогов CSV

Скриншоты:

![Screenshot1.jpg](https://bitbucket.org/repo/y4MdB5/images/1219848839-Screenshot1.jpg) ![Screenshot3.jpg](https://bitbucket.org/repo/y4MdB5/images/1904024774-Screenshot3.jpg) ![Screenshot4.jpg](https://bitbucket.org/repo/y4MdB5/images/2196002644-Screenshot4.jpg)

![Screenshot2.jpg](https://bitbucket.org/repo/y4MdB5/images/3563456305-Screenshot2.jpg)

### Как мне заставить код работать? ###

1. Прежде всего у вас должен быть установлен [Python 3.4](https://www.python.org/download/releases/3.4.0/)
2. Далее нужно установить следующие внешние библиотеки [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/installation.html), [Quandl API](https://www.quandl.com/tools/python) [Plotly](https://plot.ly/python/)
3. Запустить код :D

### Как пользоваться программой? ###

**1)** Запускаете код и перед вами всплывает окно

![main_window1.jpg](https://bitbucket.org/repo/y4MdB5/images/422788474-main_window1.jpg)

**2)** Нажимаете на вкладу **Options** в левом верхнем углу. Затем в открывшемся меню выбираете **Create** и в появившемся окне введите имя портфеля активов, нажмите **OK**. 

![main_window2.jpg](https://bitbucket.org/repo/y4MdB5/images/333233929-main_window2.jpg) ![main_window3.jpg](https://bitbucket.org/repo/y4MdB5/images/3863022154-main_window3.jpg)

**3)** Открылось рабочее окно. 

![Info.jpg](https://bitbucket.org/repo/y4MdB5/images/3195349906-Info.jpg)

**4)** Добавим акции в наш портфель. На пример, я куплю на NASDAQ 1 акцию Google и 8 акций Apple. Сперва добавлю их в портфель, а потом скачаю историю.

![work_window2.jpg](https://bitbucket.org/repo/y4MdB5/images/3056745078-work_window2.jpg) ![work_window3.jpg](https://bitbucket.org/repo/y4MdB5/images/3727828741-work_window3.jpg)![work_window4.jpg](https://bitbucket.org/repo/y4MdB5/images/2230831493-work_window4.jpg)
