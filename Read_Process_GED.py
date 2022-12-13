# if level 0 then check for tags, otherwise simply split
from cmath import rect
from unittest import result
from prettytable import PrettyTable
from datetime import datetime
from pymongo import MongoClient
import EstabilishDBConn
import datetime

inpFileName = "M3_B2_InputGED.ged"

g_ResultString = ""
m_indiTable = PrettyTable()
m_famTable = PrettyTable()
m_indiTable.field_names = ["ID", "Name",
                           "SEX", "BIRTHDATE", "DEATHDATE", "CHILDREN", "SPOUSE"]
m_famTable.field_names = ["ID", "CHILDREN", "Husband ID", "Wife ID", "MARRIAGE DATE"]
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
    for obj in m_dictFam:
        husb = obj['HUSBAND']
        wife = obj['WIFE']
        for person in m_dictIndi:
            # print(person)
            if person['_id']==husb:
                # print(person)
                if person['SEX']!="M":
                    wrong.append("Invalid gender for id: "+husb+" with a gender value: "+person['SEX']+" in family:"+obj['_id'])
            if person['_id']==wife:
                if person['SEX']!="F":
                    wrong.append("Invalid gender for id: "+wife+" with a gender value: "+person['SEX']+" in family:"+obj['_id'])
    return wrong
 


def birthAfterMomDeath(m_dictIndi,m_dictFam):
    wrong = []
    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
              'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    for fam in m_dictFam:
        maleID = fam[Keys["HUSB"]]
        femaleID = fam[Keys["WIFE"]]
        for person in m_dictIndi:
            if person['_id']==femaleID:
                if person['DEATHDATE']!='NA':
                    motherDeath = person['DEATHDATE'].split()
                    year = int(motherDeath[2])
                    month = months[motherDeath[1]]
                    day = int(motherDeath[0])
                    motherDeath = datetime.date(year, month, day)
                    children = fam['CHILDREN']
                    for child in children:
                        for check in m_dictIndi:
                            if check['_id']==child:
                                childBirth = check['BIRTHDATE'].split()
                                year = int(childBirth[2])
                                month = months[childBirth[1]]
                                day = int(childBirth[0])
                                childBirth = datetime.date(year, month, day)
                                if motherDeath < childBirth:
                                    wrong.append("Error child birth after Mother's death : "+child+" birth "+str(childBirth) +" is after mother death date "+str(motherDeath))
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


def populateMarriageDate(p_inpFile):
    last_pos = l_inpFile.tell()
    line = l_inpFile.readline()
    if line.strip().split(" ", 2)[1] == "MARR":
        keyAdd = Keys[line.strip().split(" ", 2)[1]]
        last_pos = l_inpFile.tell()
        line = l_inpFile.readline()
        
    else:
        if keyAdd != "":
            m_dictIndi[-1][keyAdd + Keys[line.strip().split(
                " ", 2)[1]]] = line.strip().split(" ", 2)[2]
        else:
            m_dictIndi[-1][Keys[line.strip().split(
                " ", 2)[1]]] = line.strip().split(" ", 2)[2]
        keyAdd = ""

def populateFamily(l_inpFile, l_strId):
    keyAdd = ""
    marriageDate = "NA"
    if isIDUnique(l_strId, arrIds):
        m_dictFam.append({idKey: l_strId, "CHILDREN": []})
        arrIds.append(l_strId)
    last_pos = l_inpFile.tell()
    line = l_inpFile.readline()
    while line.strip().split(" ", 2)[0] != 0 and line.strip().split(" ", 2)[0] != '0' and line != '':
        print(line)
        if line.strip().split(" ", 2)[1] in Keys:
            print("heree")
            if line.strip().split(" ", 2)[1] == "CHIL":
                m_dictFam[-1][Keys[line.strip().split(
                    " ", 2)[1]]].append(line.strip().split(" ", 2)[2])
            elif line.strip().split(" ", 2)[1] == "MARR":
                keyAdd = Keys[line.strip().split(" ", 2)[1]]
                line = l_inpFile.readline()
                continue
            else:
                if keyAdd != "":
                    m_dictFam[-1][keyAdd + Keys[line.strip().split(
                    " ", 2)[1]]] = line.strip().split(" ", 2)[2]
                    keyAdd = ""
                else:
                    print("VCFNGCHHMHXHCg")
                    # print(line)
                    for i in m_dictFam:
                        print(i)
                    # print(m_dictFam,"dictfam")
                    print(Keys[line.strip().split(" ", 2)[1]],"holaa")
                    print(line.strip().split(" ", 2))
                    print(Keys[line.strip().split(" ", 2)[1]],keyAdd,"pratikkkkkkk")
                    m_dictFam[-1][Keys[line.strip().split(" ", 2)[1]]] = line.strip().split(" ", 2)[2]
        last_pos = l_inpFile.tell()
        line = l_inpFile.readline()
    l_inpFile.seek(last_pos)


