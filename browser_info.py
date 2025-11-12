"""
Browser and Device Information Parser
Extracts browser, device, and OS information from User-Agent strings
"""

import re
from user_agents import parse

def get_browser_info(user_agent_string):
    """
    Parse user agent string to extract browser and device information
    
    Args:
        user_agent_string: Raw user agent string from request headers
        
    Returns:
        dict: Parsed browser and device information
    """
    if not user_agent_string:
        return {
            "success": False,
            "error": "No user agent string provided"
        }
    
    try:
        # Parse using user-agents library
        user_agent = parse(user_agent_string)
        
        # Extract browser information
        browser_name = user_agent.browser.family or "Unknown"
        browser_version = user_agent.browser.version_string or "Unknown"
        
        # Extract OS information
        os_name = user_agent.os.family or "Unknown"
        os_version = user_agent.os.version_string or "Unknown"
        os_full = f"{os_name} {os_version}".strip()
        
        # Extract device information
        device_brand = user_agent.device.brand or "Unknown"
        device_model = user_agent.device.model or "Unknown"
        
        # Determine device type
        if user_agent.is_mobile:
            device_type = "Mobile"
        elif user_agent.is_tablet:
            device_type = "Tablet"
        elif user_agent.is_pc:
            device_type = "Desktop"
        elif user_agent.is_bot:
            device_type = "Bot"
        else:
            device_type = "Unknown"
        
        # Build device string
        if device_brand != "Unknown" and device_model != "Unknown":
            device_info = f"{device_brand} {device_model}"
        elif device_brand != "Unknown":
            device_info = device_brand
        elif device_model != "Unknown":
            device_info = device_model
        else:
            device_info = device_type
        
        return {
            "success": True,
            "data": {
                "browser_name": browser_name,
                "browser_version": browser_version,
                "browser_full": f"{browser_name} {browser_version}",
                "os_name": os_name,
                "os_version": os_version,
                "os_full": os_full,
                "device_type": device_type,
                "device_info": device_info,
                "device_brand": device_brand,
                "device_model": device_model,
                "is_mobile": user_agent.is_mobile,
                "is_tablet": user_agent.is_tablet,
                "is_pc": user_agent.is_pc,
                "is_bot": user_agent.is_bot,
                "raw_user_agent": user_agent_string
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error parsing user agent: {str(e)}",
            "raw_user_agent": user_agent_string
        }