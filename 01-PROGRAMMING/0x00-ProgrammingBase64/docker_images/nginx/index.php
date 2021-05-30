<?php
session_start();

$FLAG = "FLAG{e9a25db06f}";
$CHALLENGE_TITLE = "Programming Base64";
$NUM_SECONDS = 3;

$CHALLENGE_DESCRIPTION = "Encode the following string as base64.<br>";
$CHALLENGE_DESCRIPTION .= "You have $NUM_SECONDS seconds to send your reply to:<br>";


//This is the encoding function that the user needs to perform.
//This specific function will be run against the stored challenge
//data and compared to the user's submission. i.e.:
//if($_GET['answer']==encode($_SESSION['data']) then $found = true;
function encode($data) {
	return base64_encode($data);
}

//This is the string presented in the challenge's data box.
//Modifiy as needed and just return your raw challenge string.
function generate() {
	//Get some random data
	$bytes = openssl_random_pseudo_bytes(80);
	$output = bin2hex($bytes);
	return $output;
}

$found = false;

?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title><?php echo $CHALLENGE_TITLE; ?></title>
  <style>

    .description {
      border: 1px solid black;
      padding: 10px;
      font-size: 14px;
      font-style: normal;
      font-variant: normal;
      font-weight: 400;
      line-height: 20px;
    }

    .data {
      border: 1px solid black;
      padding: 10px;
      font-family: monospace;
      font-size: 14px;
      font-style: normal;
      font-variant: normal;
      font-weight: 400;
      line-height: 20px;
    }

  </style>
  <?php
    //Do we have saved session data and a submission?
    if(isset($_SESSION['data']) and isset($_GET['answer'])){
	    $found = (encode($_SESSION['data']) == $_GET['answer']) ? true : false;
	    //did they find it fast enough?
	    $t0 = $_SESSION['time'];
	    $t1 = time();
	    if($t1 - $t0 > $NUM_SECONDS) {
	    	$found = false;
	    }
    }
	$_SESSION['data'] = generate();

  ?>
</head>
<body>
<!-- Challenge Description -->
<p class="description">
  <?php echo $CHALLENGE_DESCRIPTION; ?>
  <strong><?php echo 'http://'. $_SERVER['SERVER_NAME'] . $_SERVER['SCRIPT_NAME'] . '?answer=YOURANSWER'; ?></strong>
</p>
<!-- End Challenge Description -->
<!-- Challenge Data -->
<p class="data"><?php 
    if($found) {
    	echo $FLAG;
    } else {
	    echo $_SESSION['data']; 
	    $_SESSION['time'] = time();
    }
?></p>
<!-- End Challenge Data -->
</body>
</html>

