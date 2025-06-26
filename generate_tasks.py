import json
import random
import uuid

NUM_TASKS_TO_GENERATE = 5000
OUTPUT_FILE_PATH = "data/tasks.json"

NODE_LOCATIONS = ["node-1", "node-2", "node-3", "unspecified"]
PRIORITY_LEVELS = [1, 1, 1, 5, 5, 10, 10]
DATA_TEMPLATES = [
    "Process customer feedback log: {uuid}",
    "Analyze sales data for region: {region}",
    "Render video frame sequence: {uuid}",
    "Transcode audio file: {uuid}",
    "Run ML inference on image batch: {uuid}",
    "Archive user data for user_id: {user_id}",
    "Calculate financial risk model for transaction: {uuid}",
]
REGIONS = ["NA", "EMEA", "APAC", "LATAM"]

def generate_single_task(task_index):
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    priority = random.choice(PRIORITY_LEVELS)
    location = random.choice(NODE_LOCATIONS)
    template = random.choice(DATA_TEMPLATES)
    data_content = template.format(
        uuid=uuid.uuid4(),
        region=random.choice(REGIONS),
        user_id=random.randint(10000, 99999)
    )
    
    return {
        "task_id": task_id,
        "priority": priority,
        "location": location,
        "data": data_content
    }

def main():
    print(f"Generating {NUM_TASKS_TO_GENERATE} tasks...")
    
    all_tasks = [generate_single_task(i) for i in range(NUM_TASKS_TO_GENERATE)]
    
    print(f"Saving tasks to {OUTPUT_FILE_PATH}...")
    
    try:
        with open(OUTPUT_FILE_PATH, "w") as f:
            json.dump(all_tasks, f, indent=4) 
        print("Done! Your new tasks.json file is ready.")
    except IOError as e:
        print(f"Error: Could not write to file {OUTPUT_FILE_PATH}. Reason: {e}")

if __name__ == "__main__":
    main()
