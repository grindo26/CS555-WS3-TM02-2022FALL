# if level 0 then check for tags, otherwise simply split
from collections import OrderedDict
from prettytable import PrettyTable
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


def readInputAndPopulateDict(p_strFileName):
    with open(p_strFileName, 'r') as l_inpFile:
        for line in l_inpFile:
            l_arrTxt = line.strip().split(" ", 2)
            if l_arrTxt[0] == 0 or '0':
                l_strLvl, l_strTag, l_strValid, l_strArgs = extractInfoZeroLevel(
                    l_arrTxt)
                if l_strTag == "INDI":
                    l_strId = l_strArgs
                    l_strName = extractNameFromLine(next(l_inpFile))
                    if l_strId not in m_dictIndi:
                        m_dictIndi[l_strId] = l_strName.strip()
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


print(m_indiTable)
print(m_famTable)
