# if level 0 then check for tags, otherwise simply split
from collections import OrderedDict
from prettytable import PrettyTable
from datetime import datetime
m_indiTable = PrettyTable()
m_famTable = PrettyTable()
m_indiTable.field_names = ["ID", "Name"]
m_famTable.field_names = ["ID", "Husband ID",
                          "Husband Name", "Wife ID", "Wife Name"]

m_dictIndi = OrderedDict()
m_dictFam = OrderedDict()
# 0 level Indi Id
# 1 level NAME
# 0 level FAM Id
# 1 level FAM connections


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
def validateMarriageGender(m_dictIndi,m_dictFam,path=0):
    wrong=[]
    if path == 0:
        for i in m_dictFam:
            maleID=m_dictFam[i]['Husb']
            femaleID=m_dictFam[i]['Wife']
            
            if m_dictIndi[maleID]['sex']!='M':
                wrong.append(maleID+"with wrong sex:"+m_dictIndi[femaleID]['sex']+" is married to "+femaleID)
            elif m_dictIndi[femaleID]['sex']!='F':
                wrong.append(femaleID+"with wrong sex:"+m_dictIndi[femaleID]['sex']+" is married to "+maleID)
    else:
        f = open(path, "r")
        lines = f.read().split('\n')
        size=len(lines)
        for j in range(0,size):
            wordList=lines[j].split()
            if(len(wordList))==3 and wordList[0]=='0':
                if wordList[2]=='FAM' or wordList[1]=='FAM':
                    if lines[j+1].split()[1]!='HUSB' and lines[j+2].split()[1]!='WIFE':
                        continue
                    if lines[j+1].split()[1]=='HUSB':
                        nextLineList=lines[j+1].split()
                        husbID=nextLineList[2]
                        
                    if lines[j+2].split()[1]=='WIFE':
                        nextLineList=lines[j+2].split()
                        wifeID=nextLineList[2]

                    k=0
                    while(k < size):
                        lst3=lines[k].split()
                        if(len(lst3)>=2):
                            if lst3[0]=='0' and lst3[1]==husbID:
                                k+=1
                                while(k<size):
                                    lst3=lines[k].split()
                                    if lst3[1]=='SEX' and lst3[2]!='M':
                                        wrong.append(husbID+" with wrong sex:"+lst3[2]+" is married to "+wifeID)
                                        break
                                    if lst3[0]=='0':
                                        break
                                    k+=1
                        
                        lst3=lines[k].split()   
                        if(len(lst3)>=2):
                            if lst3[0]=='0' and lst3[1]==wifeID:
                                k+=1
                                while(k<size):
                                    lst3=lines[k].split()
                                    if lst3[1]=='SEX' and lst3[2]!='F':
                                        wrong.append(wifeID+"with wrong sex:"+lst3[2]+" is married to "+husbID+"")
                                        break
                                    if lst3[0]=='0':
                                        break
                                    k+=1
                                
                        k+=1
        wrong=set(wrong)
        return wrong
      
      
def birthAfterMOmDeath(m_dictIndi,m_dictFam):
    wrong=[]
    months = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
    for i in m_dictFam:
        maleID = m_dictFam[i]['Husb']
        femaleID = m_dictFam[i]['Wife']
        if 'death' in m_dictIndi[femaleID].keys():
            motherdeath=m_dictIndi[femaleID]['death'].split()
            year=int(motherdeath[2])
            month =  int(months[motherdeath[1]])
            day = int(motherdeath[0])
            mother_death = datetime.date(year,month,day)
            children = m_dictFam[i]['Children']
            for child in children:
                childBirth = m_dictIndi[child]['birth']
                childBirth=childBirth.split()
                year=int(childBirth[2])
                month = int(months[childBirth[1]])
                day = int(childBirth[0])
                child_date = datetime.date(year, month, day)
                if mother_death < child_date:
                    wrong.append(child+" birth "+str(child_date)+" is before mother death date "+str(mother_death))
    return wrong



def readInputAndPopulateDict(p_strFileName):
    arrIds = []
    with open(p_strFileName, 'r') as l_inpFile:
        for line in l_inpFile:
            l_arrTxt = line.strip().split(" ", 2)
            if l_arrTxt[0] == 0 or '0':
                l_strLvl, l_strTag, l_strValid, l_strArgs = extractInfoZeroLevel(
                    l_arrTxt)
                if l_strTag == "INDI":
                    l_strId = l_strArgs
                    l_strName = extractNameFromLine(next(l_inpFile))
                    if l_strId not in m_dictIndi and isIDUnique(l_strId, arrIds):
                        m_dictIndi[l_strId] = l_strName.strip()
                        arrIds.append(l_strId)
                elif l_strTag == "FAM":
                    l_strFamId = l_strArgs
                    while True:
                        l_strType, l_strId = extractSpouseIDFromLine(
                            next(l_inpFile).strip())
                        if (l_strType == "HUSB" or "WIFE") and l_strType != "":
                            if l_strFamId not in m_dictFam:
                                m_dictFam[l_strFamId] = {}
                            m_dictFam[l_strFamId][l_strType] = l_strId
                        else:
                            break


readInputAndPopulateDict("M3_B2_InputGED.ged")
for id, name in m_dictIndi.items():
    m_indiTable.add_row([id, name])

for id, val in m_dictFam.items():
    m_famTable.add_row([
        id, val.get("HUSB"), m_dictIndi.get(val.get("HUSB")), val.get("WIFE"), m_dictIndi.get(val.get("WIFE"))])

# Ru's portion


def birthafterdeath(p_strFileName):
    #file = open(r'C:\Users\rucha\Desktop\CS - 555 AGILE\ASSIGNMENT\PROJECT\M3B2 PROJECT\M3_B2_InputGED.ged', 'r')
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
m_dictIndi={'1a':{'birth':"1 JAN 1860"}}
def ageValidator(m_dictIndi):
    wrongAge=[]
    months = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
    for i in m_dictIndi:
        print(i)
        birth = m_dictIndi[i]['birth'].split()
        birth = datetime.date(int(birth[2]), int(months[birth[1]]), int(birth[0]))
        # print(birth)
        if 'death' in m_dictIndi[i].keys():
            death = m_dictIndi[i]['death'].split()
            # print(months[death[1]])
            year=int(death[2])
            month = int(months[death[1]])
            day=int(death[0])
            print(day,month,year)
            death = datetime.date(year, month, day)
            age =  death.year - birth.year - ((death.month, death.day) < (birth.month, birth.day))
            print(age)
            if age>=150:
                wrongAge.append(i+" has age:"+str(age)+" which is more than 150")
        else:
            today = datetime.date.today()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            print(age)
            wrongAge.append(i+" has age:"+str(age)+" which is more than 150")
    return wrongAge
  
  

m_dictIndi={'1a':{'birth':"1 JAN 1860"}}
def ageCHeck(m_dictIndi):
    wrongAge=[]
    months = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
    for i in m_dictIndi:
        birth = m_dictIndi[i]['birth'].split()
        birth = datetime.date(int(birth[2]), int(months[birth[1]]), int(birth[0]))
        # print(birth)
    
        today = datetime.date.today()
        if birth > today:
            wrongAge.append(i+" has birth in future "+str(birth))
    return wrongAge



# birthafterdeath("M3_B2_InputGED.ged")
print(m_indiTable)
print(m_famTable)
