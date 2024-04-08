from typing import Type
from openai import OpenAI
from pydantic import BaseModel
import json

def extract_data_from_html_str(
        html: str,
        pydantic_model: Type[BaseModel],
        base_url: str = "https://openrouter.ai/api/v1",
        model_name: str = "cohere/command-r",

):
 
    client = OpenAI(
        base_url=base_url
    )


    response = client.chat.completions.create(
        model=model_name,
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system", 
                "content": """You are an expert in data extraction and JSON formatting.
                    Given a string containing data from an HTML component, your task is to extract the relevant information
                    and populate a JSON structure based on the fields defined in the provided Pydantic model.
                    Carefully analyze the HTML data to identify and extract the required fields, ensuring the data types
                    and structure match the Pydantic model. Your goal is to accurately fill out
                    the JSON structure to the best of your ability based on the available data. 
                    Make sure if you cant find a field in the data that you include a placeholder value "Not Found" in the JSON structure.
                    When populating the JSON structure, make sure to directly include the fields in the top-level dictionary
                    without using any nested names or additional levels. The fields should be directly accessible in the JSON
                    without any unnecessary nesting.
                    Do not include any other text than the JSON response. Do not return markdown format, only JSON and nothing else.""",
            },
            {
                "role": "user",
                "content": f"""Extract all the data from:  {html}
                    output it in the following format: {pydantic_model.model_json_schema()}
                """},
        ],
        tools=[
            {
                
            }
        ]
    )


    # print(f"""Extract all the data from:  {html}
    #             output it in the following format: {pydantic_model.model_json_schema()}
    #         """)
    # print("=====================================================")
    # print(response.choices[0].message.content)
    # print("=====================================================")
    # print(response.usage)
    # print("=====================================================")

    try:
        parsed_output = json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error extracting data from html string: {e}")
        return None

    try:
        if pydantic_model.__name__ in parsed_output:
            return pydantic_model(**parsed_output[pydantic_model.__name__])
        else:
            return pydantic_model(**parsed_output)
    except Exception as e:
        print(f"Error creating Pydantic model: {e}")
        return None