shopinventory
=============

**This program will update shopify inventory from quickbooks Point Of Sale export csv file**

## required
python (duh)
shopify python lib <code>pip install shopify</code>
python dropbox lib <code>pip install dropbox</code>

This takes an inventory spreadsheet which comes out of quickbooks Point Of Sale which is saved in dropbox as input.
The inventory items in your QBPOS have "Item Number"s which are matched up against shopify SKU numbers.

## Prepare
*   Open a shopify store and import your inventory. For this to work you must have SKUs in your shopify products.
*   If you're moving from zencart, put the php script called "allExport.php" on your zencart web server, configure it, and it will export into a csv which shopify can import.
*   Get yourself a dropbox account and install it on your POS computer.
*   Open POS and export your items to a .csv file with ONLY THREE COLUMNS named **Item Number, Item Name, Qty1** in that order.
*   Save the resulting file to your dropbox folder, note the path
*   
*   




