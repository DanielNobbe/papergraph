import requests

# Prepare the file to be uploaded

path = 'data/1910.09840v3.pdf'

files = {'file': open(path, 'rb')}

# Send the POST request to the FastAPI server
response = requests.post('http://127.0.0.1:8000/process/', files=files)

# Print the response from the server
output_file = 'output.json'

with open(output_file, 'w') as f:
    f.write(response.text)
