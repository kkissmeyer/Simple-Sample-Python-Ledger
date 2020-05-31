from dataclasses import dataclass
from datetime import date,datetime

'''SortedCollection class is published at 
https://code.activestate.com/recipes/577197-sortedcollection/ 
and made available for community use '''
from sortedcollection import SortedCollection
from bisect import bisect_left, bisect_right

from functools import reduce
import operator

from enum import Enum

#tbd - change to use standard python logging
DEBUG_ON=False
def debugprint(*args,**kwargs):
    if DEBUG_ON: print(*args,**kwargs)

@dataclass(init=False)
class TransactionSortedCollection(SortedCollection):
    def __init__(self, iterable=(), key=None):  
        super().__init__( iterable,key)
     
    def find_index_item_gt(self, k):
        'Return index of first item with a key > k, and the item.  Raise ValueError if not found'
        debugprint("TransactionSortedCollection.find_index_item_gt: self._keys=",end="")
        debugprint(self._keys)
        
        lenKeys = len(self._keys)
        try:
           i = bisect_right(self._keys, k)
        except (Exception) as error:
           debugprint("error calling:  i = bisect_right(self._keys, k): ",error)
           pass
           
        debugprint("i=",i," lenKeys=", lenKeys)
        if i != lenKeys:
            return i,self._items[i] 
        raise ValueError('No item found with key above: %r' % (k,))
    
 
class BalanceRetrievalMethod(Enum):
    CACHED = 1
    REDUCED = 2

