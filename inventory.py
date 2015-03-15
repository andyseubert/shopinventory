#! /usr/bin/python
from xlrd import open_workbook
from xlrd import cellname, cellnameabs, colname
import tempfile
import shopify
import ConfigParser
import os
import io
import dropbox
import webbrowser
from datetime import *
import subprocess
from subprocess import Popen
import sys
import unicodedata
import time

debug=1

# this string will be our log
report = "starting at " + str(datetime.now()) + "\n"

# todo: use try:catch to capture errors and email them to someone specified in the config file

# shopify API help from https://groups.google.com/forum/#!msg/shopify-app-discuss/U07XoBgN7eU/CIaaOlwOGaYJ
## read configuration from a file
## todo: add argument parsing for config file location
config = ConfigParser.ConfigParser(allow_no_value=True)
configFilePath = '/home/andys/shopinventory/inventory.config'
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
    ## dropbox stuff
    # 
    # get the app key and secret from the config file
    dropbox_app_key = config.get('dropbox','dropbox_app_key')
    dropbox_app_secret = config.get('dropbox','dropbox_app_secret')
    ## if there is no access token then prompt for access granting
    dropbox_access_token = config.get('dropbox','dropbox_access_token')
    archive_path = config.get('FileSection','archive_path')
    # email report settings
    report_to=config.get('report','send_to')
    report_from=config.get('report','send_from')
    report_user=config.get('report','username')
    report_pass=config.get('report','password')
    report_subject=config.get('report','subject')
    report_py_path=config.get('report','path_to_send_script')
    
except:
    print "something wrong reading " + configFilePath
    print Exception
    exit()

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
    ## save the access token to the config file for later re-use
    cfgfile = open(configFilePath,'w')    
    config.set('dropbox','dropbox_user_id',dropbox_user_id)
    config.set('dropbox','dropbox_access_token',dropbox_access_token)
    config.write(cfgfile)
    cfgfile.close()
    print "access token received and saved in " + configFilePath
    
# found the access_token either in the config or from the above auth action
client = dropbox.client.DropboxClient(dropbox_access_token)
report = report + 'connected to dropbox\n' + 'linked account name: ' + client.account_info()["display_name"] + "\n"
report = report + 'linked account email: ' +  client.account_info()["email"] + "\n"
if debug:
    print 'connected to dropbox'
    print 'linked account name: ', client.account_info()["display_name"]
    print 'linked account email: ', client.account_info()["email"]
    print

## store exported inventory file location retrieved from configuration
inventoryFile = config.get('FileSection','store_inventory_file')
report = report + "using QB POS inventory file: " + inventoryFile+"\n"
if debug:
    print "using QB POS inventory file: " + inventoryFile
# get the file from dropbox
# I guess you "get" the file by  writing its contents to a local file in order to use it
tempDir=tempfile.gettempdir()
tmpInventoryFile = tempDir+"/tempInventory.xls"
if debug:
    print "using temporary file at: " + tmpInventoryFile
    print
 
# check that the dropbox inventory file exists here
try:
    client.get_file(inventoryFile)
except:
    print "could not get POS inventory file " + inventoryFile + " from dropbox"
    print "done"
    exit()

# open temp file for writing
tfh = open(tmpInventoryFile,"wb")
# read dropbox file in and write it out to the temp file.
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
print tmpInventoryFile + " file OK"

## get the shopify action.
shopify.ShopifyResource.set_site(shop_url)
shop = shopify.Shop.current
if debug:
    print "connected to shopify shop " + storename
    print

