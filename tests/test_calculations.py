# reminder naming matters, prefix test on fuctions (below) and name of file to auto-find tests with pytest
from app.calculations import add, subtract, multiply, divide, BankAccount, InsufficientFunds
import pytest

# these prevent repetitive code - creating bank accounts in each test below
@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(50)

@pytest.mark.parametrize("num1, num2, expected", [
    (3, 9, 12),
    (7, 1, 8),
    (15, 21, 36)
])

def test_add(num1, num2, expected):
    print('testing add function')
    assert add(num1 , num2) == expected

def test_subtract():
    print('testing subtract function')
    assert subtract(8 , 8) == 0

def test_multiply():
    print('testing multiply function')
    assert multiply(8 , 8) == 64

def test_divide():
    print('testing divide function')
    assert divide(8 , 8) == 1

def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 50

def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0

def test_withdraw(bank_account):
    bank_account.withdraw(10)
    assert bank_account.balance == 40

def test_deposit(bank_account):
    bank_account.deposit(10)
    assert bank_account.balance == 60

def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert round(bank_account.balance, 6) == 55

@pytest.mark.parametrize("deposited, withdrew, expected", [
    (200, 100, 100),
    (50, 10, 40),
    (1200, 200, 1000)
])

def test_bank_transaction(zero_bank_account, deposited, withdrew, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == expected

# how to tell python you expect an exception/error
def test_insufficient_funds(zero_bank_account):
    with pytest.raises(InsufficientFunds):
        zero_bank_account.withdraw(200)