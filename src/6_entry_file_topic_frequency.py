import os
import read_document



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

        #STEP2: Extract questions from the documents
        directory_path="./question_papers_extracted_gpt_sectionwise"
        for filename in os.listdir(directory_path):
            print(f"  File: {filename}")
            file_path = os.path.join(directory_path, filename)
            output_filepath = os.path.join("./question_papers_topic_frequency"+"/", filename+".txt")
            if os.path.exists(output_filepath):
                print(f"File already present.")
            else:
                print(f"The file '{output_filepath}' does not exist.")
                if ".csv" in filename and os.path.isfile(file_path):
                    with open(file_path, 'r') as file:
                        content = file.read()
                        response = ai_client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "You are an intelligent assistant."},
                                {"role": "user", "content": "You are given a list of topics out of which some are similar in meaning. Please group these topics along with their freqencey. - "+content},
                            ],
                            temperature=0,
                        )
                        read_document.write_or_append_to_file(output_filepath, response.choices[0].message.content)
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
