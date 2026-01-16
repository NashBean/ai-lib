# ai-lib/bdh_wrapper.py - Wrapper for BDH as core learning function
# BDH Integration (Baby Dragon Hatchling for core learning/response)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'bdh')))

from bdh.train import BDHModel  # Assuming BDH's main class (adapt from code)

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 3
FIX_VERSION = 0
VERSION_STRING = f"v{MAJOR_VERSION}.{MINOR_VERSION}.{FIX_VERSION}"


# Load or train BDH on AI data
def load_bdh_model(data_file, param_size=10000000):  # Small for testing
    try:
        model = BDHModel(param_size=param_size)
        # Train on data.json (adapt from README's train.py example)
        with open(data_file, "r") as f:
            data_text = json.dump(json.load(f), indent=4)  # Convert to text for training
        model.train(data_text)  # BDH training call (customize as per code)
        logger.info("BDH model loaded/trained.")
        return model
    except Exception as e:
        logger.error(f"BDH load error: {e}")
        return None

# Generate response using BDH
def bdh_generate(model, prompt):
    if model is None:
        return "BDH not loaded."
    # Use BDH for "deep" response (adapt from BDH generation logic)
    return model.generate(prompt)  # Placeholder - customize from BDH code

# Self-learn with BDH
def bdh_self_learn(model, topic, research):
    if model is None:
        return "BDH not loaded."
    # Update model with new data (Hebbian-style)
    model.update(research)  # Placeholder - adapt BDH's memory update
    return "Learned via BDH."