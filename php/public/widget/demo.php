<?php
/**
 * Widget Demo Page
 * Interactive testing environment for the widget
 */

require_once '../config/settings.php';
require_once '../includes/utils.php';

$page_title = "Sanctum Chat Widget - Interactive Demo";
$demo_content = file_get_contents('templates/widget_demo.html');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($page_title); ?></title>
    <link rel="stylesheet" href="assets/css/widget.css">
</head>
<body>
    <?php echo $demo_content; ?>
    <script src="assets/js/chat-widget.js"></script>
</body>
</html>
