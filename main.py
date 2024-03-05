import pandas as pd
import pytz
from datetime import datetime, timedelta

BatV = "BatV"
Bat_status = "Bat_status"
Ext_sensor = "Ext_sensor"
Hum_SHT = "Hum_SHT"
TempC_DS = "TempC_DS"
TempC_SHT = "TempC_SHT"
inputFileName = "20240305.txt"
outputFileName = "output.csv"
inputFileDirectory = "C:\\Users\\Mateus\\Documents\\GitHub\\MQTT_TTN_Python\\"
outputDirectory = "C:\\Users\\Mateus\\Documents\\GitHub\\MQTT_TTN_Python_SQLite\\output\\"

def defineInputFileDirectory():
    return inputFileDirectory + inputFileName

def readInputFile(inputFileDirectory):
    result = {
        "decodedValue": [],
        "rawDateTime": [],
    }

    with open(inputFileDirectory, 'r') as file:
        data = file.read().replace('\n', '')

        # Iterar sobre os índices e seus caracteres usando enumerate
        for i, char in enumerate(data):
            # Verificar se a data está no formato correto começando com "20" e terminando com "Z"
            if data[i:i+2] == "20" and data[i+29] == "Z":
                result["rawDateTime"].append(data[i:i+23])

            if char == "{":
                start = i
            elif char == "}":
                end = i
                result["decodedValue"].append(data[start+1:end])

    return result["decodedValue"], result["rawDateTime"]

def extractPayloadData(dataCollect):
    sensor_mappings = {
        "BatV": [],
        "Bat_status": [],
        "Ext_sensor": [],
        "Hum_SHT": [],
        "TempC_DS": [],
        "TempC_SHT": []
    }

    for data in dataCollect:
        # Remover aspas simples e dividir os dados
        data = data.replace("'", "").split(',')

        for item in data:
            # Dividir chave e valor
            key, value = item.strip().split(':')

            # Adicionar valor à lista correspondente
            if key == "BatV":
                sensor_mappings["BatV"].append(value)
            elif key == "Bat_status":
                sensor_mappings["Bat_status"].append(value)
            elif key == "Ext_sensor":
                sensor_mappings["Ext_sensor"].append(value)
            elif key == "Hum_SHT":
                sensor_mappings["Hum_SHT"].append(value)
            elif key == "TempC_DS":
                sensor_mappings["TempC_DS"].append(value)
            elif key == "TempC_SHT":
                sensor_mappings["TempC_SHT"].append(value)
    
    return (
        sensor_mappings["BatV"],
        sensor_mappings["Bat_status"],
        sensor_mappings["Ext_sensor"],
        sensor_mappings["Hum_SHT"],
        sensor_mappings["TempC_DS"],
        sensor_mappings["TempC_SHT"]
    )

def formatTime(rawDateTime):
    formatedTime = []
    timezone = pytz.timezone('America/Sao_Paulo')

    for i in range(len(rawDateTime)):
        extractedDate = datetime.strptime(rawDateTime[i], "%Y-%m-%dT%H:%M:%S.%f")
        
        # Ajustar a data e hora para o fuso horário de São Paulo (GMT-3)
        localizedDate = timezone.localize(extractedDate)
        localizedDate -= timedelta(hours=3)
        formatedTime.append(localizedDate.strftime("%H:%M:%S"))
    return formatedTime

def createDataFrame(formatedTime, batV, batStatus, extSensor, humidity_SHT, tempC_DS, tempC_SHT):
    data = {
        "DateTime": formatedTime,
        "BatV": batV,
        "BatStatus": batStatus,
        "ExtSensor": extSensor,
        "Humidity_SHT": humidity_SHT,
        "TemperatureC_DS": tempC_DS,
        "TemperatureC_SHT": tempC_SHT
    }
    return pd.DataFrame(data)

def writeCsvFile(dataFrame):
    dataFrame.to_csv(outputDirectory + outputFileName, index = True)

def setup():
    inputFileDirectory = defineInputFileDirectory()
    decodedValue, readTime = readInputFile(inputFileDirectory)
    formattedDateTime = formatTime(readTime)
    batV, batStatus, extSensor, humidity_SHT, temperatureC_DS, temperatureC_SHT = extractPayloadData(decodedValue)

    # Criar um DataFrame com os dados processados
    dataFrame = createDataFrame(formattedDateTime, batV, batStatus, extSensor, humidity_SHT, temperatureC_DS, temperatureC_SHT)

    # Converter os dados para números
    dataFrame['TemperatureC_DS'] = pd.to_numeric(dataFrame['TemperatureC_DS'])
    dataFrame['TemperatureC_SHT'] = pd.to_numeric(dataFrame['TemperatureC_SHT'])
    dataFrame['Humidity_SHT'] = pd.to_numeric(dataFrame['Humidity_SHT'])

    writeCsvFile(dataFrame)

def main():
    setup()

if __name__ == "__main__":
    main()
