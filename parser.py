import pandas as pd
import re
from datetime import datetime

# Персер для отчётов формата SHR
def parse_normal_format(row:list) -> dict:
    format_time = lambda time_str: re.sub(r"(\d{2})(\d{2})",r"\1:\2",time_str)

    res = {}
    for col in row:
        if type(col) == str:
            col = col.replace("\n","")
            
            # Находим SHR сообщение
            if re.match(r".*?\((SHR|PLN)(.*?)\).*?",col):

                # Извлекаем необходимые данные из сообщения
                flight_id_ = re.search(r"(SHR|PLN)-(.*?)\W",col)
                uav_type_ = re.search(r"TYP\/(.*?)\W",col)
                departure_coords_ = re.search(r"DEP\/(\d+)N(\d+)E\W",col)
                arrival_coords_ = re.search(r"DEST\/(\d+)N(\d+)E\W",col)
                flight_date_ = re.search(r"DOF\/(.*?)\W",col)
                flight_region_ = re.search(r"-M\d{4}\/M\d{4}.*?\/(.*?)\/",col)

                res['flight_id'] = flight_id_.group(2) if flight_id_ != None else 'ZZZZZ'
                res["uav_type"] = uav_type_.group(1) if uav_type_ != None else 'ZZZZZ'
                res["departure_coords"] = departure_coords_.group(1,2) if departure_coords_ != None else ('ZZZZZ','ZZZZZ')
                res["arrival_coords"] = arrival_coords_.group(1,2) if arrival_coords_ != None else ('ZZZZZ','ZZZZZ')
                res["flight_date"] = re.sub(r"(\d{2})(\d{2})(\d{2})",r"20\1-\2-\3",flight_date_.group(1)) if flight_date_ != None else 'ZZZZZ'
                res["flight_region"] = flight_region_.group(1) if flight_region_ != None else 'ZZZZZ'
                
                time = re.findall(r"-[A-Z]{4}(\d{4})",col)

                if len(time) == 2:
                    res['start_time'] = format_time(time[0])
                    res['end_time'] = format_time(time[1])

                else:
                    res['start_time'] = 'ZZZZZ'
                    res['end_time'] = 'ZZZZZ'

    return res


# Парсер для отчётов других типов
def parse_other_format(row:list) -> dict:
    coords = []
    time = []
    other_data = []
    typ = 'ZZZZZ'
    zona = 'ZZZZZ'
    
    for col in row:
        if type(col) != int:
            col = str(col).replace("\n","")

            if re.match(r"M\d+.*?\/M\d+.*?\/(ZONA.*?)\/",col):
                zona = re.search(r"M\d+.*?\/M\d+.*?\/ZONA(.*?)\/",col).group(1)

            elif re.match(r".*?(BLA|AER|SHAR|BPLA).*?",col):
                typ = re.search(r".*?(BLA|AER|SHAR|BPLA).*?",col).group(1)
            
            elif re.match(r".*?(\d+)N(\d+)E.*?",col):
                coords.append(re.search(r"(\d+)N(\d+)E",col).group(1,2))

            elif re.match(r".*?\d{2}\:\d{2}.*?",col):
                time.append(col)

            elif re.match(r"(\d+)\/(\d+)\/(\d+)",col): # Костыль для другого формата времени
                if re.match(r"(\d{2})\/(\d{2})\/(\d{2})",col):
                    time.append(re.sub(r"(\d{2})\/(\d{2})\/(\d{2})",r"20\3-\2-\1 00:00:00",col))

                elif re.match(r"(\d{1})\/(\d{2})\/(\d{2})",col):
                    time.append(re.sub(r"(\d{1})\/(\d{2})\/(\d{2})",r"20\3-\2-0\1 00:00:00",col))

            elif re.match(r"([A-Z0-9]+)", col):
                other_data.append(re.search(r"([A-Z0-9]+)", col).group(1))

    res = {
        "flight_id":other_data[0] if len(other_data) != 0 else 'ZZZZZ',
        "uav_type":typ,
        'flight_region':zona
    }

    # Добавляем координаты взлёта/посадки

    if len(coords) == 4:
        res['departure_coords'] = coords[0]
        res['arrival_coords'] = coords[2]

    elif len(coords) == 2:
        res['departure_coords'] = coords[0]
        res['arrival_coords'] = coords[1]

    else:
        res['departure_coords'] = ('ZZZZZ','ZZZZZ')
        res['arrival_coords'] = ('ZZZZZ','ZZZZZ')
    
    # Добавляем дату полёта и время взлёта/посадки
    format_time = lambda time_str: re.search(r"(\d{2}\:\d{2})", time_str).group(1)
    
    # Если в строке нашёлся только один столбец с датой - то это дата полёта, т.к. она указывается первой
    if len(time) == 1:
        res['flight_date'] = re.search(r"(\d{4}\-\d{2}\-\d{2})", time[0]).group(1)

    if len(time) >=2:

        res['flight_date'] = re.search(r"(\d{4}\-\d{2}\-\d{2})", time[0]).group(1)

        # Если в строке чётное кол-во  столбцов с датами - то даты полёта нету, значит её можно взять из любого столбца
        if len(time) % 2 == 0:
            res['start_time'] = format_time(time[0])

            # Если столбцов со временем 2 - то это столбцы с временем взлёта и посадки
            if len(time) == 2:
                res['end_time'] = format_time(time[1])

            # Если столбцов с временем 4 - то берём 1 и 3, так как там время идёт в парах: (время, ориентировочное время)
            elif len(time) == 4:
                res['end_time'] = format_time(time[2])

        else:
            # если кол-во столбцов со временем - нечётное - то первый - это дата
            res['start_time'] = format_time(time[1])

            # Тут логика аналогична строкам 114 и 118
            if len(time) == 3:
                res['end_time'] = format_time(time[2])

            elif len(time) == 5:
                res['end_time'] = format_time(time[3])
    else:
        res['flight_date'] = 'ZZZZZ'
        res['start_time'] = 'ZZZZZ'
        res['end_time'] = 'ZZZZZ'

    return res

def parse_csv(file_path):
    data = []
    errors = []

    df = pd.read_csv(file_path, on_bad_lines="skip")

    for ind,row in df.iterrows():

        row = row.to_list()

        # Определяем, в каком формате хранится информация в строке
        normal_format = False

        for col in row:
            if (type(col) == str):
                if re.match(r".*?\((SHR|PLN)(.*?)\).*?",col.replace("\n","")):
                    normal_format = True

        try:
            # Парсим в зависимости от формата
            if normal_format:
                res = parse_normal_format(row)

            else:
                res = parse_other_format(row)

            data.append(res)
                
        except Exception as e:
            errors.append((ind, e))

    print(errors)
    print(f"Total data length: {len(data)}\nTotal errors: {len(errors)}")
    return (data, len(errors))