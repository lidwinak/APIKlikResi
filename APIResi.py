import requests
import json
import os
from dotenv import load_dotenv

def get_klikresi_tracking_info(api_key: str, tracking_number: str, courier_code: str):
    base_url = "https://klikresi.com/api/trackings"
    url = f"{base_url}/{tracking_number}/couriers/{courier_code}"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
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

    YOUR_API_KEY = os.getenv("KLIKRESI_API_KEY")
    YOUR_TRACKING_NUMBER = os.getenv("TRACKING_NUMBER") 
    YOUR_COURIER_CODE = os.getenv("COURIER_CODE")  
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
            data_to_take = tracking_data
            if data_to_take['data']['status'] == 'Delivered':
                origin_contact_name_dlvrd = data_to_take['data']['origin']['contact_name']
                origin_address_dlvrd = data_to_take['data']['origin']['address']
                
                dest_contact_name_dlvrd = data_to_take['data']['destination']['contact_name']
                dest_address_dlvrd = data_to_take['data']['destination']['address']

                data_to_take['data']['histories'][0]
                from datetime import datetime

                datetime_string = data_to_take['data']['histories'][0]['date']
                
                if 'T' in datetime_string:
                    parts = datetime_string.split('T')
                    date_str_part = parts[0]
                    time_str_part_with_offset = parts[1]

                    # If you want to remove the timezone offset from the time string:
                    time_str_part = time_str_part_with_offset.split('+')[0] if '+' in time_str_part_with_offset else \
                                    time_str_part_with_offset.split('-')[0] if '-' in time_str_part_with_offset[1:] else \
                                    time_str_part_with_offset # Handles negative offsets and cases without offset
                    print(f'Barang telah berhasil sampai di tujuan pada {date_str_part} jam {time_str_part}. Barang dikirim dari {origin_contact_name_dlvrd}, {origin_address_dlvrd} untuk tujuan {dest_contact_name_dlvrd}, {dest_address_dlvrd}')
                else:
                    print("\n'T' separator not found in the datetime string for string splitting method.")
                
            elif data_to_take['data']['status'] == 'InTransit':
                origin_contact_name_intransit= data_to_take['data']['origin']['contact_name']
                origin_address_intransit= data_to_take['data']['origin']['address']
                
                dest_contact_name_intransit= data_to_take['data']['destination']['contact_name']
                dest_address_intransit= data_to_take['data']['destination']['address']

                data_to_take['data']['histories'][0]
                from datetime import datetime

                datetime_string = data_to_take['data']['histories'][0]['date']
                message_intransit = data_to_take['data']['histories'][0]['message']
                if 'T' in datetime_string:
                    parts = datetime_string.split('T')
                    date_str_part = parts[0]
                    time_str_part_with_offset = parts[1]

                    # If you want to remove the timezone offset from the time string:
                    time_str_part = time_str_part_with_offset.split('+')[0] if '+' in time_str_part_with_offset else \
                                    time_str_part_with_offset.split('-')[0] if '-' in time_str_part_with_offset[1:] else \
                                    time_str_part_with_offset # Handles negative offsets and cases without offset
                    print(f'Barang sedang dalam pengiriman dengan status akhir: {message_intransit} \nBarang dikirim dari {origin_contact_name_intransit}, {origin_address_intransit} untuk tujuan {dest_contact_name_intransit}, {dest_address_intransit}')
                else:
                    print("\n'T' separator not found in the datetime string for string splitting method.")
            else:
                print('no data')          
        
        elif tracking_data:
            print("\n--- Error Fetching Tracking Information ---")
            print(json.dumps(tracking_data, indent=4))
        else:
            print("\nBarang belum diterima dari ekspedisi.")