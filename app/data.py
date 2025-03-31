import pandas as pd
from sodapy import Socrata

class Inspections():
    
    client = Socrata('data.cityofnewyork.us', 
                     '89Sge8OcdXjFPgCwlD6CKbgZR',
                     username='mbabury000@citymail.cuny.edu',
                     password='Crocheron2002@')
    
    @classmethod
    def return_grades(cls):
        results = cls.client.get("43nn-pn8j", limit=2000)
        results_df = pd.DataFrame.from_records(results)
        
        results_df = results_df[['dba', 'zipcode', 'grade', 'latitude', 'longitude']]
        results_df = results_df.dropna()
        

        return results_df.to_dict(orient="records")
