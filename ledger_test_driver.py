import sys
from ledger import Transaction,BankAccount,BalanceRetrievalMethod
from datetime import date,timedelta
from functools import reduce

testresult = []

def resetTestResults():
    global testresult
    testresult = []
    
def printTestResults(label):
    print("\n\n************************************************************************************")
    print (label, " Test Results for ",len(testresult), " Test Cases:")
    passed = [t for t in testresult if t==True]
    print ("  Passed: ",len(passed))
    print ("  Failed: ",len(testresult) - len(passed))
    print("************************************************************************************\n\n")

def test_add_transaction(in_date: str,  in_amount: float,in_from: str, in_to: str):
    t= Transaction(in_date,\
                   in_amount,\
                   in_from,\
                   in_to)
    
def test_case_balance(in_owner: str, in_date: str, in_expected_balance: float, in_test_case_n: int, \
                      in_method: BalanceRetrievalMethod,  in_expected_excep: bool = False, in_chk_pass_fail: bool = True):
    """ instantiate a BankAccount instance for specified account owner, and retrieve the account balance for specified date
    if in_chk_pass_fail is True, compare results and indicate PASS/FAIL  """
    global testresult
    
    if in_method == BalanceRetrievalMethod.REDUCED: strMethod = 'REDUCED'
    if in_method == BalanceRetrievalMethod.CACHED: strMethod = 'CACHED'
    strInDate = in_date
    if in_date is None: strInDate = 'None'
    
    strTestCaseN = '{:0>10}'.format(str(in_test_case_n))
    strTestCase = '{:<60}'.format("".join(["(account: " ,in_owner," date: ",strInDate, " method: ", strMethod, ")"]))

    account = BankAccount.getAccount(in_owner)
    account.setBalanceRetrievalMethod(in_method)
    #print(in_owner, " Account: ", account)
    try:
        balance = account.getBalance(in_date)
        if not in_chk_pass_fail: 
            print("Run Case ", strTestCaseN, strTestCase)
            testresult.append(True)
            return True
        assert balance == in_expected_balance
        if not in_expected_excep: 
                 print("Test Case ", strTestCaseN, " ", strTestCase, "  PASSED")
                 testresult.append(True)
                 return True
    except Exception as error:
        print("error: ", error)
        if not in_chk_pass_fail: 
            print("Run Case ", strTestCaseN, " ", strTestCase, "   EXCEPTION")
            testresult.append(False)
            return False
        if in_expected_excep: 
            print("Test Case ", strTestCaseN," ", strTestCase, "  PASSED")
            testresult.append(True)
            return True
        else:
            print("Test Case ", strTestCaseN," ", strTestCase, "   FAILED:  balance: ",balance," not equal to ", in_expected_balance)               
            testresult.append(False)
            return False
        pass
         
input_transactions = \
[ \
{'trans_date':'2015-01-16','from_party':'john','to_party': 'mary','amount':125.00}, \
{'trans_date': '2015-01-17','from_party':'john','to_party':'supermarket','amount':20.00},\
{'trans_date': '2015-01-17','from_party':'mary','to_party':'insurance','amount': 100.00}, \
{'trans_date': '2020-04-17','from_party':'irs','to_party':'george','amount':1200.00},\
{'trans_date': '2020-04-17','from_party':'irs','to_party':'john','amount':1200.00},\
{'trans_date': '2020-04-17','from_party':'irs','to_party':'mary','amount':1200.00},\
{'trans_date': '2015-05-17','from_party':'george','to_party':'mary','amount':120.00},\
{'trans_date': '2015-05-17','from_party':'george','to_party':'irs','amount':360.00},\
{'trans_date': '2020-04-17','from_party':'irs','to_party':'mary','amount':780.00}\
]

def runTestInputTransactions():
    for trans in input_transactions:
        test_add_transaction(trans['trans_date'],\
                             trans['amount'],\
                             trans["from_party"],\
                             trans["to_party"])

def runRegressionTests(method: BalanceRetrievalMethod = BalanceRetrievalMethod.REDUCED):
    #input_transactions  = sorted(input_transactions, key = lambda i: i.trans_date)
    
                       
    print("run some positive and negative tests")

    test_case_balance('mary', '2015-01-01', 0, 1, method)
 
    #if method == BalanceRetrievalMethod.REDUCED: print("********")
    
    test_case_balance('mary', '2015-01-16', 125, 2, method)

    test_case_balance('mary', '2015-02-01', 25, 3, method)

    test_case_balance('mary', None, 2125, 4, method)

    test_case_balance('john', '2015-01-17', -145, 5, method)

    test_case_balance('john', '2015-13-17', None, 6, method, True)

    test_case_balance('george', '2016-01-01', -480, 7, method)

    test_case_balance('mary', '2020-04-18', 2125, 8, method)
    
    
