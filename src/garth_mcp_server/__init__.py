import os
from datetime import date
from functools import wraps
from urllib.parse import urlencode
from typing import Optional
import contextlib
import threading

import garth
from mcp.server.fastmcp import FastMCP


__version__ = "0.0.8"

# Thread-local storage for HTTP context (Bearer token)
_context = threading.local()

server = FastMCP("Garth - Garmin Connect", dependencies=["garth"])

def set_bearer_token(token: str):
    """Set the Bearer token for the current request context."""
    _context.bearer_token = token

def get_bearer_token() -> Optional[str]:
    """Get the Bearer token from the current request context."""
    return getattr(_context, 'bearer_token', None)


def requires_garth_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # First try to get token from HTTP Bearer authentication (HTTP mode)
        token = get_bearer_token()
        
        # Fall back to environment variable (stdio mode for backward compatibility)
        if not token:
            token = os.getenv("GARTH_TOKEN")
            
        if not token:
            return "Authentication required: You must provide a GARTH_TOKEN via Bearer authentication or environment variable to use this tool"
        
        garth.client.loads(token)
        return func(*args, **kwargs)

    return wrapper


# Tools using Garth data classes


@server.tool()
@requires_garth_session
def user_profile() -> str | garth.UserProfile:
    """
    Get user profile information using Garth's UserProfile data class.
    """
    return garth.UserProfile.get()


@server.tool()
@requires_garth_session
def user_settings() -> str | garth.UserSettings:
    """
    Get user settings using Garth's UserSettings data class.
    """
    return garth.UserSettings.get()


@server.tool()
@requires_garth_session
def weekly_intensity_minutes(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklyIntensityMinutes]:
    """
    Get weekly intensity minutes data for a given date and number of weeks.
    If no date is provided, the current date will be used.
    If no weeks are provided, 1 week will be used.
    """
    return garth.WeeklyIntensityMinutes.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_body_battery(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyBodyBatteryStress]:
    """
    Get daily body battery data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyBodyBatteryStress.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_hydration(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyHydration]:
    """
    Get daily hydration data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyHydration.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_steps(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailySteps]:
    """
    Get daily steps data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailySteps.list(end_date, days)


@server.tool()
@requires_garth_session
def weekly_steps(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklySteps]:
    """
    Get weekly steps data for a given date and number of weeks.
    If no date is provided, the current date will be used.
    If no weeks are provided, 1 week will be used.
    """
    return garth.WeeklySteps.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_hrv(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyHRV]:
    """
    Get daily heart rate variability data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyHRV.list(end_date, days)


@server.tool()
@requires_garth_session
def hrv_data(end_date: date | None = None, days: int = 1) -> str | list[garth.HRVData]:
    """
    Get detailed HRV data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.HRVData.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_sleep(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailySleep]:
    """
    Get daily sleep summary data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailySleep.list(end_date, days)


# Tools using direct API calls


@server.tool()
@requires_garth_session
def get_activities(
    start_date: str | None = None, limit: int | None = None
) -> str | dict | None:
    """
    Get list of activities from Garmin Connect.
    start_date: Start date for activities (YYYY-MM-DD format)
    limit: Maximum number of activities to return
    """
    params = {}
    if start_date:
        params["startDate"] = start_date
    if limit:
        params["limit"] = str(limit)

    endpoint = "activitylist-service/activities/search/activities"
    if params:
        endpoint += "?" + urlencode(params)
    return garth.connectapi(endpoint)


@server.tool()
@requires_garth_session
def get_activities_by_date(date: str) -> str | dict | None:
    """
    Get activities for a specific date from Garmin Connect.
    date: Date for activities (YYYY-MM-DD format)
    """
    return garth.connectapi(f"wellness-service/wellness/dailySummaryChart/{date}")


