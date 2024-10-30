import os

# Prompt the user to enter their name
name = input("Enter your name: ").strip()

# Validate the user input
if not name:
    print("Error: Name cannot be empty.")
    exit()

# Define the directory path to save samples: data/samples/<name>
samples_dir = os.path.join('data', 'samples', name)

# Create the directory structure if it doesn't exist
os.makedirs(samples_dir, exist_ok=True)

print(f"Samples will be saved in: {samples_dir}")