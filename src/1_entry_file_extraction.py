import os
import read_document
import time

if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv
    from openai import AzureOpenAI
    import os
    load_dotenv()

    deployment_name = os.environ['COMPLETIONS_MODEL']

    # The API key for your Azure OpenAI resource.
    api_key = os.environ["AZURE_OPENAI_API_KEY"]

    # The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
    azure_endpoint = os.environ['AZURE_OPENAI_ENDPOINT']

    # Currently OPENAI API have the following versions available: 2022-12-01
    api_version = os.environ['OPENAI_API_VERSION']

    ai_client = AzureOpenAI(
    api_key=api_key,  
    azure_endpoint=azure_endpoint,
    api_version=api_version
    )
    try:
        load_dotenv(find_dotenv())

        #STEP1: Extract text from the documents
        for root, dirs, files in os.walk("./data/"):
            print(f"Current Directory: {root}")
            for dir_name in dirs:
                print(f"  Directory: {dir_name}")
                #fetch files from dir_name directory
                for entry in os.listdir(root+"/"+dir_name):
                    if "DS_Store" not in entry: 
                        file_name = os.path.join(dir_name, entry)
                        print(f"  File: {file_name}")
                        #Input file path
                        file_path = os.path.join(root+"/"+dir_name, entry)
                        output_filepath = os.path.join(root+"1_extraction"+"/"+dir_name, entry)
                        # Check if the file was modified in the last minute (60 seconds)
                        if not os.path.exists(output_filepath):
                            read_document.analyze_read(file_path,output_filepath)

    except HttpResponseError as error:
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
