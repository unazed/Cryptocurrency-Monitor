"""
Monitors the BTC market for changes and rises in certain markets.
"""

from time import asctime
from time import localtime
from time import sleep
from requests import get


def get_time():
    "Returns the local-time"

    return asctime(localtime())


def get_data(_fail_count=0, _max_fail_count=10):
    "Returns data from the API, includes error-checking and API failure handling."

    data = get("https://bittrex.com/api/v1.1/public/getmarketsummaries").json()
    if not data['success']:
        print("{*} Unsuccessful API call. Check if the API is down or under maintenance?")
        if _fail_count == _max_fail_count:
            print("{*} API timeout/failure.")
            return False
        return get_data(_fail_count+1)
    return data['result']


def find_diff(seq1, seq2, subscript=None, key=None):
    """
    seq1 -> (list, dict)
    seq2 -> (list, dict)
    key  -> str: This will return the matches with a key
        to identify the matches and what names they belong to.
    subscript -> string: If the sequences are able to be subscripted
        then this will compare the subscripted values instead of the
        list/dictionary itself.
    """

    match = []
    for i, j in zip(seq1, seq2):
        if not subscript is None:
            if not i[subscript] == j[subscript]:
                match.append([i[key] if not key is None else None, i[subscript], j[subscript]])
        else:
            if not i == j:
                match.append([i, j])
    return match


def run_bot(high_low=True, perc=30.0, delay=5, dynamic=False, _rerun=False):
    """
    high_low -> bool:
        False: Prints based on whether the values go above original
               value by the given percentage
        True: Prints based on whether the value drops below the original
              basd on the given percentage
        None:
              Prints any sort of change that has happened to the values.
    perc -> float:
        Percentage that is the determining factor for how low or high
        a value must drop before being acknowledged.
    dynamic -> bool:
        True: Will change current percentage by 10% based on whether
              the market values rise or drop, requires high_low to be
              set to None as else the code will simply reach 0% and not
              give the expected outcome.
    """

    if not isinstance(perc, float):
        perc = float(perc)

    while 1:
        last_market = get_data()
        sleep(delay)
        market = get_data()

        if not last_market or not market:
            print("{*} Exitting main bot loop due to an error with the API call.")
            return False

        for name, previous, latest in find_diff(last_market, market, 'Last', 'MarketName'):
            perc_change = (latest - previous)/latest*100

            if latest <= previous-(previous*(perc/100)) and (high_low or high_low is None):
                if dynamic and high_low is None:
                    perc -= perc/10
                yield ["decrease", perc_change, name]


            if latest >= previous+(previous*(perc/100)) and not high_low:
                if dynamic and high_low is None:
                    perc += perc/10
                yield ["increase", perc_change, name]

            