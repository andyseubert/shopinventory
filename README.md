shopinventory
=============

**This program will update shopify inventory from quickbooks Point Of Sale export csv file**

This takes an inventory spreadsheet which comes out of quickbooks Point Of Sale which is saved in dropbox as input.
The inventory items in your QBPOS have "Item Number"s which are matched up against shopify SKU numbers.

## required
*   python (duh)
*   shopify python lib <code>pip install shopify</code>
*   python dropbox lib <code>pip install dropbox</code>
*   dropbox dev account? https://www.dropbox.com/developers

   If you would like to use the app without creating your own dropbox dev account, then contact me. I will send you the dropbox_api configurations to put in the .config file

## Prepare
*   Open a shopify store and import your inventory. For this to work you must have SKUs in your shopify products.
*   If you're moving from zencart, put the php script called "allExport.php" on your zencart web server, configure it, and it will export into a csv which shopify can import.
*   Get yourself a dropbox account and install it on your POS computer.
*   Open POS and export your items to a .xls file with ONLY THREE COLUMNS
 * **Item Number, Item Name, Qty1** in that order
 * these are default column headings in POS so it should be no problem but you will want to create a template in POS so you can use it repeatedly.
*   Save the resulting file to your dropbox folder, note the path
 * put the path in the <code>inventory.config</code> file
*   get your shopify api_key and api_secret http://docs.shopify.com/support/configuration/apps/where-do-i-find-my-api-key
 * Put your shopify api stuff in the <code>inventory.config</code> file
 
## Run it
*   The first time the program runs, it will ask you to authorize it access to your store. Follow the instructions.
 * it will save the access_token in the <code>inventory.config</code> file itself, so be sure that happens.

## Schedule
* the POS export process is sadly entirely manual.
* Create a scheduled task to run the **inventory.py** on a regular basis so it "notices" when an inventory file is created and updates your shopify site without too much interaction on your part.

## inventoryArchiveCleaner.py
* deletes any files older than **max_age** setting found in the config file
* from the **archive_path** dropbox directory setting in the config file
* could be scheduled to run or maybe should be called from the inventory script at the end.

## TO-DOs
* the todos are in comments in the code.
