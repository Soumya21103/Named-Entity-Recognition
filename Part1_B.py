import json

# Function for performing BIO chunking
def bio_chunking(text, aspects, opinions):
    tokens = text.split()
    labels = ['O'] * len(tokens)
    
    # Assign BIO tags for aspect terms
    for aspect in aspects:
        aspect_start = aspect['from']
        aspect_end = aspect['to']
        for i in range(aspect_start, aspect_end):
            if i < len(tokens):
                if i == aspect_start:
                    labels[i] = 'B'
                else:
                    labels[i] = 'I'
    
    # Assign BIO tags for opinion terms
    for opinion in opinions:
        opinion_start = opinion['from']
        opinion_end = opinion['to']
        for i in range(opinion_start, opinion_end):
            if i < len(tokens):
                if labels[i] == 'O':
                    if i == opinion_start:
                        labels[i] = 'B'
                    else:
                        labels[i] = 'I'
    
    return tokens, labels

# Function for processing and saving data
def process_data(data, filename):
    processed_data = {}
    for i, entry in enumerate(data, start=1):
        text = entry['raw_words']
        aspects = entry['aspects']
        opinions = entry['opinions']
        tokens, labels = bio_chunking(text, aspects, opinions)
        processed_data[str(i)] = {'text': text, 'labels': labels}

    with open(filename, 'w') as f:
        json.dump(processed_data, f, indent=4)

# Loading and processing training data
with open('ATE/Laptop_Review_Train.json', 'r') as f:
    train_data = json.load(f)
process_data(train_data, 'ATE_train.json')

# Loading and processing validation data
with open('ATE/Laptop_Review_Val.json', 'r') as f:
    val_data = json.load(f)
process_data(val_data, 'ATE_val.json')

# Loading and processing test data
with open('ATE/Laptop_Review_Test.json', 'r') as f:
    test_data = json.load(f)
process_data(test_data, 'ATE_test.json')
