#!/usr/bin/env python3
# pathway_bdh_wrapper.py - Integrate Pathway for data streaming + BDH for learning

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'pathway')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'bdh')))

import pathway as pw
from bdh.train import BDHModel  # From BDH code

MAJOR_VERSION = 0
MINOR_VERSION = 3
FIX_VERSION = 1
# Version
VERSION_STRING = f"v{MAJOR_VERSION}.{MINOR_VERSION}.{FIX_VERSION}"

# Pathway stream for data (e.g., research API or Bible JSON)
def pathway_stream_data(source_file, topic):
    try:
        table = pw.io.jsonlines.read(source_file, schema=pw.schema_from_types(text=str))
        filtered = table.filter(table.text.contains(topic))
        return filtered  # Stream filtered data to BDH
    except Exception as e:
        logger.error(f"Pathway stream error: {e}")
        return pw.Table.empty()

# Train BDH on Pathway stream
def bdh_train_on_stream(stream, param_size=10000000):
    try:
        model = BDHModel(param_size=param_size)
        # Convert stream to text for BDH training (adapt from README train.py)
        data_text = '\n'.join(row['text'] for row in stream.iterrows())
        model.train(data_text)  # BDH training call
        return model
    except Exception as e:
        logger.error(f"BDH train error: {e}")
        return None

# Generate with BDH
def bdh_generate(model, prompt):
    if model is None:
        return "BDH not loaded."
    return model.generate(prompt)  # Adapt from BDH code

# Self-learn: Stream data + train BDH
def pathway_bdh_self_learn(source_file, topic):
    stream = pathway_stream_data(source_file, topic)
    model = bdh_train_on_stream(stream)
    return bdh_generate(model, f"Explain {topic} in context")

# Example use in scheduler or self_learn
# pathway_bdh_self_learn("data/abraham_data.json", "Ur culture")