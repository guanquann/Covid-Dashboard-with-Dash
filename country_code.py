import pycountry
import pandas as pd

df = pd.read_csv('total_cases.csv')
country_names = list(df.columns[:])
# for country_name in country_names:
#     print(country_name)
# print(country_names)
# country_names.remove('Bonaire Sint Eustatius and Saba')
# country_names.remove('Cape Verde')
# country_names.remove('International')
# country_names.remove('Palestine')
# country_names.remove('Vatican')

countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_3

codes = [countries.get(country, country) for country in country_names]

dff = df.copy()
# Change column names
dff.columns = codes

# Rotate table
dff = dff.T.reset_index().reindex()

# Rename current header name to date and remove date row
dff = dff.rename(columns=dff.iloc[0])
dff = dff.drop(df.index[0])

# Remove World row, index 0 is empty
dff = dff.drop(df.index[1])
dff.rename(columns={'date': 'Country Code'}, inplace=True)

dff = dff.set_index('Country Code')
dff.rename(index={'British Virgin Islands': 'VGB', 'Brunei': 'BRN', 'Czech Republic': 'CZE',
                  'Congo, Democratic Republic of the': 'COD', 'Faeroe Islands': 'FRO', 'Falkland Islands': 'FLK',
                  'Iran': 'IRN', 'Kosovo': 'KSV', 'Macedonia': 'MKD', 'Moldova': 'MDA', 'Russia': 'RUS',
                  'South Korea': 'KOR', 'Swaziland': 'SWZ', 'Syria': 'SYR', 'Taiwan': 'TWN', 'Tanzania': 'TZA',
                  'Timor': 'TLS', 'United States Virgin Islands': 'VGB', 'Venezuela': 'VEN', 'Vietnam': 'VNM'},
           inplace=True)

dff = dff.fillna(0)
print(dff)
dff.to_csv('test.csv')
