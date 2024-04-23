import subprocess
import signal
import sys
from collections import defaultdict
import re
import warnings
import csv
import datetime
import time

from constants import AVAILABLE_API_PATH, OVERALL_ANALYSIS_DURATION, MAX_PATH_HIT_ANALYSIS_DURATION, DURATION_UNIT, EXPORT_CSV_DURATION


level_counts = defaultdict(int)
error_counts = defaultdict(int)
path_level_counts = defaultdict(lambda: defaultdict(int))

start_time = datetime.datetime.now()
last_write_time = start_time

# Function to parse GENRATED log message
def parse_log_message(message):
    pattern = r'(\w+):(.+):(.+) for (.+)'
    match = re.match(pattern, message)
    if match:
        return match.groups()
    else:
        return None

#Prints the overall analysis
def print_overall_analysis():
    print("***************************************")

    print("Logger Level Counts:")
    for level, count in level_counts.items():
        print(f"{level}: {count}")

    print("\nPath Level Counts:")
    for path, counts in path_level_counts.items():
        print("-----------------------------------")
        print(f"Path: {path}")
        for level, count in counts.items():
            print(f" {level}: {count}")
    
    print("***************************************")

# Function to find the most hit path
def find_most_hit_path(data):
    max_sum = 0
    most_hit_path = None
    for path, sub_data in data.items():
        current_sum = sum(sub_data.values())
        if current_sum > max_sum:
            max_sum = current_sum
            most_hit_path = path
    return most_hit_path

def write_to_csv(level_counts, path_level_counts):
    # Create a filename based on the current time
    filename = f"log_counts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Level', 'Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for level, count in level_counts.items():
            writer.writerow({'Level': level, 'Count': count})
        
        # Write path-wise counts
        writer.writeheader()
        for path, counts in path_level_counts.items():
            for level, count in counts.items():
                writer.writerow({'Level': f"{path} - {level}", 'Count': count})


# Function to start log monitoring
def monitor_application():
    global level_counts, path_level_counts, last_write_time # Declare these as global

    try:
        # Start the application as a subprocess
        application_command = ["/usr/bin/python3", "app.py"]
        application_process = subprocess.Popen(application_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
       
        overall_analysis_count = 0
        max_path_hit_analysis_count = 0
        # Continuously read and analyse application's log messagess
        while True:
            line = application_process.stdout.readline().strip()
        
            if line:
                parsed = parse_log_message(line.strip())

                if parsed:
                    level, log_location, error_message, path = parsed
                    level_counts[level] += 1
                    path_level_counts[path][level] += 1
                    overall_analysis_count+=1
                    max_path_hit_analysis_count+=1
                else:
                    print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    warnings.warn("FAILED TO PARSE FOLLOWING LOG :", line)
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

                if (overall_analysis_count == OVERALL_ANALYSIS_DURATION):
                    # Print analysis results
                    print_overall_analysis()                    
                    overall_analysis_count = 0
                
                if(max_path_hit_analysis_count == MAX_PATH_HIT_ANALYSIS_DURATION):
                    max_hitted_path = find_most_hit_path(path_level_counts)
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print(f"MAXIMUM HITTED API IN LAST {MAX_PATH_HIT_ANALYSIS_DURATION} {DURATION_UNIT} IS : {max_hitted_path}")
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                # Check if an hour has passed since the last write
                current_time = datetime.datetime.now()
                if (current_time - last_write_time).total_seconds() >= EXPORT_CSV_DURATION:
                    write_to_csv(level_counts, path_level_counts)
                    # Reset counters and update the last write time
                    level_counts = {"info": 0, "debug": 0, "warning": 0}
                    path_level_counts = {}
                    last_write_time = current_time

    except KeyboardInterrupt:
        # Handle Ctrl+C to stop the monitoring loop
        print("\nMonitoring stopped.")

        # Terminate the application process
        application_process.terminate()

    except Exception as e:
        warnings.warn(f"Error occurred: {e}")

if __name__ == "__main__":
    monitor_application()
