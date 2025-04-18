<?php
header('Content-Type: text/html; charset=utf-8');
// Disable caching for this page
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: 0');

// Get environment information
$hostname = gethostname();
$serverAddr = $_SERVER['SERVER_ADDR'] ?? 'Not available';

// Determine availability zone based on IP address
$availabilityZone = 'Not available';
if (strpos($serverAddr, '10.0.1') === 0 || strpos($serverAddr, '10.0.15') === 0) {
    $availabilityZone = 'us-east-1a';
} elseif (strpos($serverAddr, '10.0.2') === 0 || strpos($serverAddr, '10.0.24') === 0) {
    $availabilityZone = 'us-east-1b';
} else {
    $availabilityZone = 'Unknown';
}

// Generate a unique identifier for this instance
$instanceId = substr(md5($hostname . $serverAddr), 0, 8);

// Add a timestamp to prevent caching
$timestamp = time();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>PHP Hello World - AWS Fargate</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            text-align: center;
            max-width: 800px;
            width: 90%;
        }
        h1 {
            color: #232f3e;
            margin-bottom: 1rem;
        }
        .aws-orange {
            color: #ff9900;
        }
        .info {
            background-color: #f8f8f8;
            border-radius: 4px;
            padding: 1rem;
            margin-top: 2rem;
            text-align: left;
        }
        .info h2 {
            margin-top: 0;
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: bold;
            margin-left: 0.5rem;
            font-size: 0.9rem;
        }
        .badge-az-a {
            background-color: #e6f7ff;
            color: #0070a8;
            border: 1px solid #0070a8;
        }
        .badge-az-b {
            background-color: #fff2e6;
            color: #ff6600;
            border: 1px solid #ff6600;
        }
        .badge-unknown {
            background-color: #f0f0f0;
            color: #666;
            border: 1px solid #666;
        }
        .instance-id {
            font-family: monospace;
            background-color: #f0f0f0;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-size: 0.9rem;
        }
        .refresh-note {
            margin-top: 2rem;
            font-style: italic;
            color: #666;
        }
        .refresh-button {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background-color: #ff9900;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            text-decoration: none;
        }
        .refresh-button:hover {
            background-color: #e68a00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello World from <span class="aws-orange">PHP</span> on AWS Fargate!</h1>
        <p>This page is served from a PHP container running on AWS Fargate
            <?php 
            $badgeClass = 'badge-unknown';
            if ($availabilityZone === 'us-east-1a') {
                $badgeClass = 'badge-az-a';
            } elseif ($availabilityZone === 'us-east-1b') {
                $badgeClass = 'badge-az-b';
            }
            ?>
            <span class="badge <?php echo $badgeClass; ?>">
                <?php echo $availabilityZone; ?>
            </span>
        </p>
        <p>Instance ID: <span class="instance-id"><?php echo $instanceId; ?></span></p>
        
        <div class="info">
            <h2>Environment Information:</h2>
            <ul>
                <li>Hostname: <?php echo $hostname; ?></li>
                <li>IP Address: <?php echo $serverAddr; ?></li>
                <li>PHP Version: <?php echo phpversion(); ?></li>
                <li>Server Date and Time: <?php echo date('Y-m-d H:i:s'); ?></li>
                <li>User Agent: <?php echo $_SERVER['HTTP_USER_AGENT'] ?? 'Not available'; ?></li>
                <li>Client IP: <?php echo $_SERVER['REMOTE_ADDR'] ?? 'Not available'; ?></li>
                <?php if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])): ?>
                <li>X-Forwarded-For: <?php echo $_SERVER['HTTP_X_FORWARDED_FOR']; ?></li>
                <?php endif; ?>
                <?php if (isset($_SERVER['HTTP_CLOUDFRONT_VIEWER_COUNTRY'])): ?>
                <li>Visitor Country (CloudFront): <?php echo $_SERVER['HTTP_CLOUDFRONT_VIEWER_COUNTRY']; ?></li>
                <?php endif; ?>
                <li>Page Timestamp: <?php echo $timestamp; ?></li>
            </ul>
        </div>
        
        <p class="refresh-note">Refresh the page to see if you are redirected to an instance in a different availability zone.</p>
        <a href="?t=<?php echo $timestamp; ?>" class="refresh-button">Refresh Page</a>
    </div>
</body>
</html>
