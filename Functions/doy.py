def doy(Y,M,D):
    """ 
        Copy and past from:
        https://stackoverflow.com/questions/620305/convert-year-month-day-to-day-of-year-in-python
        Given year, month, and day;
        Return day of year.
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7.
    """
    def IsLeapYear(Year):
        """ If year is a leap year return True;
            else return False.
            Copy and past from:
            https://stackoverflow.com/questions/620305/convert-year-month-day-to-day-of-year-in-python
        """
        if Year % 100 == 0:
            return Year % 400 == 0
        return Year % 4 == 0

    [Y,M,D] = [int(Y),int(M),int(D)]
    if IsLeapYear(Y):
        K = 1
    else:
        K = 2
    N = int((275 * M) / 9.0) - K * int((M + 9) / 12.0) + D - 30
    return N