@dataclass(init=False, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class Ledger:
    '''Class for storing all transactions across all bank accounts.'''
    _sorted_transactions_collection = TransactionSortedCollection([],key= lambda t: t._trans_date) 
    _first_transaction_date : date = None
    _last_transaction_date : date = None

    @classmethod         
    def addTransaction(cls,trans):
 
        #order the Ledger transactions by the trans_date. 
        #if there is a date collision for one or more trans, insert to the right
        cls._sorted_transactions_collection.insert_right(trans)
                           
        dts = [dt for dt in [trans._trans_date,cls._first_transaction_date] if dt ]
        cls._first_transaction_date = min(dts)
        dts = [dt for dt in [trans._trans_date,cls._last_transaction_date] if dt ]
        cls._last_transaction_date = max(dts)
        

@dataclass(init=False, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class Transaction:
    '''Class for storing individual transaction information.'''

    _trans_date: date
    _trans_amount: float
    _from_party: str
    _to_party: str

    def __init__(self,in_trans_date : date,in_trans_amount : float,\
                in_from_party : str,in_to_party : str):
        try:
            self._trans_date = datetime.strptime(in_trans_date, "%Y-%m-%d")
        except (Exception) as error:
            debugprint("error: ", error)
            raise error
        self._trans_amount = in_trans_amount
        self._from_party = in_from_party
        self._to_party = in_to_party
        #append transaction to class-level (static) list
        Ledger.addTransaction(self)
        fromAccount = BankAccount.getAccount(self._from_party)
        toAccount = BankAccount.getAccount(self._to_party)
        
        fromAccount.addTransaction(self,'debit')
        toAccount.addTransaction(self,'credit')
        
@dataclass(init=False, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class AccountTransaction:
    '''Class for storing bank account specific transaction info.'''
    _base_trans : str
    _trans_type : int
    def __init__(self,in_base_trans : Transaction,in_str_trans_type : str):
        debugprint ("initialize AccountTransaction")
        self._trans_type = 1
        if in_str_trans_type == 'debit': self._trans_type = -1
        self._base_trans = in_base_trans
        
    
@dataclass(init=False, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class BankAccount:
    '''Class for storing bank account reference data, transactions, and daily balances.'''
    _name: str
    _accounts = {}
    _current_balance : float
    _first_transaction_date : date
    _last_transaction_date : date
    _transactions = []
    
    @classmethod
    def getAccount(cls,in_name : str):
        if in_name in cls._accounts: 
            debugprint("Return existing account for ", in_name)
            return cls._accounts[in_name]    
        debugprint("Create new account for ", in_name)
        newAccount= BankAccount(in_name)
        #add account to static class dictionary
        cls._accounts[in_name] = newAccount
        return newAccount
    
    def __init__(self,in_name: str):
        self._name = in_name
        BankAccount._accounts[in_name] = self
        self._daily_balance = {}
        self._current_balance=0
        self._first_transaction_date = None
        self._last_transaction_date = None
        self._balance_retrieval_method = BalanceRetrievalMethod.REDUCED
        self._sorted_transactions_collection = TransactionSortedCollection([],key= lambda t: t._base_trans._trans_date)
     
    def setBalanceRetrievalMethod(self,method: BalanceRetrievalMethod):
        """ 
        This method provides the ability to change how balances are returned at any point 
        in the lifetime of a BankAccount instance
        This is useful to balance space/cpu usage along with transaction write vs balance retrieval speed
        This retrieval method could also be selected automatically based on run-time resource conditions
        or account profile and usage (balance retrieval frequence vs transaction frequency)
        """
        if self._balance_retrieval_method == method:
            return
        self._balance_retrieval_method = method
        if self._balance_retrieval_method == BalanceRetrievalMethod.REDUCED:
            self._daily_balance = {}
        if self._balance_retrieval_method == BalanceRetrievalMethod.CACHED:
            self.updateDailyBalance()     
        
        
    def getBalance(self,on_date : str = None) -> float:
        if on_date is None: return self._current_balance  
        if self._first_transaction_date is None: return 0;
        try:
            dt = datetime.strptime(on_date,'%Y-%m-%d')
        except (Exception) as error:
            debugprint("error: ", error)
            raise error
            
        if dt < self._first_transaction_date: return 0
        if dt >= self._last_transaction_date: return self._current_balance
        
        if self._balance_retrieval_method == BalanceRetrievalMethod.CACHED:
            #return balance from daily balance cache
            bal_index = (dt - self._first_transaction_date).days

            return self._daily_balance[bal_index]

        dt_gt_index = 0
        trans = None
        
        try:
            dt_gt_index, trans = self._sorted_transactions_collection.find_index_item_gt(dt)
        except (Exception,ValueError) as error:
            dt_gt_index == 0
            trans = None
            debugprint("error", error)
            pass
            
        debugprint ("dt_gt_index: ", dt_gt_index," trans: ", trans)
        
        if dt_gt_index == 0 or dt_gt_index == 1: 
            trans = self._sorted_transactions_collection[0]
            return (trans._base_trans._trans_amount*trans._trans_type)
            
        debugprint("self._sorted_transactions_collection[:dt_gt_index ]: ",self._sorted_transactions_collection[:dt_gt_index ])
        trans_amts=[t2._base_trans._trans_amount*t2._trans_type for t2 in self._sorted_transactions_collection[:dt_gt_index ]]
        balance = reduce((lambda x, y: x+y), trans_amts) #(lambda x, y: x+y)
        
        return balance
        
        
    def updateDailyBalance(self,trans : Transaction = None):
        #if we are using the reduced balance retrieval method return
        if self._balance_retrieval_method == BalanceRetrievalMethod.REDUCED:
            return
            
        debugprint("updateDailyBalance")
                    
        balance = 0;
        lasti = -1
        
        #transactions are already sorted by trans_date 
        transGen = self.getTransaction(trans) #begin updating daily_balance from transaction trans
        while 1:
            try:
                t = next(transGen)
            except (StopIteration) as error:
                break;
            amount=t._base_trans._trans_amount*t._trans_type
            diff = self._first_transaction_date - t._base_trans._trans_date
            i = abs(diff.days)
            debugprint("while iter i: ",i)
            if lasti == -1: lasti = i
            
            for j in range(lasti,i):
                self._daily_balance[j] = balance
            balance+=amount
            self._daily_balance[i]=balance
            lasti = i
            
    
        
    def addTransaction(self,transIn : Transaction,trans_type : str) -> float:
        trans = AccountTransaction(transIn,trans_type)
        debugprint("BankAccount._addTransaction: ",trans)

        self._current_balance = self._current_balance +(trans._base_trans._trans_amount*trans._trans_type)
        
        self._sorted_transactions_collection.insert_right(trans)
        
        dts = [dt for dt in [trans._base_trans._trans_date,self._first_transaction_date] if dt ]
        self._first_transaction_date = min(dts)
        dts = [dt for dt in [trans._base_trans._trans_date,self._last_transaction_date] if dt ]
        self._last_transaction_date = max(dts)

        self.updateDailyBalance()
        debugprint("transactions: ",self._sorted_transactions_collection)
        debugprint("daily_balance: ",self._daily_balance)
        return self._current_balance

    def getTransactionIndex(self, tran : Transaction = None):
        if tran is None: return -1
        n = len(self._sorted_transactions_collection)
        if n == 0 : return -1
        j = n   
        while j > 0:
            if self._sorted_transactions_collection(j-1) == tran: 
                return j-1
            j -= 1
        return -1
           
    def getTransaction(self, tran : Transaction = None):
        #if a tran is provided, find it before yielding transactions
        #if tran found, begin yielding transactions from that transaction
        j = -1
        if tran: j = self.getTransactionIndex(tran)
            
        if j == -1: j = 0 
        debugprint("getTransaction j: ",j)
        
        for i, item in enumerate(self._sorted_transactions_collection[j:]):
                 yield item
        
