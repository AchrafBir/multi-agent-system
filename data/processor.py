import pandas as pd
import logging

def read_data(file_path):
    try:
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            data = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format.")
        logging.info(f"Data loaded from {file_path}")
        return data
    except Exception as e:
        logging.error(f"Error reading the file: {e}")
        return None

def preprocess_data(data):
    data = data.dropna()
    logging.info("Data preprocessing completed.")
    return data

def process_data_from_file(file_path):
    data = read_data(file_path)
    if data is None:
        return []
    data = preprocess_data(data)
    task_list = data.to_dict(orient='records')
    return task_list