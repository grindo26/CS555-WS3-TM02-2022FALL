# if level 0 then check for tags, otherwise simply split
from cmath import rect
from unittest import result
from prettytable import PrettyTable
from datetime import datetime
from pymongo import MongoClient
import EstabilishDBConn

inpFileName = "M3_B2_InputGED.ged"

g_ResultString = ""
m_indiTable = PrettyTable()
m_famTable = PrettyTable()
m_indiTable.field_names = ["ID", "Name",
                           "SEX", "BIRTHDATE", "DEATHDATE", "CHILDREN", "SPOUSE"]
m_famTable.field_names = ["ID", "CHILDREN", "Husband ID", "Wife ID"]
m_dictIndi = []
m_dictFam = []
# 0 level Indi Id
# 1 level NAME
# 0 level FAM Id
# 1 level FAM connections
arrIds = []
idKey = "_id"


def initKeys():
    Keys = {
        "NAME": "NAME",
        "SEX": "SEX",
        "BIRT": "BIRTH",
        "DATE": "DATE",
        "DEAT": "DEATH",
        "DIV": "DIVORCE",
        "MARR": "MARRIAGE",
        "HUSB": "HUSBAND",
        "WIFE": "WIFE",
        "CHIL": "CHILDREN"
    }
    return Keys


def isIDUnique(id, list_id):
    if id not in list_id:
        return True
    else:
        return False


def extractInfoZeroLevel(p_arrLine):
    l_lvl = p_arrLine[0]
    if checkIfValidTag(p_arrLine[1]) == "Y":
        l_Tag = p_arrLine[1]
        l_valid = "Y"
        l_args = p_arrLine[2] if 2 < len(p_arrLine) else ""
    elif checkIfValidTag(p_arrLine[2]) == "Y":
        l_Tag = p_arrLine[2]
        l_valid = "Y"
        l_args = p_arrLine[1] if 1 < len(p_arrLine) else ""
    else:
        l_Tag = p_arrLine[1]
        l_valid = "N"
        l_args = p_arrLine[2] if 2 < len(p_arrLine) else ""
    return l_lvl, l_Tag, l_valid, l_args


def checkIfValidTag(p_strTag):
    l_listValidTags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS",
                       "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]
    l_strValid = "N"
    if p_strTag in l_listValidTags:
        l_strValid = "Y"
    return l_strValid


def extractNameFromLine(p_strLine):
    l_arrTxt = p_strLine.split(" ", 2)
    if l_arrTxt[1] == "NAME":
        return l_arrTxt[2]
    return ""


def extractSpouseIDFromLine(p_strLine):
    l_arrTxt = p_strLine.split(" ", 2)
    if l_arrTxt[1] == "HUSB":
        return "HUSB", l_arrTxt[2]
    if l_arrTxt[1] == "WIFE":
        return "WIFE", l_arrTxt[2]
    return "", ""

# Swaraj's portion


