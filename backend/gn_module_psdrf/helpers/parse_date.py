from datetime import datetime

def parse_iso_datetime(date_str):
    """Parses a datetime string that may include URL-encoded characters."""
    # Decode URL-encoded characters if any; for example, %3A to :
    try:
        # Replace any '+' with spaces and decode URL-encoded colons
        decoded_date_str = date_str.replace('+', ' ').replace('%3A', ':')
        # Python's strptime does not handle milliseconds directly, so split them if present
        if '.' in decoded_date_str:
            decoded_date_str = decoded_date_str.split('.')[0]
        
        # Check for the presence of 'T', if ISO format used differently
        if 'T' in decoded_date_str:
            return datetime.fromisoformat(decoded_date_str)
        else:
            # Assuming the format is 'YYYY-MM-DD HH:MM:SS'
            return datetime.strptime(decoded_date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}. Error: {str(e)}")
