<?php

//error_reporting(0);

if(!array_key_exists('HTTP_X_GITHUB_EVENT', $_SERVER))
{
	throw new Exception( 'Missing X-GitHub-Event header.');
}

if(!array_key_exists('REQUEST_METHOD', $_SERVER) || $_SERVER['REQUEST_METHOD'] !== 'POST')
{
	throw new Exception( 'Invalid request method.');
}

if(!array_key_exists('CONTENT_TYPE', $_SERVER))
{
	throw new Exception('Missing content type.');
}

$ContentType = $_SERVER['CONTENT_TYPE'];

if($ContentType === 'application/x-www-form-urlencoded')
{
	if(!array_key_exists('payload', $_POST))
	{
		throw new Exception('Missing payload.');
	}
	
	$raw = filter_input(INPUT_POST, 'payload');
}
else if($ContentType === 'application/json')
{
	$raw = file_get_contents('php://input');
}
else
{
	throw new Exception('Unknown content type.');
}

$payload = json_decode($raw);

if($payload === null)
{
	throw new Exception('Failed to decode JSON: ' .
		function_exists('json_last_error_msg') ? json_last_error_msg() : json_last_error()
	);
}

if(!isset($payload))
{
	throw new Exception('Missing repository information.');
}

if ($payload->ref === 'refs/heads/master')
{
	$modified = [];
	
	foreach ($payload->commits as $commit)
	{
		foreach ($commit->added as $file)
		{
			$modified[$file] = true;			
		}
		
		foreach ($commit->modified as $file)
		{
			$modified[$file] = true;			
		}
	}
	
	foreach ($modified as $key => $item)
	{
		 `echo {$key} >> /root/netkan.hook`;
	}
}

echo "Thanks!";

?>
