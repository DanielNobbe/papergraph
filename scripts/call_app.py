import requests

# Prepare the file to be uploaded

path = 'data/2410.07959v1.pdf'

files = {'file': open(path, 'rb')}

# Send the POST request to the FastAPI server
response = requests.post('http://localhost:8000/process/', files=files)

# Print the response from the server
output_file = 'output.json'

with open(output_file, 'w') as f:
    f.write(response.text)
