import pymysql

# Сообщаем Django, что наша "подделка" — это нужная, новая версия драйвера
pymysql.version_info = (2, 2, 8, "final", 0)
pymysql.install_as_MySQLdb()