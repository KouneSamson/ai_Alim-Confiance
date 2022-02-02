<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "alim_confiance";

function check_accent($libelle)
{
	return  str_replace("'", "''", $libelle);
}


function remplir_activite_inspection($conn, $conn_alim){
	$sql = "SELECT numero_inspection, app_libelle_activite_etablissement, synthese_eval_sanit from jeu_de_donnes
				GROUP by numero_inspection, app_libelle_activite_etablissement, synthese_eval_sanit";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	while($row  = $resultats->fetch_assoc()){	
		$numero_inspection =$row['numero_inspection'];
		$nom_activite = $row['app_libelle_activite_etablissement'];
		$nom_activite = check_accent($nom_activite);
		$synthese = $row['synthese_eval_sanit'];
		$synthese = check_accent($synthese);
		
		$id_inspection = $conn_alim->query("select id_inspection from inspection where numero_inspection = '$numero_inspection'")->fetch_assoc()['id_inspection'];
		$id_activite = $conn_alim->query("select id_activite from activite where nom_activite = '$nom_activite'")->fetch_assoc()['id_activite'];
//		echo $id_inspection . " ,  " . $id_activite . " ,  " . $synthese ."<br>";
//		$rows_Number++;
		
		$sql = "insert into inspection_activite (id_inspection, id_activite, synthese_eval) values ('$id_inspection', '$id_activite', '$synthese')";
		if(!$conn_alim->query($sql))
		{
			echo "Add is not possible for - ". $id_activite."<br>";

		}
		else  
			$rows_Number++;
		
		
	}
	echo $rows_Number."<br>";
}

function remplir_add_geo($conn, $conn_alim){
	
	$sql = "SELECT  siret, adresse_2_ua, geores FROM jeu_de_donnes
			GROUP by siret, adresse_2_ua, geores ";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	while($row  = $resultats->fetch_assoc()){
		$siret = $row['siret'];
		$adress = $row['adresse_2_ua'];
		$adress = check_accent($adress);
		$geo = $row['geores'];
		$id_etablissement = $conn_alim->query("select id_etablissement  from etablissement where siret = '$siret'")->fetch_assoc()['id_etablissement'];
		
		$sql = "insert into add_geo (id_etablissement, adress, geo) values ('$id_etablissement', '$adress', '$geo')";
		if(!$conn_alim->query($sql))
		{
			echo "Add is not possible for - ". $id_etablissement."<br>";

		}
		else  
			$rows_Number++;
//		echo $id_etablissement. " ,  " . $adress. " ,   " .$geo . "<br>";
//		$rows_Number++;
	}
	
	echo $rows_Number. "<br>";
	
}


function remplir_inspection($conn, $conn_alim){
	$sql = "SELECT  numero_inspection, date_inspection FROM jeu_de_donnes 
			GROUP by numero_inspection, date_inspection";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	while($row  = $resultats->fetch_assoc()){
		$numero_inspection = $row['numero_inspection'];
		$date_inspection = $row['date_inspection'];
		
		$sql = "insert into inspection (numero_inspection, date_inspection) values('$numero_inspection', '$date_inspection')";
		echo $numero_inspection . "    " . $date_inspection . "<br>";
		
		if(!$conn_alim->query($sql))
		{
			echo "Add is not possible for - ". $nom_etablissement."<br>";

		}
		else  
			$rows_Number++;
	}
	echo $rows_Number. "<br>";
}

function remplir_etablissement_activite($conn, $conn_alim){
	
	$sql = "select distinct numero_inspection from jeu_de_donnes";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	while($row  = $resultats->fetch_assoc()){
		$numero_inspection = $row['numero_inspection'];
		$sql = "select siret, app_libelle_activite_etablissement, date_inspection,synthese_eval_sanit, agrement from jeu_de_donnes
		where numero_inspection = '$numero_inspection' ";
		$results_for_alim = $conn->query($sql);
		while($row_for_alim = $results_for_alim->fetch_assoc()){
			$siret = $row_for_alim['siret'];
			$nom_activite = $row_for_alim['app_libelle_activite_etablissement'];
//			$nom_etablissement = check_accent($nom_etablissement);
			$nom_activite = check_accent($nom_activite);
			$id_etablissement = $conn_alim->query("select id_etablissement from etablissement where siret = '$siret'")->fetch_assoc()['id_etablissement'];
			$id_activite = $conn_alim->query("select id_activite from activite where nom_activite = '$nom_activite'")->fetch_assoc()['id_activite'];
			$date_inspection = $row_for_alim['date_inspection'];
			$synthese_eval = $row_for_alim['synthese_eval_sanit'];
			$agrement = $row_for_alim['agrement'];
			
			echo $id_etablissement . " ,  ". $id_activite . " ,  ". $numero_inspection. " ,   " . $date_inspection . " ,   " . $synthese_eval . " ,   " . $agrement . "<br>";
		//	$rows_Number++;
			$sql = "insert into etablissement_activite (id_etablissement, id_activite, numero_inspection, date_inspection, synthese_eval, agrement)
			values('$id_etablissement', '$id_activite', '$numero_inspection', '$date_inspection', '$synthese_eval', '$agrement')";
			if(!$conn_alim->query($sql))
			{
				echo "Add is not possible for - ". $nom_etablissement."<br>";

			}
			else  
				$rows_Number++;
			
		}
		echo $rows_Number . '<br>';
	}
	echo $rows_Number . '<br>';

}

