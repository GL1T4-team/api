import pandas as pd
import re

# Персер для отчётов формата SHR
def parse_normal_format(row:list) -> dict:
    format_time = lambda time_str: re.sub(r"(\d{2})(\d{2})",r"\1:\2",time_str)

    res = {}
    for col in row:
        if type(col) == str:
            col = col.replace("\n","")
            
            if re.match(r".*?\((SHR|PLN)(.*?)\).*?",col):
                flight_id_ = re.search(r"(SHR|PLN)-(.*?)\W",col)
                uav_type_ = re.search(r"TYP\/(.*?)\W",col)
                departure_coords_ = re.search(r"DEP\/(\d+)N(\d+)E\W",col)
                arrival_coords_ = re.search(r"DEST\/(\d+)N(\d+)E\W",col)
                flight_date_ = re.search(r"DOF\/(.*?)\W",col)
                flight_region_ = re.search(r"-M\d{4}\/M\d{4}.*?\/(.*?)\/",col)

                res['flight_id'] = flight_id_.group(2) if flight_id_ != None else 'ZZZZZ'
                res["uav_type"] = uav_type_.group(1) if uav_type_ != None else 'ZZZZZ'
                res["departure_coords"] = departure_coords_.group(1,2) if departure_coords_ != None else'ZZZZZ'
                res["arrival_coords"] = arrival_coords_.group(1,2) if arrival_coords_ != None else 'ZZZZZ'
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
        res['departure_coords'] = 'ZZZZZ'
        res['arrival_coords'] = 'ZZZZZ'
    
    # Добавляем дату полёта и время взлёта/посадки
    format_time = lambda time_str: re.search(r"(\d{2}\:\d{2})", time_str).group(1)

    if len(time) == 1:
        res['flight_date'] = re.search(r"(\d{4}\-\d{2}\-\d{2})", time[0]).group(1)

    if len(time) >=2:

        res['flight_date'] = re.search(r"(\d{4}\-\d{2}\-\d{2})", time[0]).group(1)
        if len(time) % 2 == 0:
            res['start_time'] = format_time(time[0])

            if len(time) == 2:
                res['end_time'] = format_time(time[1])

            elif len(time) == 4:
                res['end_time'] = format_time(time[2])

        else:
            res['start_time'] = format_time(time[1])

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

    df = pd.read_csv(file_path)

    for ind,row in df.iterrows():

        row = row.to_list()
        normal_format = False

        for col in row:
            if (type(col) == str):
                if re.match(r".*?\((SHR|PLN)(.*?)\).*?",col.replace("\n","")):
                    normal_format = True

        try:
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

# xls = pd.ExcelFile('2025.xlsx')

# data = []
# errors = []
# row = xls.parse(0).loc[17].to_list()#.fillna("ZZZZZ")

# print(row)
# print(parse_normal_format(row))

# sheets_num = len(xls.sheet_names)

# for sheet_ind in range(0,sheets_num-1):
#     for ind,row in xls.parse(sheet_ind).iterrows():

#         row = row.to_list()
        
#         normal_format = False

#         for col in row:
#             if (type(col) == str):
#                 if re.match(r".*?\((SHR|PLN)(.*?)\).*?",col.replace("\n","")):
#                     normal_format = True

#         try:
#             if normal_format:
#                 res = parse_normal_format(row)

#             else:
#                 res = parse_other_format(row)

#             data.append(res)

#             # print(f"Parsed: {sheet_ind+1} / {sheets_num}, {ind}")
                
#         except Exception as e:
#             errors.append((sheet_ind, ind, e))

# print(errors)
# print(f"Total data length: {len(data)}\nTotal errors: {len(errors)}")