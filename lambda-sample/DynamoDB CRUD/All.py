try:
    import os
    import sys
    import datetime
    import boto3
    import time
    print("All Modules Loaded ...... ")
except Exception as e:
    print("Error {}".format(e))

class MyDB(object):
    def __init__(self, Table_Name='boto3mana'):
        self.Table_Name=Table_Name
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(Table_Name)
        self.db_client = boto3.client('dynamodb')

    @property
    def get(self):
        response = self.table.get_item(
            Key={
                'Num':"1"
            }
        )
        return response
    
    def put(self, Num='', Country='', Name=''):
        self.table.put_item(
            Item={
                'Num':Num,
                'Country':Country,
                'Name':Name
            }
        )
    
    def delete(self, Num=''):
        self.table.delete_item(
            Key={
                'Num': Num
            }
        )
    
    def describe_table(self):
        response = self.client.describe_table(
            TableName='boto3mana'
        )
        return response
    
obj = MyDB()
data = obj.get
resp = obj.put(Num='2', Country='Korea', Name='John')
