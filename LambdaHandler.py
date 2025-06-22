import requests
import json
import os

# --- Corrected Function Definition ---
def dataprocessing(tracking_data):
    """
    Processes tracking data, prints it (for debugging), and returns it as a Python dictionary.
    Handles cases with and without 'error_status'.
    """
    if tracking_data and "error_status" not in tracking_data:
        # Print the data for debugging/visibility
        print(json.dumps(tracking_data, indent=4))
        # Return the data as a dictionary directly
        validated_data = tracking_data
    elif tracking_data and "error_status":
        # Print the error data for debugging/visibility
        print(json.dumps(tracking_data, indent=4))
        # Return the data as a dictionary directly
        validated_data = tracking_data
    else:
        print("\nNo tracking data received or an unknown error occurred.")
        validated_data = {"error_status": "No tracking data received or an unknown error occurred."}
    return validated_data

# --- New Section for Loading Data from Files (Updated Call) ---

def process_tracking_file(file_path):
    """
    Loads tracking data from a specified JSON file, processes it,
    and returns the `response_for_connect` dictionary.
    """
    print(f"\n--- Processing file: {file_path} ---")
    try:
        with open(file_path, 'r') as f:
            tracking_data = json.load(f) # Load JSON content from file into a Python dictionary
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return {
            "lambdaResult": "Unsuccessful",
            "errorMessage": f"File not found: {file_path}",
            "displayMessage": "Terjadi kesalahan: File data tidak ditemukan."
        }
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return {
            "lambdaResult": "Unsuccessful",
            "errorMessage": f"Invalid JSON in file: {file_path}",
            "displayMessage": "Terjadi kesalahan: Format data JSON tidak valid."
        }

    # IMPORTANT CHANGE: No json.loads() here, as dataprocessing now returns a dict
    validated_data = dataprocessing(tracking_data)

    response_for_connect = {
        "lambdaResult": "Success", # Default to success, will change on error
        "trackingStatus": "UNKNOWN", # Default tracking status
        "displayMessage": "Barang belum diterima dari ekspedisi atau terjadi kesalahan.", # Default message for Connect
        "deliveryDate": '',
        "deliveryTime": '',
        "originContact": '',
        "originAddress": '',
        "destinationContact": '',
        "destinationAddress": '',
        "latestEventMessage": 'abc'
    }

    if validated_data and "error_status" not in validated_data:
        # Ensure 'data' and 'status' keys exist in the successful response
        if "data" in validated_data and "status" in validated_data["data"]:
            data_to_take = validated_data["data"]
            status = data_to_take["status"]
            response_for_connect["trackingStatus"] = status
            if status == 'Delivered':
                    response_for_connect["displayMessage"] = 'Barang sudah sampai ke tujuan'
            elif data_to_take["status"] == 'InTransit':
                    response_for_connect["displayMessage"] = 'Barang sedang dalam proses pengiriman'
            elif status == 'OutForDelivery':
                    response_for_connect["displayMessage"] = 'Barang sedang diantarkan ke alamatmu'
            elif status == 'InfoReceived':
                    response_for_connect["displayMessage"] = 'Kurir sudah menerima informasi tentang paketmu.'       
            elif status == 'FailedAttempt':
                    response_for_connect["displayMessage"] = 'Barang gagal dikirimkan, silakan tunggu sebentar'
            elif status == 'ReturnToSender':
                    response_for_connect["displayMessage"] = 'Barang dalam perjalanan kembali ke pengirim'
            elif status == 'Exception':
                    response_for_connect["displayMessage"] = 'Barang gagal dikirimkan, silakan tunggu sebentar'
            elif status == 'Expired':
                    response_for_connect["displayMessage"] = 'Terjadi kesalahan pada kurir, mohon hubungi kurir langsung'
            elif status == 'Pending':
                    response_for_connect["displayMessage"] = 'Tidak ada informasi terkait resi yang diinput, mohon hubungi kurir langsung'

            # Extract common origin/destination data
            origin_contact = data_to_take.get('origin', {}).get('contact_name', '')
            origin_address = data_to_take.get('origin', {}).get('address', '')
            dest_contact = data_to_take.get('destination', {}).get('contact_name', '')
            dest_address = data_to_take.get('destination', {}).get('address', '')

            response_for_connect["originContact"] = origin_contact
            response_for_connect["originAddress"] = origin_address
            response_for_connect["destinationContact"] = dest_contact
            response_for_connect["destinationAddress"] = dest_address

            if 'histories' in validated_data['data']:
                first_history_entry = validated_data['data']['histories'][0] # Assuming first entry is the delivery event
                datetime_string = first_history_entry.get('date', '')

                date_part = ""
                time_part = ""
                if 'T' in datetime_string:
                    parts = datetime_string.split('T')
                    date_part = parts[0]
                    # Split off timezone offset
                    time_str_part_with_offset = parts[1]
                    time_part = time_str_part_with_offset.split('+')[0].split('-')[0]

                last_message = validated_data['data']['histories'][0]['message']

                response_for_connect['latestEventMessage'] = last_message
                response_for_connect['deliveryDate'] = date_part
                response_for_connect['deliveryTime'] = time_part
            else:
                response_for_connect['displayMessage'] = 'Histori pengiriman tidak ditemukan'
        else:
            response_for_connect['displayMessage'] = 'Status pengiriman tidak ditemukan'

    elif validated_data and "error_status" in validated_data: # Use validated_data here
        # API returned an error (e.g., tracking number not found, invalid API key)
        response_for_connect["lambdaResult"] = "Unsuccessful"
        # Prioritize 'details' or 'error' message from the API response
        api_error_message = validated_data.get("details", validated_data.get("error_status", "Unknown API error."))
        response_for_connect["errorMessage"] = api_error_message
        response_for_connect["displayMessage"] = f"Terjadi kesalahan saat mengambil data pelacakan: {api_error_message}. Mohon periksa kembali nomor pelacakan Anda."
        print(f"API Error Response: {json.dumps(validated_data)}") # Use validated_data here

    else:
        # This handles cases where no tracking_data is returned at all or other unhandled exceptions
        response_for_connect["lambdaResult"] = "Unsuccessful"
        response_for_connect["errorMessage"] = "No tracking data received or an unknown error occurred."
        response_for_connect["displayMessage"] = "Barang belum diterima dari ekspedisi atau terjadi kesalahan saat mengambil data."
        print("No tracking data received or an unknown error occurred (empty tracking_data).")

    return response_for_connect

# --- Main Execution Block (remains the same) ---

if __name__ == "__main__":
    # Create a directory to store your test JSON files
    test_data_dir = "test_json_data"
    os.makedirs(test_data_dir, exist_ok=True)

    # Get a list of all JSON files in the test_data_dir
    test_files = [f for f in os.listdir(test_data_dir) if f.endswith('.json')]

    for test_file_name in test_files:
        test_file_name = 'delivery_intransit.json'
        file_path = os.path.join(test_data_dir, test_file_name)
        result = process_tracking_file(file_path)
        print("\n--- Final `response_for_connect` ---")
        print(json.dumps(result, indent=4))
        print("-" * 40)