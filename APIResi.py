import requests
import json
import os
from dotenv import load_dotenv

def get_klikresi_tracking_info(api_key: str, tracking_number: str, courier_code: str):
    """
    Fetches real-time tracking information from the KlikResi API.

    Args:
        api_key (str): Your API key obtained from klikresi.com.
        tracking_number (str): The airwaybill (AWB) number of the shipment.
        courier_code (str): The code for the courier (e.g., 'jne' for JNE).

    Returns:
        dict: A dictionary containing the tracking information if successful,
              otherwise a dictionary with an 'error' key.
    """
    base_url = "https://klikresi.com/api/trackings"
    url = f"{base_url}/{tracking_number}/couriers/{courier_code}"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
        return {"error": f"HTTP error: {http_err}", "details": response.text}
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return {"error": f"Connection error: {conn_err}"}
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return {"error": f"Timeout error: {timeout_err}"}
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
        return {"error": f"An unexpected error occurred: {req_err}"}
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err} - Response text: {response.text}")
        return {"error": f"Failed to decode JSON response: {json_err}", "raw_response": response.text}

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # --- IMPORTANT ---
    # Retrieve your API key from environment variables
    # Make sure you have a .env file in the same directory as this script
    # with a line like: KLIKRESI_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
    YOUR_API_KEY = os.getenv("KLIKRESI_API_KEY")

    YOUR_TRACKING_NUMBER = os.getenv("TRACKING_NUMBER") # e.g., "000000000000"
    YOUR_COURIER_CODE = os.getenv("COURIER_CODE")  # e.g., "jne", "pos", "tiki"

    if YOUR_API_KEY is None:
        print("Error: KLIKRESI_API_KEY not found in environment variables.")
        print("Please create a .env file in the same directory as this script with:")
        print("KLIKRESI_API_KEY=\"YOUR_ACTUAL_API_KEY_HERE\"")
        print("And make sure to replace 'YOUR_ACTUAL_API_KEY_HERE' with your API key from https://klikresi.com/.")
    else:
        print(f"Attempting to fetch tracking info for AWB: {YOUR_TRACKING_NUMBER} with courier: {YOUR_COURIER_CODE}...")
        tracking_data = get_klikresi_tracking_info(
            api_key=YOUR_API_KEY,
            tracking_number=YOUR_TRACKING_NUMBER,
            courier_code=YOUR_COURIER_CODE
        )

        if tracking_data and "error" not in tracking_data:
            print("\n--- Tracking Information ---")
            print(json.dumps(tracking_data, indent=4))
        elif tracking_data:
            print("\n--- Error Fetching Tracking Information ---")
            print(json.dumps(tracking_data, indent=4))
        else:
            print("\nNo tracking data received or an unknown error occurred.")
