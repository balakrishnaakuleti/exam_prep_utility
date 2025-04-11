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
        #STEP1: Extract questions from the documents

        sections = ["A","B","C"]
        prompt ={"A": """The first field month and year is fixed and is shown in example itself. Help by extracting the four questions numbered 1, 2,3 and 4. CSV file should only have the content rows and not even the header row. DO NO ADD ANY ADDITIONAL TEXT. Do not add additional text or fields since this is a CSV. 
    Strictly follow thye provided csv format. The content is provided below-

""", 
    
    "B": """The first field month and year is fixed and is shown in example itself. Help by extracting the five questions numbered 5, 6,7,8 and 9. CSV file should only have the content rows and not even the header row. DO NO ADD ANY ADDITIONAL TEXT. Do not add additional text or fields since this is a CSV. 
    Strictly follow thye provided csv format. The content is provided below-
""",
 "C": """The first field month and year is fixed and is shown in example itself. Help by extracting the three questions numbered 10, 11 and 12. The questions might be just a phrase. CSV file should only have the content rows and not even the header row. DO NO ADD ANY ADDITIONAL TEXT. Do not add additional text or fields since this is a CSV. 
    Strictly follow thye provided csv format. The content is provided below-


"""}
        for section in sections:
            for root, dirs, files in os.walk("./1_extraction/"):
                print(f"Current Directory: {root}")
                for dir_name in dirs:
                    print(f"  Directory: {dir_name}")
                    #fetch files from dir_name directory
                    for entry in os.listdir(root+"/"+dir_name):
                        if "DS_Store" not in entry and any(item in  dir_name for item in ['21','22','23','46']):
                            file_name = os.path.join(dir_name, entry)
                            print(f"  File: {file_name}")
                            #Input file path
                            file_path = os.path.join(root+"/"+dir_name, entry)
                            output_filepath = os.path.join(root+"2_extraction_sectionwise"+"/", dir_name+"_"+section+".csv")
                            is_hot_file = False
                            if not os.path.exists(output_filepath):
                                is_hot_file = True
                            else:
                                with open(output_filepath, 'r') as file:
                                    content = file.read()
                                    if len(content)<5:
                                        is_hot_file=True
                                current_time = time.time()
                                # Get the last modified time of the file
                                file_mod_time = os.path.getmtime(output_filepath)
                                if current_time - file_mod_time < 300:
                                    print(f"The file '{output_filepath}' was modified in the last 5 minute.")
                                    is_hot_file=True
                            if (is_hot_file):
                                print(f"The file '{output_filepath}' does not exist. Or it is being processed now for appending.")
                                if "MPC" in file_path and os.path.isfile(file_path):
                                    time.sleep(1)
                                    month_year = file_name.split(" - ")[1].split(".PDF")[0].split(".")[0]
                                    print("Month and Year",month_year)
                                    with open(file_path, 'r') as file:
                                        content = file.read()
                                        if section == "C":
                                            content = content.split("2×3")[1]
                                        if section == "B":
                                            content = (content.split("4×6")[1]).split("2×3")[0]
                                        if section == "A":
                                            content = (content.split("2×10")[1]).split("4×6")[0]
                                        response = ai_client.chat.completions.create(
                                            model="gpt-4",
                                            messages=[
                                                {"role": "system", "content": "You are an intelligent assistant."},
                                                {"role": "user", "content": """You are an intelligent assist who will provide the extracted questions in CSV from a question paper content provided. Format of the output CSV which has 3 fields separated by commas is:
Format:
Month Year, “Question”,”Topic”
Example extracted questions CSV:
"""+month_year+""",”Discuss the characteristics and types of hazards during early childhood.","early childhood hazards"

Question should always be enclosed in double quotes and should be STRICTLY IN ONE LINE without any serial numbers. Topic should be enclosed in double quotes and the topic should not be high level like the subject name. examples for topic names are: { question:Critically evaluate Sternberg's information processing approach , topic:Sternberg's information processing , question:Define Creativity. Explain the measurement of creativity, topic: Creativity }. """+prompt[section]+"""
    Content:
    """+content

    },
                                            ],
                                            temperature=0,
                                        )
                                        print("Content",response.choices[0].message.content)
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