function remplir_activite($conn, $conn_alim){
	$sql = "SELECT DISTINCT app_libelle_activite_etablissement FROM jeu_de_donnes";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	while($row  = $resultats->fetch_assoc()){
		$activite = $row['app_libelle_activite_etablissement'];
		$activite = check_accent($activite);
		$sql = "insert into activite (nom_activite) values('$activite')";
		
		echo $activite . "<br>";
		if(!$conn_alim->query($sql))
		{
			echo "Add is not possible for - ". $nom_etablissement."<br>";

		}
		else  
			$rows_Number++;
	}
	
	echo $rows_Number ."<br>";
}

function remplir_etablissement_postal($conn, $conn_alim){
	$sql = "SELECT code_postal, siret from jeu_de_donnes GROUP by siret, Code_postal";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	while($row  = $resultats->fetch_assoc()){
		$siret = $row['siret'];
		$code_postal = $row['code_postal'];
		$id_postal = $conn_alim->query("select id_postal from postal where code_postal = '$code_postal'")->fetch_assoc()['id_postal'];
		$id_etablissement = $conn_alim->query("select id_etablissement from etablissement where siret = '$siret'")->fetch_assoc()['id_etablissement'];
		
		$sql = "insert into etablissement_postal (id_etablissement, id_postal) values('$id_etablissement', '$id_postal') ";
		echo $id_etablissement . '  ' . $id_postal . " ,    " . $rows_Number .'<br>';
		if(!$conn_alim->query($sql))
		{
			echo "Add is not possible for - ". $nom_etablissement."<br>";

		}
		else  
			$rows_Number++;
		
		//$rows_Number++;
	}
}



function remplir_etablissement($conn, $conn_alim){
	$sql = "select APP_Libelle_etablissement, siret from jeu_de_donnes
			group by siret";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	while($row  = $resultats->fetch_assoc()){
		$siret = $row['siret'];
		$nom_etablissement = $row['APP_Libelle_etablissement'];
		$nom_etablissement = check_accent($nom_etablissement);
		$sql = "insert into etablissement (siret, nom_etablissement) values('$siret', '$nom_etablissement')";
		
		if(!$conn_alim->query($sql))
		{
			echo "Add is not possible for - ". $nom_etablissement."<br>";

		}
		else  
			$rows_Number++;
	
		
	}
	echo "Nombre de lignes injectés est = $rows_Number <br>";
}

function remplir_commune($conn, $conn_alim){
	$sql = "select distinct Libelle_commune from jeu_de_donnes";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	while($row  = $resultats->fetch_assoc()){
		$sous_row = $row['Libelle_commune'];
		$sous_row = str_replace("'", "''", $sous_row);
		$sql = "insert into commune (nom_commune) values('$sous_row')";
		if(!$conn_alim->query($sql))
		{
//			echo "Add is done for - ". $sous_row."<br>";
			alert("$sous_row is not possible to add ..");
		}
		else
			$rows_Number++;
	
		
	}
	echo "Nombre de lignes injectés est = $rows_Number <br>";
}


function remplir_postal($conn, $conn_alim){
	$sql = "select libelle_commune, code_postal from jeu_de_donnes group by code_postal";
	$resultats = $conn->query($sql);
	$rows_Number = 0;
	
	while($row  = $resultats->fetch_assoc()){
		$code_postal = $row['code_postal'];
		$nom_commune = $row['libelle_commune'];
		$nom_commune = check_accent($nom_commune);
		$sql = "select id_commune from commune where nom_commune = '$nom_commune'";
	
		$res_id_commune = $conn_alim->query($sql);
		$id_commune = $res_id_commune->fetch_assoc()['id_commune'];
		
		$sql = "insert into postal (id_commune, code_postal) values('$id_commune', '$code_postal')";
		if(!$conn_alim->query($sql))
		{
			alert("is not possible to add ..");
		}
		else   
			$rows_Number++;
	
		
	}
	echo "Nombre de lignes injectés est = $rows_Number <br>";
}

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
$conn_alim = new mysqli($servername, $username, $password, "alim");
// Check connection
if ($conn->connect_error || $conn_alim->connect_error) 
  die("Connection failed: " . $conn->connect_error);
else
{
	echo "Connection à la BDD est fait .. <br>";
	//remplir_commune($conn, $conn_alim); // C'est deja fait 
	//remplir_postal($conn, $conn_alim);
	//remplir_etablissement($conn, $conn_alim);
	//remplir_etablissement_postal($conn, $conn_alim);
	//remplir_activite($conn, $conn_alim);	
	//remplir_etablissement_activite($conn, $conn_alim);
	//remplir_inspection($conn, $conn_alim);
	//remplir_add_geo($conn, $conn_alim);
	//remplir_activite_inspection($conn, $conn_alim);
}
?>