# get all of the products
# get how many pages there are
pages = int(shopify.Product.count() / 50)+1
currentpage = 1
productscount = 0 
print "comparing inventory listings"
while currentpage <= pages:
	print "page nbr " + str(currentpage)
	products = shopify.Product.find(page=currentpage)
	# REAL ACTION HAPPENS IN THIS LOOP
	changecount=0
	for product in products:
		productscount = productscount +1
		productname = unicodedata.normalize('NFKD', product.title).encode('ascii','ignore')
		if not product.variants[0].sku:
			report = report + "online product sku missing for " + productname + "\n"
		else:   
			websku = product.variants[0].sku
			webqty = product.variants[0].inventory_quantity
			
			if not product.published_at:
				if debug > 1:
					print "*HIDDEN PRODUCT* SKU: " + websku + " " + productname + " id: >" + str(product.id) +"<"
					report = report + "*HIDDEN PRODUCT* SKU: " + websku + " " + productname + " id: >" + str(product.id) +"<\n"
			else:
				if debug >1:         
					#print product.attributes
					print "SKU: " + websku + " " + productname + " id: >" + str(product.id) +"<"
					report = report + "SKU: " + websku + " \'"+ productname + "\' id: >" + str(product.id) +"<\n"
				for row_index in range(1,sheet.nrows):
		## IF THERE IS A MATCH BETWEEN THE POS ITEM NUMBER AND THE SHOPIFY SKU
		# it means the item exists in both places
					if int(sheet.cell(row_index,0).value) == int(websku):
			## if the inventory quantities differ,
				# don't set to negative value please				
						if int(sheet.cell(row_index,2).value) < 0:
							storeqty = 0
						else:
							storeqty = int(sheet.cell(row_index,2).value)
							
						if int(storeqty) != int(webqty):
								
			## the POS is the authority
							report = report + "\n"
							report = report + productname + "\nonline inventory change\n"
							report = report + "xl SKU: " + str(storeqty) + "\n"
							report = report + "webSKU: " + str(websku) + "\n"
							report = report + "from " + str(webqty) + " in shopify inventory.\n"
							report = report + "to " + str(int(storeqty))+ "\n"
							if debug:
								print productname + "online inventory change"
								print "xl SKU: " + str(sheet.cell(row_index,0).value) 
								print "webSKU: " + str(websku) 
								print "from " + str(webqty) + " in shopify inventory. to " + str(int(storeqty))
			## set the shopify quantity to the POS quantity here  
							
							product.variants[0].inventory_quantity = storeqty
							result = product.save()
							print "result from API: " + str(result)
							
							## check it updated
							if int(product.variants[0].inventory_quantity) != int(storeqty):
								print "unable to update quantity"
								report = report + "unable to update online quantity for SKU: " + str(websku) + " " + productname
							else:
								print "confirmed quantity changed to " + str(product.variants[0].inventory_quantity)
								report = report + "confirming online qty changed to " + str(product.variants[0].inventory_quantity) + "\n"
								changecount +=1 
								
							report = report + "\n"
	currentpage = currentpage + 1
	#print "sleeping 2 seconds"
	#time.sleep(2)

# todo: log all changes to a file

# todo: send email report

# todo: move the inventory file to archive folder specified in config file
archive_name = str(datetime.now().strftime("%Y%m%d-%H%M%S"))+".xls"

## commented out until zencart is finished
client.file_move(inventoryFile,archive_path+"/"+ archive_name)
report = report + "archived at " + archive_path+"/"+ archive_name + "\n"

if debug:
    print "archived at " + archive_path+"/"+ archive_name
# todo: delete archive files older than days specified in config file
# done in inventoryArchiveCleaner.py script
if changecount==0:
    report = report + "\nno products updated\n"
    #exit()
else:
	report = report + str(changecount) + " products changed\n"

report = report + "total online product count: " + str(int(shopify.Product.count()))+"\n"
report = report + str(pages) + " pages of products\n"

report = report + str(productscount) + " products checked for inventory\n"
print str(productscount) + " products examined\n"
report = report + "finished at " + str(datetime.now()) + "\n"

#todo: email report to someone
emailto   = "-t " + report_to
emailfrom = "-f " + report_from
emailuser = "-u " + report_user
emailpass = "-p " + report_pass
emailsubj = "-s " + report_subject
emailbody = "-b " + report


subprocess.Popen([sys.executable, report_py_path, emailto,emailfrom,emailuser,emailpass,emailsubj,emailbody])


print
print "done"