def runRandomTests(numTransactions):

     
    #turn parallel sequences into dictionaries for the test driver
        
    from itertools import combinations,chain
    from random import choice,randrange

    owners = ['rachel', 'peter', 'gary', 'connor','theresa','david','ben','jasmine','erica']

    party_combos = list(combinations(owners,2))

    print (party_combos)

    parties = [choice(party_combos) for i in range(numTransactions)]
    
    print (parties)
    
    amounts = [randrange(-110,1600) for i in range(numTransactions) ]
       
    print (amounts)

    date_offsets = [randrange(0, 365) for i in range(numTransactions) ]

    print (date_offsets)
    
    d = zip(parties,amounts,date_offsets)
                
    input = list(d)

    print("input: ",input)
    
    base_date = date(2019,1,1)
    print("trans_date,","amount,","owner")
    
    #minimalistic account ledger for validating BankAccount class balances
    transArr = []
    for tpl in input:
        try:        
            trans_date = base_date + timedelta(tpl[2])
            str_date = trans_date.strftime('%Y-%m-%d')
            trans_amt = tpl[1]
            trans_from = tpl[0][0]
            trans_to = tpl[0][1]
            print(trans_date,",",trans_amt,",",trans_to)
            trans = {'date': trans_date,'amount':trans_amt, 'owner':trans_to}
            
            transArr.append(trans)
            
            print(trans_date,",",-1*trans_amt,",",trans_from)
            trans = {'date': trans_date,'amount':-1*trans_amt, 'owner':trans_from}
            transArr.append(trans)
            
            test_add_transaction(str_date,\
                                 trans_amt,\
                                 trans_from,\
                                 trans_to)
        except (Exception) as error:
            debugprint("error: ", error)
            pass

    run_num = 0
    methods=[BalanceRetrievalMethod.CACHED,BalanceRetrievalMethod.REDUCED]
    for tpl in input:
        try:        
            run_num+=1
            trans_date = base_date + timedelta(tpl[2])
            str_date = trans_date.strftime('%Y-%m-%d')
            trans_amt = tpl[1]
            trans_from = tpl[0][0]
            trans_to = tpl[0][1]
            method = choice(methods)
            
            #use our minimalistic transArr account ledger with reduce call to get expected balance          
            trans_to_date = [item["amount"] for item in transArr if item["owner"] == trans_from and item["date"] <= trans_date]
            expected_bal = reduce((lambda x, y: x+y), trans_to_date,0)
            
            test_case_balance(trans_from, str_date, expected_bal, run_num, method, in_chk_pass_fail=True)

            run_num+=1
            #use our minimalistic transArr account ledger with reduce call to get expected balance          
            trans_to_date = [item["amount"] for item in transArr if item["owner"] == trans_to and item["date"] <= trans_date]
            expected_bal = reduce((lambda x, y: x+y), trans_to_date,0)
            
            test_case_balance(trans_to, str_date, expected_bal, run_num, method, in_chk_pass_fail=True)

            run_num+=1
            trans_date = base_date + timedelta(tpl[2]-1) 
            str_date = trans_date.strftime('%Y-%m-%d')
            #use our minimalistic transArr account ledger with reduce call to get expected balance          
            trans_to_date = [item["amount"] for item in transArr if item["owner"] == trans_from and item["date"] <= trans_date]
            expected_bal = reduce((lambda x, y: x+y), trans_to_date,0)
            
            test_case_balance(trans_from, str_date, expected_bal, run_num, method, in_chk_pass_fail=True)

            run_num+=1

            trans_date = base_date + timedelta(tpl[2]+1) 
            str_date = trans_date.strftime('%Y-%m-%d')
             #use our minimalistic transArr account ledger with reduce call to get expected balance          
            trans_to_date = [item["amount"] for item in transArr if item["owner"] == trans_to and item["date"] <= trans_date]
            expected_bal = reduce((lambda x, y: x+y), trans_to_date,0)
            
            test_case_balance(trans_to, str_date, expected_bal, run_num, method, in_chk_pass_fail=True)

        except (Exception) as error:
            debugprint("error: ", error)
            pass
    
runRandomTestNum = 0

   
    
resetTestResults()

runTestInputTransactions()

runRegressionTests(BalanceRetrievalMethod.REDUCED)
printTestResults('Regression Test(REDUCED)')

resetTestResults()
runRegressionTests(BalanceRetrievalMethod.CACHED)
printTestResults('Regression Test(CACHED)')

import cProfile

runRandomTestNum = 100

if len(sys.argv) > 1 and sys.argv[1].isnumeric(): runRandomTestNum = int(sys.argv[1])

resetTestResults()
runRandomSpec = "runRandomTests(" + str(runRandomTestNum) + ")"
print(runRandomSpec)

cProfile.run(runRandomSpec, 'restats')
printTestResults('Random Tests')

import pstats
from pstats import SortKey
p = pstats.Stats('restats')
p.strip_dirs().sort_stats(-1).print_stats()
"""
tbd: integrate documentation and test cases with doctest

if __name__ == "__main__":
    import doctest
    doctest.testmod()
"""