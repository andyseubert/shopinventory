<?php
$dbhost = 'databasehostname';
$dbuser = 'zencart_database_user';
$dbpass = 'yes_the_password';

$conn = mysql_connect($dbhost, $dbuser, $dbpass) or die                      ('Error connecting to mysql');

$dbname = 'zencart_database_name';
mysql_select_db($dbname);

// make a csv file
$export="/full/path/to/resulting/export/file/inventory.csv"
?>
<HTML>
<title>Inventory Exporter</title>
<head>
<!--
<link rel="stylesheet" href="example.css" TYPE="text/css" MEDIA="screen">
<link rel="stylesheet" href="example-print.css" TYPE="text/css" MEDIA="print">

<script type="text/javascript" src="tabber.js"></script>
-->
</head> 
<body>

<?

$fh = fopen($export, 'w') or die("can't open file");

//echo php_uname('n');

$headers = "Handle,Title,Product Description,Vendor,Type,Tags,Published,Option1 Name,Option1 Value,Option2 Name,Option2 Value,Option3 Name,Option3 Value,Variant SKU,Variant Grams,Variant Inventory Tracker,Variant Inventory Qty,Variant Inventory Policy,Variant Fulfillment Service,Variant Price,Variant Compare At Price,Variant Requires Shipping,Variant Taxable,Variant Barcode,Image Src,Image Alt Text";

//echo "\n<table border=1>\n";

fwrite($fh, $headers);

// get the categories
$catQry="SELECT zen_categories.categories_id, zen_categories_description.categories_name, zen_categories_description.categories_id
FROM  `zen_categories` , `zen_categories_description` 
WHERE zen_categories.categories_id = zen_categories_description.categories_id";
$catResult=mysql_query($catQry);
// for each category, get the products 

$i=0;
	// put them in tabs
while ($row = mysql_fetch_array($catResult, MYSQL_BOTH)) {
	$catID=$row["categories_id"];
	$catNAME=$row["categories_name"];
	

	$query = "SELECT
		zen_products.products_status,
		zen_products.products_price,
		zen_products.products_image,
		zen_products.products_id,
		zen_products.products_weight,
		zen_products.products_sort_order,
		zen_products_description.products_name,
		zen_products_description.products_description,
		zen_products.products_quantity,
		zen_products.products_model,
		zen_products_to_categories.products_id,
		zen_products_to_categories.categories_id
	FROM `zen_products` , `zen_products_description`,   `zen_products_to_categories` 
	WHERE zen_products.products_id = zen_products_description.products_id
	AND zen_products.products_id = zen_products_to_categories.products_id
	AND zen_products_to_categories.categories_id = $catID
	AND zen_products.products_status !=0 
	ORDER BY zen_products.products_sort_order";

	$result=mysql_query($query);
	if (mysql_num_rows($result) >0 )
	{	
		$c=0;
		//echo "\n<div class=tabbertab title=".$catNAME.">\n"; 
		
		
		while ($data = mysql_fetch_array($result, MYSQL_BOTH)) { 
		// break up the long list. every 6 lines write the header row again
		//if (($c>1)&&($c % 6 == 1 )) {
		//	echo "$headers";
		//}
		// increment the count of ?
		//++$c;
		
		// get the image name like a path to get it without the extension (.jpg)
		$path_parts = pathinfo($data["products_image"]);
		
		// begin the csv values
		fwrite($fh, "\n");
$bodyhtml=$data["products_description"];
//$bodyhtml = htmlspecialchars($data["products_description"], ENT_QUOTES);
//$bodyhtml = str_replace(array("\r","\n"), "", $data["products_description"] );
$bodyhtml = str_replace(array("\""), "", $bodyhtml);
// stupid price
$price = str_replace("0","",$data["products_price"]);

$weight = $data["products_weight"] * 453.6 ;

$invLine =
	"".$data["products_name"].",".			//handle
	"".$data["products_name"].",".			//title
	"\"".$bodyhtml."\",".				//body(html)
	",".						//Vendor
	"".$catNAME.",".				//type
	"".$catNAME.",".				//tags
	"True,".					//Published
	",".						//option1 name
	",".						//option1 value
	",".						//option2 name
	",".						//option2 value
	",".						//option3 name
	",".						//option3 value
	"".$data["products_model"].",".			//Variant SKU
	$weight.",".					//variant grams
	"shopify,".					//variant inventory tracker
	$data["products_quantity"].",".			//variant inventory quantity
	"deny,".					//variant inventory policy
	"manual,".					//variant fulfillment service
	$price.",".					//variant price
	",".						//variant compare at price
	"True,".					//variant requires shipping
	"False,".					//variant taxable
	",".						//variant barcode
	"http://florapdx.com/images/large/".$path_parts['filename']."_LRG.jpg,".	//image src
	"";						// image alt text

fwrite($fh, $invLine);
?>
<!--
"<? echo $data["products_name"];?>","
<? echo $data["products_name"];?>","
<? $converted = htmlspecialchars($data["products_description"], ENT_QUOTES); echo $converted;?>","
","
","
<? echo $catNAME ?>","	
True","
","
","
","
","
","
","
<? echo $data["products_model"];?>","
<? echo ( $data["products_weight"] * 453.6 ); ?>","
<? echo $data["products_status"]; ?>","
<? echo $data["products_quantity"];?>","
",
","
<? echo $data["products_price"];?>","
","
True","
False","
","
http://florapdx.com/images/large/<? echo $path_parts['filename']; ?>_LRG.jpg",""
	
			<? ++$i; // count of items in this category?
		} 
		?> 
		<?
	}
}

fclose($fh);
?>
-->
<a href="http://yourdomain.com/link/to/the/exported/inventory.csv">Done. Pick up the file here</a>
<br />
</body>
</HTML>
