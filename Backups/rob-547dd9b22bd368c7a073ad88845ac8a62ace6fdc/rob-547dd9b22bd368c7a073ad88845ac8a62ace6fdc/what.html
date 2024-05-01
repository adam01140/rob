<?php
    // Check if a PDF file is uploaded
    if(isset($_FILES['pdf_file'])) {
        $file_name = $_FILES['pdf_file']['name'];
        $file_tmp = $_FILES['pdf_file']['tmp_name'];

        // Move uploaded file to a temporary location
        move_uploaded_file($file_tmp, $file_name);

        // Execute pdftk command to dump form fields
        $output = shell_exec("pdftk $file_name dump_data_fields");

        // Parse the output to extract field names
        preg_match_all('/FieldName: (.+?)\n/', $output, $matches);

        // Output the extracted field names
        echo "<h2>Form Field Names:</h2>";
        echo "<ul>";
        foreach ($matches[1] as $field) {
            echo "<li>$field</li>";
        }
        echo "</ul>";

        // Remove the uploaded file
        unlink($file_name);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Form Field Extractor</title>
</head>
<body>
    <form action="" method="post" enctype="multipart/form-data">
        <input type="file" name="pdf_file" accept=".pdf">
        <input type="submit" value="Extract Form Fields">
    </form>
</body>
</html>
