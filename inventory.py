
from xlrd import open_workbook
from xlrd import cellname, cellnameabs, colname
import tempfile
import shopify
import ConfigParser
import os
import io
import dropbox
import webbrowser
# todo: use try:catch to capture errors and email them to someone specified in the config file

# shopify API help from https://groups.google.com/forum/#!msg/shopify-app-discuss/U07XoBgN7eU/CIaaOlwOGaYJ
## read configuration from a file
## todo: add argument parsing for config file location
config = ConfigParser.ConfigParser(allow_no_value=True)
configFilePath = 'c:\\Users\\andys\\Dropbox\\shopify\\inventory.config'
if not os.path.isfile(configFilePath):
    print "config file " + configFilePath + " not found"
    exit()
try:
    config.read(configFilePath)
    # shopify configurations
    #URL Format	https://apikey:password@hostname/admin/resource.json
    #Example URL	https://cc9fa84b4d3d05b7f2256f7913b66272:0192638aacc90d3ebfe7168b9d77f1d0@flora-60.myshopify.com/admin/orders.json
    ## get shopify config options
    api_key=config.get('shopify','api_key')
    api_pass=config.get('shopify','api_pass')
    storename=config.get('shopify','storename')
    shop_url = "https://"+api_key+":"+api_pass+"@"+storename+".myshopify.com/admin"

except:
    print "something wrong reading " + configFilePath
    print Exception

## dropbox stuff
# 
# get the app key and secret from the config file
dropbox_app_key = config.get('dropbox','dropbox_app_key')
dropbox_app_secret = config.get('dropbox','dropbox_app_secret')
## if there is no access token then prompt for access granting
dropbox_access_token = config.get('dropbox','dropbox_access_token')
if not dropbox_access_token:
    print "no dropbox token found"
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(dropbox_app_key, dropbox_app_secret)
    authorize_url = flow.start()
    print '******'
    print 'Now I will open a dropbox web page in your web browser.'
    print 'Click "Allow" on that page (you might have to log in first)'
    print 'Copy the authorization code.'
    print 'Return here once you have copied it to the clipboard'
    tmp=raw_input("--->push Enter when ready...")
    webbrowser.open(authorize_url)
    print 'right-click to paste'
    code = raw_input("paste the authorization code here: ").strip()
    # This will fail if the user enters an invalid authorization code
    dropbox_access_token, dropbox_user_id = flow.finish(code)
    
    cfgfile = open(configFilePath,'w')
    
    config.set('dropbox','dropbox_user_id',dropbox_user_id)
    config.set('dropbox','dropbox_access_token',dropbox_access_token)
    config.write(cfgfile)
    cfgfile.close()
    print "access token received and saved"
    
# found the access_token either in the config or from the above auth action
client = dropbox.client.DropboxClient(dropbox_access_token)
print 'connected to dropbox'
print 'linked account name: ', client.account_info()["display_name"]
print 'linked account email: ', client.account_info()["email"]
print

## store exported inventory file location retrieved from configuration
inventoryFile = config.get('FileSection','store_inventory_file')
print "using POS inventory file: " + inventoryFile
# get the file from dropbox
# I guess you "get" the file and write its contents to a local file in order to use it
tempDir=tempfile.gettempdir()
tmpInventoryFile = tempDir+"\\tempInventory.csv"
print "using temporary file at: " + tmpInventoryFile
print

tfh = open(tmpInventoryFile,"wb")
with client.get_file(inventoryFile) as f:
    tfh.write(f.read())
tfh.close()
print "opening temporary file with excel reader"
## open excel sheet
book = open_workbook(tmpInventoryFile)
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
print "inventory csv OK"

## get the shopify action.
shopify.ShopifyResource.set_site(shop_url)
shop = shopify.Shop.current
print "connected to shopify"
print

# get all of the products
# todo: limit products by something?
products = shopify.Product.find()
# REAL ACTION HAPPENS IN THIS LOOP
print "comparing inventory listings"
for product in products:
    #print str(product.variants[0].inventory_quantity) + " " + product.title + " >" + product.variants[0].sku +"<"
    #print "looking for "+ product.variants[0].sku + " in spreadsheet"
    for row_index in range(1,sheet.nrows):
## IF THERE IS A MATCH BETWEEN THE POS ITEM NUMBER AND THE SHOPIFY SKU
# it means the item exists in both places
        if int(sheet.cell(row_index,0).value) == int(product.variants[0].sku):
## if the inventory quantities differ,
            if sheet.cell(row_index,2).value != product.variants[0].inventory_quantity:
## in this code, the POS is the authority
                print "inventory change"
                print "found " + str(int(sheet.cell(row_index,2).value)) + " in store inventory : " + sheet.cell(row_index,1).value
                print "found " + str(product.variants[0].inventory_quantity) + " in shopify inventory : " + product.title
                print
## set the shopify quantity to the POS quantity here                
                product.variants[0].inventory_quantity = int(sheet.cell(row_index,2).value)
                product.save()
                print "updated shopify "+ product.title

# todo: log all changes to a file

# todo: send email report

# todo: move the inventory file to archive folder specified in config file

# todo: delete archive files older than days specified in config file



print
print "done"