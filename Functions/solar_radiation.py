def solar_radiation(Latitude,DOY,Year,Print):
    '''
    This function is built based on the learning materials formed by G.P. Merkley.
    The original equations are taken from Allen, et al. (1993),
    Duffie and Beckman (1980), and London and Frohlich (1982)
    
    Parameters:
    Latitude: the latitude of the place.
    DOY: day of year.
    Year: the year with four digital number, eg., 2024.
    Print: if you want to see the results during the calculation. 
            "YES", showing the results, and other comments (string format) won't show the results.

    Return:
    Solar radiation in mm/day will be returned.
    '''
    import math
    pi = math.pi
    latitude_radians = Latitude*pi/180

    # Leap year or not?
    if Year % 4 == 0:
        DaysInYear = 366
    else:
        DaysInYear = 365
    # Declination of the sun
    ds = 0.4093*math.sin((2*pi*(284+DOY))/DaysInYear)
    # Relative distance from the earth to the sun
    dr = 1+0.033*math.cos(2*pi*DOY/DaysInYear)
    # The sunset hour angle
    ws = 1/math.acos(-1*math.tan(latitude_radians)*math.tan(ds))
    # The solar radiation in MJ/(m^2day)
    ra = 37.6*dr*(ws*math.sin(latitude_radians)*math.sin(ds)+math.cos(latitude_radians)*math.cos(ds)*math.sin(ws))

    if Print =="YES":
        print("This year contains:",DaysInYear,"days.")
        print("The declination of the sun is:",round(ds,4))
        print("The relative distance from the earth to the sun is:",round(dr,4))
        print("The sunset hour angle in decimal value is:",round(ws,4))
        print("The solar radiation at the location is:",round(ra,4))
    else:
        pass

    return(ra)