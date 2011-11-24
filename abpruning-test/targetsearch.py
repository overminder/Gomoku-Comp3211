
from abpruning import main as _main

def main(argv):
    _main(argv)
    return 0

def target(driver, argl):
    driver.exe_name = 'search-c'
    return main, None