def validateMarriageGender(m_dictIndi, m_dictFam, path=0):
    wrong = []
    if path == 0:
        for i in m_dictFam:
            maleID = m_dictFam[i]['Husb']
            femaleID = m_dictFam[i]['Wife']

            if m_dictIndi[maleID]['sex'] != 'M':
                wrong.append(maleID+"with wrong sex:" +
                             m_dictIndi[femaleID]['sex']+" is married to "+femaleID)
            elif m_dictIndi[femaleID]['sex'] != 'F':
                wrong.append(femaleID+"with wrong sex:" +
                             m_dictIndi[femaleID]['sex']+" is married to "+maleID)
    else:
        f = open(path, "r")
        lines = f.read().split('\n')
        size = len(lines)
        for j in range(0, size):
            wordList = lines[j].split()
            if (len(wordList)) == 3 and wordList[0] == '0':
                if wordList[2] == 'FAM' or wordList[1] == 'FAM':
                    if lines[j+1].split()[1] != 'HUSB' and lines[j+2].split()[1] != 'WIFE':
                        continue
                    if lines[j+1].split()[1] == 'HUSB':
                        nextLineList = lines[j+1].split()
                        husbID = nextLineList[2]

                    if lines[j+2].split()[1] == 'WIFE':
                        nextLineList = lines[j+2].split()
                        wifeID = nextLineList[2]

                    k = 0
                    while (k < size):
                        lst3 = lines[k].split()
                        if (len(lst3) >= 2):
                            if lst3[0] == '0' and lst3[1] == husbID:
                                k += 1
                                while (k < size):
                                    lst3 = lines[k].split()
                                    if lst3[1] == 'SEX' and lst3[2] != 'M':
                                        wrong.append(
                                            husbID+" with wrong sex:"+lst3[2]+" is married to "+wifeID)
                                        break
                                    if lst3[0] == '0':
                                        break
                                    k += 1

                        lst3 = lines[k].split()
                        if (len(lst3) >= 2):
                            if lst3[0] == '0' and lst3[1] == wifeID:
                                k += 1
                                while (k < size):
                                    lst3 = lines[k].split()
                                    if lst3[1] == 'SEX' and lst3[2] != 'F':
                                        wrong.append(
                                            wifeID+"with wrong sex:"+lst3[2]+" is married to "+husbID+"")
                                        break
                                    if lst3[0] == '0':
                                        break
                                    k += 1

                        k += 1
        wrong = set(wrong)
        return wrong


def birthAfterMOmDeath(m_dictIndi, m_dictFam):
    wrong = []
    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
              'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    for i in m_dictFam:
        maleID = m_dictFam[i]['Husb']
        femaleID = m_dictFam[i]['Wife']
        if 'death' in m_dictIndi[femaleID].keys():
            motherdeath = m_dictIndi[femaleID]['death'].split()
            year = int(motherdeath[2])
            month = int(months[motherdeath[1]])
            day = int(motherdeath[0])
            mother_death = datetime.date(year, month, day)
            children = m_dictFam[i]['Children']
            for child in children:
                childBirth = m_dictIndi[child]['birth']
                childBirth = childBirth.split()
                year = int(childBirth[2])
                month = int(months[childBirth[1]])
                day = int(childBirth[0])
                child_date = datetime.date(year, month, day)
                if mother_death < child_date:
                    wrong.append(child+" birth "+str(child_date) +
                                 " is before mother death date "+str(mother_death))
    return wrong


def connectAndInsertRecordsDB(p_dictRecords, collectionName):
    m_dbCluster = EstabilishDBConn.getConn()
    db = m_dbCluster["GedComData"]
    collection = db[collectionName]
    collection.insert_many(p_dictRecords)


def readRecords(collectionName, filterCondn):
    m_dbCluster = EstabilishDBConn.getConn()
    db = m_dbCluster["GedComData"]
    collection = db[collectionName]
    return collection.find(filterCondn)


def populateFamily(l_inpFile, l_strId):
    if isIDUnique(l_strId, arrIds):
        m_dictFam.append({idKey: l_strId, "CHILDREN": []})
        arrIds.append(l_strId)
    last_pos = l_inpFile.tell()
    line = l_inpFile.readline()
    while line.strip().split(" ", 2)[0] != 0 and line.strip().split(" ", 2)[0] != '0' and line != '':
        if line.strip().split(" ", 2)[1] in Keys and line.strip().split(" ", 2)[1] not in ["PEDI"]:
            if line.strip().split(" ", 2)[1] == "CHIL":
                m_dictFam[-1][Keys[line.strip().split(
                    " ", 2)[1]]].append(line.strip().split(" ", 2)[2])
                last_pos = l_inpFile.tell()
                line = l_inpFile.readline()
            else:
                m_dictFam[-1][Keys[line.strip().split(
                    " ", 2)[1]]] = line.strip().split(" ", 2)[2]
        last_pos = l_inpFile.tell()
        line = l_inpFile.readline()
    l_inpFile.seek(last_pos)


