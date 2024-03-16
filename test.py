with open("countries1.txt", "r") as countryList:
    CountryList1 = []
    for row in countryList:
        CountryList1.append(row.rstrip())
    print(CountryList1)
    
    