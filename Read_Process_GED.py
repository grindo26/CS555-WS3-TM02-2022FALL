# Name: Pratik Jitendra Sangle 20016174
# if level 0 then check for tags, otherwise simply split

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


l_inpFile = open('Assignment_Proj2_Input.ged', 'r')
Lines = l_inpFile.read().splitlines()
for line in Lines:
    print(f"--> {line}")
    l_arrTxt = line.split(" ", 2)
    if l_arrTxt[0] == 0 or '0':
        l_strLvl, l_strTag, l_strValid, l_strArgs = extractInfoZeroLevel(
            l_arrTxt)
    else:
        l_strLvl = l_arrTxt[0]
        l_strTag = l_arrTxt[1]
        l_strValid = checkIfValidTag(l_strTag)
        l_strArgs = l_arrTxt[2] if 2 < len(l_arrTxt) else ""
    if l_strArgs != "":
        print(f"<-- {l_strLvl}|{l_strTag}|{l_strValid}|{l_strArgs}")
    else:
        print(f"<-- {l_strLvl}|{l_strTag}|{l_strValid}")