@server.tool()
@requires_garth_session
def get_activity_details(activity_id: str) -> str | dict | None:
    """
    Get detailed information for a specific activity.
    activity_id: Garmin Connect activity ID
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}")


@server.tool()
@requires_garth_session
def get_activity_splits(activity_id: str) -> str | dict | None:
    """
    Get lap/split data for a specific activity.
    activity_id: Garmin Connect activity ID
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}/splits")


@server.tool()
@requires_garth_session
def get_activity_weather(activity_id: str) -> str | dict | None:
    """
    Get weather data for a specific activity.
    activity_id: Garmin Connect activity ID
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}/weather")


@server.tool()
@requires_garth_session
def get_body_composition(date: str | None = None) -> str | dict | None:
    """
    Get body composition data from Garmin Connect.
    date: Date for body composition data (YYYY-MM-DD format), if not provided returns latest
    """
    if date:
        endpoint = f"wellness-service/wellness/bodyComposition/{date}"
    else:
        endpoint = "wellness-service/wellness/bodyComposition"
    return garth.connectapi(endpoint)


@server.tool()
@requires_garth_session
def get_respiration_data(date: str) -> str | dict | None:
    """
    Get respiration data from Garmin Connect.
    date: Date for respiration data (YYYY-MM-DD format)
    """
    return garth.connectapi(f"wellness-service/wellness/dailyRespiration/{date}")


@server.tool()
@requires_garth_session
def get_spo2_data(date: str) -> str | dict | None:
    """
    Get SpO2 (blood oxygen) data from Garmin Connect.
    date: Date for SpO2 data (YYYY-MM-DD format)
    """
    return garth.connectapi(f"wellness-service/wellness/dailyPulseOx/{date}")


@server.tool()
@requires_garth_session
def get_blood_pressure(date: str) -> str | dict | None:
    """
    Get blood pressure readings from Garmin Connect.
    date: Date for blood pressure data (YYYY-MM-DD format)
    """
    return garth.connectapi(f"wellness-service/wellness/dailyBloodPressure/{date}")


@server.tool()
@requires_garth_session
def get_devices() -> str | dict | None:
    """
    Get connected devices from Garmin Connect.
    """
    return garth.connectapi("device-service/deviceregistration/devices")


@server.tool()
@requires_garth_session
def get_device_settings(device_id: str) -> str | dict | None:
    """
    Get settings for a specific device.
    device_id: Device ID from Garmin Connect
    """
    return garth.connectapi(
        f"device-service/deviceservice/device-info/settings/{device_id}"
    )


@server.tool()
@requires_garth_session
def get_gear() -> str | dict | None:
    """
    Get gear information from Garmin Connect.
    """
    return garth.connectapi("gear-service/gear")


@server.tool()
@requires_garth_session
def get_gear_stats(gear_uuid: str) -> str | dict | None:
    """
    Get usage statistics for specific gear.
    gear_uuid: UUID of the gear item
    """
    return garth.connectapi(f"gear-service/gear/stats/{gear_uuid}")


@server.tool()
@requires_garth_session
def get_connectapi_endpoint(endpoint: str) -> str | dict | None:
    """
    Get the data from a given Garmin Connect API endpoint.
    This is a generic tool that can be used to get data from any Garmin Connect API endpoint.
    """
    return garth.connectapi(endpoint)


@server.tool()
@requires_garth_session
def nightly_sleep(
    end_date: date | None = None, nights: int = 1, sleep_movement: bool = False
) -> str | list[garth.SleepData]:
    """
    Get sleep stats for a given date and number of nights.
    If no date is provided, the current date will be used.
    If no nights are provided, 1 night will be used.
    sleep_movement provides detailed sleep movement data. If looking at
    multiple nights, it'll be a lot of data.
    """
    sleep_data = garth.SleepData.list(end_date, nights)
    if not sleep_movement:
        for night in sleep_data:
            if hasattr(night, "sleep_movement"):
                del night.sleep_movement
    return sleep_data


@server.tool()
@requires_garth_session
def daily_stress(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyStress]:
    """
    Get daily stress data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyStress.list(end_date, days)