def populateIndividual(l_inpFile, l_strId, keyAdd):
    if isIDUnique(l_strId, arrIds):
        m_dictIndi.append({idKey: l_strId})
        arrIds.append(l_strId)
    last_pos = l_inpFile.tell()
    line = l_inpFile.readline()
    while line.strip().split(" ", 2)[0] != 0 and line.strip().split(" ", 2)[0] != '0' and line != '':
        if line.strip().split(" ", 2)[1] in Keys:
            if line.strip().split(" ", 2)[1] == "BIRT" or line.strip().split(" ", 2)[1] == "DEAT" or line.strip().split(" ", 2)[1] == "DIV" or line.strip().split(" ", 2)[1] == "MARR":
                keyAdd = Keys[line.strip().split(" ", 2)[1]]
                last_pos = l_inpFile.tell()
                line = l_inpFile.readline()
                continue
            else:
                if keyAdd != "":
                    m_dictIndi[-1][keyAdd + Keys[line.strip().split(
                        " ", 2)[1]]] = line.strip().split(" ", 2)[2]
                else:
                    m_dictIndi[-1][Keys[line.strip().split(
                        " ", 2)[1]]] = line.strip().split(" ", 2)[2]
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
        if Keys["MARR"]+Keys["DATE"] not in elem:
            elem[Keys["MARR"]+Keys["DATE"]] = "NA"; 

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



def AgeValidator(m_dictIndi):
    wrongAge = []
    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
              'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    for person in m_dictIndi:
        birth = person['BIRTHDATE'].split()
        year = int(birth[2])
        month = months[birth[1]]
        day = int(birth[0])
        birth = datetime.date(year, month, day)
        # print(birth)
        if person['DEATHDATE']!='NA':
            death = person['DEATHDATE'].split()
            # print(months[death[1]])
            year = int(death[2])
            month = months[death[1]]
            day = int(death[0])
            death = datetime.date(year, month, day)
            age = death.year - birth.year - ((death.month, death.day) < (birth.month, birth.day))
            if age >= 150:
                wrongAge.append("Invalid age error: "+person['_id']+" has age:"+str(age) +" which is more than 150")
            if age <= 0:
                wrongAge.append("Invalid age error: "+person['_id']+" has age:"+str(age) +" which is less than or equal to 0")
        else:
            today = datetime.date.today()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            if age >= 150:
                wrongAge.append("Invalid age error: "+person['_id']+" has age:"+str(age) +" which is more than 150")
            if age <= 0:
                wrongAge.append("Invalid age error: "+person['_id']+" has age:"+str(age) +" which is less than or equal to 0")
    return wrongAge



def birthCheck(m_dictIndi):
    wrongAge = []
    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
              'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    for person in m_dictIndi:
        birth = person['BIRTHDATE'].split()
        year = int(birth[2])
        month = months[birth[1]]
        day = int(birth[0])
        birth = datetime.date(year, month, day)
        # print(birth)

        today = datetime.date.today()
        if birth > today:
            wrongAge.append("Person cannot have birth in future. Person:"+person['_id']+" has birth in future "+str(birth))
    return wrongAge





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
# birthafterdeath(inpFileName)

print("__________________________________________________________________________________________________")
print(m_dictFam)
print("__________________________________________________________________________________________________")
print(m_dictIndi)
print("__________________________________________________________________________________________________")
print(validateMarriageGender(m_dictIndi,m_dictFam))
print(birthCheck(m_dictIndi))
print(birthAfterMomDeath(m_dictIndi,m_dictFam))
print(AgeValidator(m_dictIndi))