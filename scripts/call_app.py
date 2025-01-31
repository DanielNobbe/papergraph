# pylint: disable=C0103,
from argparse import ArgumentParser
import requests

# Prepare the file to be uploaded


def main(args):
    path = args.file

    with open(path, 'rb') as f:
        file_content = f.read()
        files = {'file': file_content}

        # Send the POST request to the FastAPI server
        if args.local:
            response = requests.post(
                f'http://localhost:{args.port}/process/',
                files=files
                timeout=600
            )
        else:
            endpoint = args.url + "/process"

            response = requests.post(
                endpoint,
                files=files,
                timeout=600
            )

        print(response.text)

        # Print the response from the server
        output_file = 'output.json'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--local",
        type=bool,
        help="Include to call local"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://papergraph-47463167639.europe-central2.run.app",
        help="Set remote url."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Set port for local mode."
    )
    parser.add_argument(
        "--file",
        type=str,
        default='data/2501.05409v2.pdf',
        help="Set file to process."
    )
    arguments = parser.parse_args()
    main(arguments)
