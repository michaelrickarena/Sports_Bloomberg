Write-Output "Building lambda distribution package..."
mkdir -Force dist

#copy all of src into dist
Copy-Item -Path src -Destination dist -Recurse -Force

#remove pychaches, and visualizations folder
Remove-Item -Recurse -Force -Path dist\src\visualizations, dist\src\__pycache__, dist\src\data\__pycache__, dist\src\utils\__pycache__

# copy package binaries into dist
Copy-Item -Recurse -Path pkg\* -Destination dist -Force

# copy app.py (__main__.py)
Copy-Item -Path app.py -Destination dist -Force

#move init into root
Move-Item -Path dist\src\__init__.py -Destination dist -Force

# Zip the dist folder
$zipFilePath = "dist.zip" 
Compress-Archive -Path dist\* -DestinationPath $zipFilePath -Force

Write-Output "Lambda distribution package zipped as $zipFilePath"

# Deploy to AWS Lambda
$functionName = "db_update"
aws lambda update-function-code --function-name $functionName --zip-file fileb://$zipFilePath --region us-east-2

Write-Output "Lambda function $functionName updated successfully."