@server.tool()
@requires_garth_session
def weekly_stress(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklyStress]:
    """
    Get weekly stress data for a given date and number of weeks.
    If no date is provided, the current date will be used.
    If no weeks are provided, 1 week will be used.
    """
    return garth.WeeklyStress.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_intensity_minutes(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyIntensityMinutes]:
    """
    Get daily intensity minutes data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyIntensityMinutes.list(end_date, days)


@server.tool()
@requires_garth_session
def monthly_activity_summary(month: int, year: int) -> str | dict | None:
    """
    Get the monthly activity summary for a given month and year.
    """
    return garth.connectapi(f"mobile-gateway/calendar/year/{year}/month/{month}")


@server.tool()
@requires_garth_session
def snapshot(from_date: date, to_date: date) -> str | dict | None:
    """
    Get the snapshot for a given date range. This is a good starting point for
    getting data for a given date range. It can be used in combination with
    the get_connectapi_endpoint tool to get data from any Garmin Connect API
    endpoint.
    """
    return garth.connectapi(f"mobile-gateway/snapshot/detail/v2/{from_date}/{to_date}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Garth MCP Server")
    parser.add_argument(
        "--http", 
        action="store_true", 
        help="Run as HTTP server (default: stdio)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port for HTTP server (default: 8000)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host for HTTP server (default: 0.0.0.0)"
    )
    
    args = parser.parse_args()
    
    if args.http:
        # Run as HTTP server
        run_http_server(args.host, args.port)
    else:
        # Run as stdio server (default)
        server.run()

def run_http_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the MCP server over HTTP with Bearer token authentication."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    import traceback
    from urllib.parse import urlparse, parse_qs
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    # Get the FastMCP server's tools for integration
    server_tools = {}
    
    # Extract tool information from the FastMCP server
    # This is a simplified approach - in practice, we'd integrate more deeply with FastMCP
    try:
        # Try to access FastMCP's internal tool registry
        if hasattr(server, '_tools'):
            server_tools = server._tools
        elif hasattr(server, 'tools'):
            server_tools = server.tools
    except:
        pass
    
    class MCPHTTPHandler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            """Handle CORS preflight requests."""
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
        
        def do_GET(self):
            """Handle GET requests for health check and info."""
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                health_response = {
                    "status": "healthy",
                    "server": "Garth MCP Server",
                    "version": __version__,
                    "authentication": "Bearer token required"
                }
                self.wfile.write(json.dumps(health_response).encode('utf-8'))
                return
            
            elif parsed_path.path == '/tools':
                # Return available tools list
                auth_header = self.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    self.send_error(401, 'Bearer token required')
                    return
                
                # Basic token validation
                token = auth_header[7:]
                if not token:
                    self.send_error(401, 'Invalid Bearer token')
                    return
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # List all available tools
                tools_list = [
                    {"name": "user_profile", "description": "Get user profile information"},
                    {"name": "user_settings", "description": "Get user settings"},
                    {"name": "daily_steps", "description": "Get daily steps data"},
                    {"name": "daily_sleep", "description": "Get daily sleep data"},
                    {"name": "get_activities", "description": "Get activities from Garmin Connect"},
                    {"name": "get_body_composition", "description": "Get body composition data"},
                    {"name": "snapshot", "description": "Get snapshot data for date ranges"},
                    # Add more tools as needed
                ]
                
                response = {
                    "tools": tools_list,
                    "count": len(tools_list)
                }
                self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
                return
                
            else:
                self.send_error(404, 'Not Found - Available endpoints: /health, /tools, POST /')
        
        def do_POST(self):
            """Handle POST requests for tool execution."""
            try:
                # Extract Bearer token
                auth_header = self.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    self.send_error(401, 'Bearer token required. Use Authorization: Bearer <your_garth_token>')
                    return
                
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                if not token:
                    self.send_error(401, 'Invalid Bearer token')
                    return
                    
                set_bearer_token(token)
                
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                request_body = self.rfile.read(content_length).decode('utf-8')
                
                try:
                    request_data = json.loads(request_body)
                except json.JSONDecodeError:
                    self.send_error(400, 'Invalid JSON in request body')
                    return
                
                # Handle the tool call
                response = self.handle_tool_call(request_data)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_json = json.dumps(response, indent=2, default=str)
                self.wfile.write(response_json.encode('utf-8'))
                
            except Exception as e:
                self.send_error(500, f'Internal Server Error: {str(e)}')
                traceback.print_exc()
        
        def handle_tool_call(self, request_data):
            """Handle tool execution requests."""
            tool_name = request_data.get('tool')
            arguments = request_data.get('arguments', {})
            
            if not tool_name:
                return {
                    "error": "Missing 'tool' parameter in request",
                    "example": {
                        "tool": "user_profile",
                        "arguments": {}
                    }
                }
            
            try:
                # Map tool names to functions
                tool_functions = {
                    'user_profile': user_profile,
                    'user_settings': user_settings,
                    'daily_steps': daily_steps,
                    'daily_sleep': daily_sleep,
                    'daily_hydration': daily_hydration,
                    'daily_body_battery': daily_body_battery,
                    'daily_hrv': daily_hrv,
                    'weekly_steps': weekly_steps,
                    'weekly_intensity_minutes': weekly_intensity_minutes,
                    'hrv_data': hrv_data,
                    'nightly_sleep': nightly_sleep,
                    'daily_stress': daily_stress,
                    'weekly_stress': weekly_stress,
                    'daily_intensity_minutes': daily_intensity_minutes,
                    'get_activities': get_activities,
                    'get_activities_by_date': get_activities_by_date,
                    'get_activity_details': get_activity_details,
                    'get_activity_splits': get_activity_splits,
                    'get_activity_weather': get_activity_weather,
                    'get_body_composition': get_body_composition,
                    'get_respiration_data': get_respiration_data,
                    'get_spo2_data': get_spo2_data,
                    'get_blood_pressure': get_blood_pressure,
                    'get_devices': get_devices,
                    'get_device_settings': get_device_settings,
                    'get_gear': get_gear,
                    'get_gear_stats': get_gear_stats,
                    'get_connectapi_endpoint': get_connectapi_endpoint,
                    'monthly_activity_summary': monthly_activity_summary,
                    'snapshot': snapshot,
                }
                
                if tool_name not in tool_functions:
                    return {
                        "error": f"Unknown tool: {tool_name}",
                        "available_tools": list(tool_functions.keys())
                    }
                
                # Execute the tool function
                tool_func = tool_functions[tool_name]
                
                # Call the function with provided arguments
                if arguments:
                    result = tool_func(**arguments)
                else:
                    result = tool_func()
                
                return {
                    "tool": tool_name,
                    "result": result,
                    "status": "success"
                }
                
            except Exception as e:
                return {
                    "tool": tool_name,
                    "error": str(e),
                    "status": "error"
                }
        
        def log_message(self, format, *args):
            """Override to customize logging."""
            print(f"[{self.address_string()}] {format % args}")
    
    print(f"🚀 Garth MCP HTTP Server starting...")
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"🔑 Authentication: Bearer token required")
    print(f"📊 Health check: GET http://{host}:{port}/health")
    print(f"🛠️  Available tools: GET http://{host}:{port}/tools")
    print(f"⚡ Tool execution: POST http://{host}:{port}/")
    print(f"")
    print(f"💡 Usage example:")
    print(f"   curl -H 'Authorization: Bearer <your_garth_token>' \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d '{{\"tool\": \"user_profile\", \"arguments\": {{}}}}' \\")
    print(f"        http://{host}:{port}/")
    print(f"")
    print(f"🔗 For n8n MCP Client, use:")
    print(f"   - URL: http://{host}:{port}/")
    print(f"   - Auth: Bearer")
    print(f"   - Token: <your_garth_token>")
    
    httpd = HTTPServer((host, port), MCPHTTPHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down HTTP server...")
        httpd.shutdown()


if __name__ == "__main__":
    main()
