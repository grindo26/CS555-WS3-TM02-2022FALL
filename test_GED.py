
# test file starts
import unittest
import Read_Process_GED as GEDcode


class TestGED (unittest.TestCase):

    def test_uniqueIds(self):
        self.assertTrue(GEDcode.isIDUnique(5, [1, 2]))
        self.assertFalse(GEDcode.isIDUnique(5, [5, 2]))
        self.assertTrue(GEDcode.isIDUnique(5, ["@I1", 2]))
        self.assertTrue(GEDcode.isIDUnique(5, [1, "-5"]))
        self.assertFalse(GEDcode.isIDUnique("@I7@", ["@I11", "@I7@"]))


if __name__ == "__main__":
    unittest.main()


# test file ends


# US33 Sprint 1 code starts:
def isIDUnique(id, list_id):
    if id not in list_id:
        return True
    else:
        return False

    # if l_strTag == "INDI":
    #                 l_strId = l_strArgs
    #                 l_strName = extractNameFromLine(next(l_inpFile))
    #                 if l_strId not in m_dictIndi and isIDUnique(l_strId, arrIds):
    #                     m_dictIndi[l_strId] = l_strName.strip()
    #                     arrIds.append(l_strId)
    #             elif l_strTag == "FAM":
    #                 l_strFamId = l_strArgs
    #                 while True:
    #                     l_strType, l_strId = extractSpouseIDFromLine(
    #                         next(l_inpFile).strip())
    #                     if (l_strType == "HUSB" or "WIFE") and l_strType != "":
    #                         if l_strFamId not in m_dictFam and and isIDUnique(l_strId, arrIds):
    #                             m_dictFam[l_strFamId] = {}
#                                 arrIds.append(l_strId)
    #                         m_dictFam[l_strFamId][l_strType] = l_strId
    #                     else:
    #                         break

# US33 Sprint 1 code ends:
