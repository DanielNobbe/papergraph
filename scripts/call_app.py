import requests

# Prepare the file to be uploaded

path = 'data/2501.05409v2.pdf'

files = {'file': open(path, 'rb')}

# Send the POST request to the FastAPI server
# response = requests.post('http://localhost:8000/process/', files=files)

response = requests.post('https://papergraph-47463167639.europe-central2.run.app/process', files=files)

print(response.text)

# Print the response from the server
output_file = 'output.json'

with open(output_file, 'w') as f:
    f.write(response.text)
