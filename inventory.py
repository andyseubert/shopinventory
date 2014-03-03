
from xlrd import open_workbook
from xlrd import cellname, cellnameabs, colname

import shopify
import ConfigParser
import os
import io

# API help from https://groups.google.com/forum/#!msg/shopify-app-discuss/U07XoBgN7eU/CIaaOlwOGaYJ

config = ConfigParser.ConfigParser()
configFilePath = 'c:\Users\andys\Dropbox\shopify\inventory.config'
config.read("c:\\Users\\andys\\Dropbox\\shopify\\inventory.config")
#print config.sections()

#API_Key="cc9fa84b4d3d05b7f2256f7913b66272"
#PASSWORD="0192638aacc90d3ebfe7168b9d77f1d0"
#Shared Secret	03122b58c83252e6ce85b45fc84026f3
#URL Format	https://apikey:password@hostname/admin/resource.json
#Example URL	https://cc9fa84b4d3d05b7f2256f7913b66272:0192638aacc90d3ebfe7168b9d77f1d0@flora-60.myshopify.com/admin/orders.json

api_key=config.get('shopify','api_key')
api_pass=config.get('shopify','api_pass')
storename=config.get('shopify','storename')

shop_url = "https://"+api_key+":"+api_pass+"@"+storename+".myshopify.com/admin"

inventoryFile = config.get('FileSection','storeFile')

## open excel sheet
book = open_workbook(inventoryFile)
sheet = book.sheet_by_index(0)
## check names of columns and exit if not right (notify someone)
# should be Item Number, Item Name, Qty1
#print sheet.cell(0,0).value
#print sheet.cell(0,1).value
#print sheet.cell(0,2).value
if sheet.cell(0,0).value+sheet.cell(0,1).value+sheet.cell(0,2).value != "Item NumberItem NameQty 1" :
    print sheet.cell(0,0).value+sheet.cell(0,1).value+sheet.cell(0,2).value
    print "bad columns"
    exit()

#shop_url = "https://cc9fa84b4d3d05b7f2256f7913b66272:0192638aacc90d3ebfe7168b9d77f1d0@flora-60.myshopify.com/admin"
shopify.ShopifyResource.set_site(shop_url)
shop = shopify.Shop.current
products = shopify.Product.find()
for product in products:
    #print str(product.variants[0].inventory_quantity) + " " + product.title + " >" + product.variants[0].sku +"<"
    #print "looking for "+ product.variants[0].sku + " in spreadsheet"
    for row_index in range(1,sheet.nrows):
        if int(sheet.cell(row_index,0).value) == int(product.variants[0].sku):
            if sheet.cell(row_index,2).value != product.variants[0].inventory_quantity:
                print "inventory change"
                print "found " + str(int(sheet.cell(row_index,2).value)) + " in store inventory : " + sheet.cell(row_index,1).value
                print "found " + str(product.variants[0].inventory_quantity) + " in shopify inventory : " + product.title
                print
                product.variants[0].inventory_quantity = int(sheet.cell(row_index,2).value)
                product.save()
                print "updated shopify "+ product.title
#
#for row_index in range(sheet.nrows):
#    if sheet.cell(row_index,2).value > 0 :
#        itemnum = (str(sheet.cell(row_index,0).value).split("."))[0]
#        print 'ItemNumber:' + str(itemnum)
#        print 'ItemName:' , sheet.cell(row_index,1).value
#        print 'Quantity:' , sheet.cell(row_index,2).value



