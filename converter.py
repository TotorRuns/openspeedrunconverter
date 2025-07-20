
import xml.etree.ElementTree as ET
import json
import os
import base64
import sys

def convert_lss_to_json(lss_file_path):
    """
    Converts a LiveSplit split file (.lss) to a specific JSON format.

    Args:
        lss_file_path (str): The path to the .lss file.
    """
    def sanitize_filename(name):
        """Sanitizes a string to be used as a filename."""
        return "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '_')]).rstrip()

    try:
        tree = ET.parse(lss_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML in {lss_file_path}: {e}")
        return
    except FileNotFoundError:
        print(f"Error: {lss_file_path} not found.")
        return

    file_name = os.path.splitext(os.path.basename(lss_file_path))[0]
    icons_to_save = []

    # Extract data
    game_name = root.find('GameName').text
    category_name = root.find('CategoryName').text
    offset = root.find('Offset').text
    
    # Attempt to extract layout settings, provide defaults if not present
    splits_per_page = 5
    auto_update_pb = True
    gold_split = True
    
    layout = root.find('Layout')
    if layout is not None:
        settings = layout.find('Settings')
        if settings is not None:
            splits_per_page_element = settings.find('SplitsPerPage')
            if splits_per_page_element is not None:
                splits_per_page = int(splits_per_page_element.text)
            
            auto_update_pb_element = settings.find('AutoUpdatePB')
            if auto_update_pb_element is not None:
                auto_update_pb = auto_update_pb_element.text.lower() == 'true'

            gold_split_element = settings.find('GoldSplit')
            if gold_split_element is not None:
                gold_split = gold_split_element.text.lower() == 'true'


        

    def get_image_format(data):
        """Detects image format based on magic bytes."""
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        elif data.startswith(b'\xff\xd8\xff'):
            return 'jpg'
        elif data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
            return 'gif'
        elif data.startswith(b'BM'):
            return 'bmp'
        elif data.startswith(b'\x00\x00\x01\x00'):
            return 'ico'
        # Add more formats as needed
        return 'bin' # Default to binary if format not recognized

    splits = []
    for segment in root.find('Segments'):
        split_name = segment.find('Name').text
        icon_element = segment.find('Icon')
        icon_path = None

        if icon_element is not None and icon_element.text:
            try:
                icon_data = base64.b64decode(icon_element.text)
                
                # Search for PNG magic bytes within the decoded data
                png_magic = b'\x89PNG\r\n\x1a\n'
                png_start_index = icon_data.find(png_magic)

                if png_start_index != -1:
                    # Search for PNG IEND chunk after the start of PNG data
                    iend_chunk = b'\x00\x00\x00\x00IEND\xaeB`\x82' # IEND chunk with CRC
                    iend_index = icon_data.find(iend_chunk, png_start_index)

                    if iend_index != -1:
                        # Extract the PNG data between magic bytes and IEND chunk
                        actual_image_data = icon_data[png_start_index : iend_index + len(iend_chunk)]
                        image_format = get_image_format(actual_image_data)
                    else:
                        # If IEND chunk not found, assume it's just raw PNG data from start_index
                        actual_image_data = icon_data[png_start_index:]
                        image_format = get_image_format(actual_image_data)
                else:
                    # If PNG magic bytes are not found, default to bin
                    actual_image_data = icon_data
                    image_format = 'bin'
                sanitized_name = sanitize_filename(split_name)
                icon_filename = f"{sanitized_name.replace(' ', '_').lower()}.{image_format}"
                
                # Ensure the icon path in the JSON is relative and uses forward slashes
                json_icon_path = f"icons/{icon_filename}"
                
                icons_to_save.append({"path": json_icon_path, "data": actual_image_data})
                
                icon_path = json_icon_path
            except (base64.binascii.Error, IOError) as e:
                print(f"Could not process icon for '{split_name}': {e}")


        splits.append({
            "name": split_name,
            "pb_time": None,
            "last_time": None,
            "gold_time": None,
            "icon_path": icon_path
        })

    def time_to_milliseconds(time_str):
        """Converts a time string (HH:MM:SS.ms) to milliseconds."""
        if not time_str:
            return 0
        
        parts = time_str.split(':')
        if len(parts) != 3:
            # Handle cases where the format is unexpected
            return 0

        seconds_and_ms = parts[2].split('.')
        
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(seconds_and_ms[0])
        
        milliseconds = 0
        if len(seconds_and_ms) > 1:
            ms_str = seconds_and_ms[1]
            # Pad with zeros to make it 3 digits for milliseconds
            ms_str = (ms_str + "000")[:3]
            milliseconds = int(ms_str)

        return (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds

    # Construct JSON data
    json_data = {
        "title": game_name,
        "category": category_name,
        "splits": splits,
        "start_offset": time_to_milliseconds(offset),
        "splits_per_page": splits_per_page,
        "auto_update_pb": auto_update_pb,
        "gold_split": gold_split
    }

    return {"main_data": json_data, "icons": icons_to_save}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python converter.py <path_to_lss_file>")
        sys.exit(1)
    
    lss_file = sys.argv[1]
    result = convert_lss_to_json(lss_file)
    if result:
        print(json.dumps(result, indent=2))
