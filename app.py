import json
import os

base = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base, "config.json")) as f:
    config = json.load(f)

with open(os.path.join(base, "kernel.txt")) as f:
    kernel = f.read()

print("Config loaded:")
print(config)
print("\nKernel loaded:")
print(kernel)