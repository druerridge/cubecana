param(
    [Parameter(Position=0, Mandatory=$false)]
    [string]$uri
)

# Read the JSON file content
$jsonContent = Get-Content -Path ".\test_data\test_draft_log.json" -Raw

# Set headers for JSON content
$headers = @{
    "Content-Type" = "application/json"
}

try {
    # Make the POST request
    Write-Host "Sending POST request to: $uri"
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $jsonContent -Headers $headers
    
    Write-Host "Response received:"
    $response | ConvertTo-Json -Depth 10
}
catch {
    Write-Error "Failed to send request: $($_.Exception.Message)"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Status Description: $($_.Exception.Response.StatusDescription)"
}