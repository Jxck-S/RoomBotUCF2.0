def print_response_str(rsp):
    if rsp.history:
        print("Redirected!")
        # Print information about each step in the redirection history
        for idx, redirect_response in enumerate(rsp.history, 1):
            print(f"Step {idx} - URL: {redirect_response.url}, Status Code: {redirect_response.status_code}\n")
    print("Final URL:", rsp.url)
    print("Final Status Code:", rsp.status_code)

