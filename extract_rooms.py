import js2py
import re
import json
import requests

# The room JSON info is inside the HTML page inside embedded JavaScript

def get_room_info():
    url = "https://ucf.libcal.com/spaces"  # Replace with the URL of the web page you want to retrieve

    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
    html_content = response.text
    # Use regular expression to find all script tags
    # Use regular expression to find the JavaScript code between var resources = []; and var paginatedResources =
    pattern = re.compile(r'(var resources = \[\];.*?)(var paginatedResources = |<\/script>)', re.DOTALL)
    match = pattern.search(html_content)

    if match:
        javascript_code = match.group(1).strip()



    if javascript_code:
        # Wrap the code in a function for better compatibility
        wrapped_code = f"""
            function parseResources() {{
                {javascript_code}
                return resources;
            }}
        """

        # Use js2py to execute the wrapped JavaScript code in a Python context
        context = js2py.EvalJs()
        context.execute(wrapped_code)

        # Convert the JsObjectWrapper to a standard Python dictionary
        resources_list = context.parseResources().to_dict()



        # Print the resulting JSON
        for idx, room_info in resources_list.items():
            # Extract the room number from the title
            match = re.search(r'Room (\d+\w*)', room_info['title'])
            if match:
                extracted_room_number = match.group(1)
                room_info['extracted_room_number'] = extracted_room_number

        return resources_list

    else:
        print("No script tags found in the HTML.")
        return None