import unittest
import Read_Process_GED as GEDcode


class TestGED (unittest.TestCase):

    def test_uniqueIds(self):
        self.assertTrue(GEDcode.isIDUnique(5, [1, 2]))
        self.assertFalse(GEDcode.isIDUnique(5, [5, 2]))
        self.assertTrue(GEDcode.isIDUnique(5, ["@I1", 2]))
        self.assertTrue(GEDcode.isIDUnique(5, [1, "-5"]))
        self.assertFalse(GEDcode.isIDUnique("@I7@", ["@I11", "@I7@"]))
        # Swaraj's portion
         self.assertEqual(GEDcode.birthAfterMOmDeath({'PratikID':{'birth':'01 JAN 1975'}, 'PratikshaID':{'death':'02 NOV 2012'}, 'praID':{'birth':'02 JAN 2009'}, 'tikID':{'birth':'02 JUN 2016'}},{'1a':{'Husb':'PratikID', 'Wife':'PratikshaID','Children':['praID','tikID']}}),['tikID birth 2016-06-02 is after mother death date 2012-11-02'])
        self.assertEqual(GEDcode.birthAfterMOmDeath({'@I2@':{'death':'12 JUN 2007'},'@I8@':{'birth':'03 MAR 2009'}, '@I9@':{'birth':'07 MAY 2012'}},{'@F4@':{'Husb':'@I1@','Wife':'@I2@','Children':['@I8@','@I9@']} }),['@I8@ birth 2009-03-03 is after mother death date 2007-06-12', '@I9@ birth 2012-05-07 is after mother death date 2007-06-12'])
        self.assertEqual(GEDcode.birthAfterMOmDeath({'@I2@':{'death':'12 JUN 2017'},'@I8@':{'birth':'03 MAR 2009'}, '@I9@':{'birth':'07 MAY 2012'}},{'@F4@':{'Husb':'@I1@','Wife':'@I2@','Children':['@I8@','@I9@']} }),[])
        self.assertEqual(GEDcode.birthAfterMOmDeath({'@I2@':{'death':'12 JUN 2016'},'@I8@':{'birth':'03 MAR 2018'}, '@I9@':{'birth':'07 MAY 2021'}},{'@F4@':{'Husb':'@I1@','Wife':'@I2@','Children':['@I8@','@I9@']} }),['@I8@ birth 2018-03-03 is after mother death date 2016-06-12', '@I9@ birth 2021-05-07 is after mother death date 2016-06-12'])
        self.assertEqual(GEDcode.birthAfterMOmDeath({'@I4@':{'death':'26 AUG 2015'},'@I13@':{'birth':'28 AUG 2015'}, '@I14@':{'birth':'25 MAY 2015'}, '@I12@':{'birth':'27 AUG 2015'}},{'@F4@':{'Husb':'@I1@','Wife':'@I4@','Children':['@I12@','@I13@','@I14@']} }),['@I12@ birth 2015-08-27 is after mother death date 2015-08-26', '@I13@ birth 2015-08-28 is after mother death date 2015-08-26'])
        # Shoaib's portion
        self.assertEqual(GEDcode.ageCheck({'@I2@':{'birth':"1 JAN 2060"}}),['@I2@ has birth in future 2060-01-01'])
        self.assertEqual(GEDcode.ageCheck({'@I3@':{'birth':'2 MAR 2023'}}),['@I3@ has birth in future 2023-03-02'])
        self.assertEqual(GEDcode.ageCheck({'@I4@':{'birth':'2 JAN 2021'}}),[])
        self.assertEqual(GEDcode.ageCheck({'@I5@':{'birth':'2 JAN 2023'}}),['@I5@ has birth in future 2023-01-02'])
        self.assertEqual(GEDcode.ageCheck({'@I6@':{'birth':'2 AUG 2025'}}),['@I6@ has birth in future 2025-08-02'])

if __name__ == "__main__":
    unittest.main()