def populateIndividual(l_inpFile, l_strId, keyAdd):
    if isIDUnique(l_strId, arrIds):
        m_dictIndi.append({idKey: l_strId})
        arrIds.append(l_strId)
    last_pos = l_inpFile.tell()
    line = l_inpFile.readline()
    l_arrLine = line.strip().split(" ", 2)[0]
    l_strKey = l_arrLine[1]
    l_strArgs = l_arrLine[2]
    while l_strKey != 0 and l_strKey != '0' and line != '':
        if l_strKey in Keys:
            if l_strKey == "BIRT" or l_strKey == "DEAT" or l_strKey == "DIV" or l_strKey == "MARR":
                keyAdd = Keys[l_strKey]
                last_pos = l_inpFile.tell()
                line = l_inpFile.readline()
                continue
            else:
                if keyAdd != "":
                    m_dictIndi[-1][keyAdd + Keys[l_strKey]] = l_strArgs
                else:
                    m_dictIndi[-1][Keys[l_strKey]] = l_strArgs
                keyAdd = ""
        last_pos = l_inpFile.tell()
        line = l_inpFile.readline()
    l_inpFile.seek(last_pos)


def readInputAndPopulateDict(p_strFileName):
    l_inpFile = open(p_strFileName, 'r')
    line = l_inpFile.readline()
    keyAdd = ""
    while line != '':
        l_arrTxt = line.strip().split(" ", 2)
        if l_arrTxt[0] == 0 or l_arrTxt[0] == '0':
            l_strLvl, l_strTag, l_strValid, l_strArgs = extractInfoZeroLevel(
                l_arrTxt)
            if l_strTag == "INDI":
                l_strId = l_strArgs
                populateIndividual(l_inpFile, l_strId, keyAdd)
            if l_strTag == "FAM":
                l_strId = l_strArgs
                populateFamily(l_inpFile, l_strId)
        line = l_inpFile.readline()


def populateFamDataInIndTable():
    for elem in m_dictIndi:
        indId = elem[idKey]
        famRecord = [record for record in m_dictFam if (Keys["HUSB"] in record and record[Keys["HUSB"]]
                                                        == indId) or (Keys["WIFE"] in record and record[Keys["WIFE"]] == indId)]
        if famRecord:
            famRecord = famRecord[0]
            elem["CHILDREN"] = famRecord["CHILDREN"] if famRecord["CHILDREN"] else "None"
            elem["SPOUSE"] = famRecord[Keys["HUSB"]] if (Keys["WIFE"] in famRecord and famRecord[Keys["WIFE"]
                                                                                                 ] == indId) else famRecord[Keys["WIFE"]] if (Keys["HUSB"] in famRecord and famRecord[Keys["HUSB"]
                                                                                                                                                                                      ] == indId) else "NA"
        else:
            elem["CHILDREN"] = "None"
            elem["SPOUSE"] = "NA"
        elem["DEATHDATE"] = "NA" if "DEATHDATE" not in elem else elem["DEATHDATE"]


def handleEmptyKeysInFam():
    for elem in m_dictFam:
        if Keys["HUSB"] not in elem:
            elem[Keys["HUSB"]] = "NA"
            tempWife = elem[Keys["WIFE"]]
            elem.pop(Keys["WIFE"])
            elem[Keys["WIFE"]] = tempWife
        if Keys["WIFE"] not in elem:
            elem[Keys["WIFE"]] = "NA"

        # elem[Keys["HUSB"]] = "NA" if Keys["HUSB"] not in elem else elem[Keys["HUSB"]]
        # elem[Keys["WIFE"]] = "NA" if Keys["WIFE"] not in elem else elem[Keys["WIFE"]]


def addIntoIndiOutputTable():
    for objInd in m_dictIndi:
        val = list(objInd.values())
        m_indiTable.add_row(val)


def addIntoFamilyOutputTable():
    for objFam in m_dictFam:
        val = list(objFam.values())
        m_famTable.add_row(val)


def birthafterdeath(p_strFileName):
    file = open(p_strFileName, 'r')
    x = []
    for count, line in enumerate(file):
        x.append(line)
    y = len(x)-1
    for i in range(0, y):
        if (x[i][2:6]) == "DEAT":
            birth = x[i-1][7:].strip()
            death = x[i+1][7:].strip()
            if datetime.strptime(birth, '%d %b %Y').date() > datetime.strptime(death, '%d %b %Y').date():
                print("Birth date cant be after death date")
    for i in range(0, y):
        if (x[i][2:6]) == "MARR":
            marraige = x[i+1][7:].strip()
            if datetime.strptime(birth, '%d %b %Y').date() > datetime.strptime(marraige, '%d %b %Y').date():
                print("Birth date cant be after marraige date")


# Shoaib's portion
# m_dictIndi = {'1a': {'birth': "1 JAN 1860"}}


def ageValidator(m_dictIndi):
    wrongAge = []
    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
              'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    for i in m_dictIndi:
        print(i)
        birth = m_dictIndi[i]['birth'].split()
        birth = datetime.date(int(birth[2]), int(
            months[birth[1]]), int(birth[0]))
        # print(birth)
        if 'death' in m_dictIndi[i].keys():
            death = m_dictIndi[i]['death'].split()
            # print(months[death[1]])
            year = int(death[2])
            month = int(months[death[1]])
            day = int(death[0])
            print(day, month, year)
            death = datetime.date(year, month, day)
            age = death.year - birth.year - \
                ((death.month, death.day) < (birth.month, birth.day))
            print(age)
            if age >= 150:
                wrongAge.append(i+" has age:"+str(age) +
                                " which is more than 150")
        else:
            today = datetime.date.today()
            age = today.year - birth.year - \
                ((today.month, today.day) < (birth.month, birth.day))
            print(age)
            wrongAge.append(i+" has age:"+str(age)+" which is more than 150")
    return wrongAge


# m_dictIndi = {'1a': {'birth': "1 JAN 1860"}}


def ageCHeck(m_dictIndi):
    wrongAge = []
    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
              'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    for i in m_dictIndi:
        birth = m_dictIndi[i]['birth'].split()
        birth = datetime.date(int(birth[2]), int(
            months[birth[1]]), int(birth[0]))
        # print(birth)

        today = datetime.date.today()
        if birth > today:
            wrongAge.append(i+" has birth in future "+str(birth))
    return wrongAge


def birthAfterMOmDeath():
    wrong = []
    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
              'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    for i in m_dictFam:
        maleID = i[Keys["HUSB"]]
        femaleID = i[Keys["WIFE"]]
        if 'death' in m_dictIndi[femaleID].keys():
            motherdeath = m_dictIndi[femaleID]['death'].split()
            year = int(motherdeath[2])
            month = int(months[motherdeath[1]])
            day = int(motherdeath[0])
            mother_death = datetime.date(year, month, day)
            children = i['Children']
            for child in children:
                childBirth = m_dictIndi[child]['birth']
                childBirth = childBirth.split()
                year = int(childBirth[2])
                month = int(months[childBirth[1]])
                day = int(childBirth[0])
                child_date = datetime.date(year, month, day)
                if mother_death < child_date:
                    wrong.append(child+" birth "+str(child_date) +
                                 " is after mother death date "+str(mother_death))
    return wrong


Keys = initKeys()
readInputAndPopulateDict(inpFileName)
populateFamDataInIndTable()
handleEmptyKeysInFam()

# connectAndInsertRecordsDB(m_dictIndi, "Individual")
# connectAndInsertRecordsDB(m_dictFam, "Family")

addIntoIndiOutputTable()
addIntoFamilyOutputTable()


# Ru's portion


print("Individuals Data:\n")
print(m_indiTable)
print("Family Data:\n")
print(m_famTable)
birthafterdeath(inpFileName)
# birthAfterMOmDeath()
