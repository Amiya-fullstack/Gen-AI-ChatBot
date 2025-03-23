import os
import json

def extract_vue_sources(directory, output_file):
    dataset = []
    
    # Walk through the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".vue"):
                file_path = os.path.join(root, file)
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Append the Vue component source as a data point
                dataset.append({
                    "filename": file,
                    "filepath": file_path,
                    "source_code": content
                })
    
    # Save dataset to a JSON file
    with open(output_file, "w", encoding="utf-8") as out_file:
        json.dump(dataset, out_file, indent=4)
    
    print(f"Dataset saved to {output_file}")

# Example usage
vue_project_dir = "D:/vue/my-app"
output_json = "./vue_dataset.json"
extract_vue_sources(vue_project_dir, output_json)
