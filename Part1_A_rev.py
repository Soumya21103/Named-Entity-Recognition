import json
import random
from collections import defaultdict
import re
from sklearn.model_selection import train_test_split

# Loading the dataset
with open('NER/NER_TRAIN_JUDGEMENT.json', 'r') as f:
    data = json.load(f)

# Manually stratifying the data to ensure each class has at least two instances
class_instances = defaultdict(list)
for entry in data:
    annotations = entry['annotations']
    for annotation in annotations:
        for result in annotation['result']:  # Iterating over the list of annotations within 'result'
            label = result['value']['labels'][0]  # Accessing the 'labels' list and retrieve the first label
            class_instances[label].append(entry)

train_data = []
val_data = []

for instances in class_instances.values():
    instances_train, instances_val = train_test_split(instances, test_size=0.15, random_state=42)
    train_data.extend(instances_train)
    val_data.extend(instances_val)

def bio_chunking(text, annotations):
    char_t  = list(text)
    t_mask = ["0"]*len(char_t)
    fin_mask = ""
    fin_char = ""
    labels = dict()
    for j in annotations:
        for k in j["result"]:
            index = str(len(labels)+1)
            labels[index] = str(k["value"]["labels"][0])
            # print(k["value"])

            for l in range(k["value"]["start"],k["value"]["end"]):
                t_mask[l] = index
            # print(t_mask)
    
    # handling HTML
    s = 0
    for j in range(len(char_t)):
        if s == 0:
            if(char_t[j] == "<"):
                char_t[j] = ' '
                t_mask[j] = ' '
                s = 1
            if(char_t[j] == ">"):
                char_t[j] = ' '
                t_mask[j] = ' '
        if s == 1:
            if(char_t[j] == ">"):
                s == 0
            char_t[j] = ' '
            t_mask[j] = ' '

    # HANDELING CLOSURES 
    s = 0
    x = 0
    for j in range(len(char_t)):
        if char_t[j] in "<>(){[]}":
            char_t[j] = ' ' + char_t[j] + ' '
            t_mask[j] = ' ' + t_mask[j] + ' '
        
    for j in range(len(char_t)):
        if s == 0:
            if char_t[j] in "!,?\"\'": 
                s = 1
                x = j
            if char_t[j] == ' ':
                s = 2
        elif s == 1:
            if char_t[j] == ' ':
                char_t[x] = " " + char_t[x] + " "
                t_mask[x] = " " + t_mask[x] + " "
            s = 0
        elif s == 2:
            if char_t[j] in "!,?\"\'": 
                char_t[j] = " " + char_t[j] + " "
                t_mask[j] = " " + t_mask[j] + " "
            s = 0
            if char_t[j] == ' ':
                s = 2

    # HAndling unicodes
    for j in range(len(char_t)):
        char_t[j] = re.sub(r'[^\x00-\x7F]', '', char_t[j])
        char_t[j] = re.sub(r'\s+',' ',char_t[j])
        char_t[j] = re.sub(r'[-]',' ',char_t[j])
        if char_t[j] == '':
            t_mask[j] = ''
        if(char_t[j] == ' '):
            t_mask[j] = ' '

    #Handling spaces 
    for j in range(len(char_t)):
        if char_t[j] == ' ':
            t_mask[j] = ' '
    
    for j in range(len(char_t)):
        fin_char += char_t[j]
        fin_mask += t_mask[j]
 
    if(len(fin_mask.split(' ')) != len(fin_char.split(' '))):
        print(len(fin_mask.split(' ')) == len(fin_char.split(' ')))

    tokens = [t for t in  fin_char.split(' ') if len(t) != 0]
    token_mask =[t for t in  fin_mask.split(' ') if len(t) != 0] 


    final_tokens = []
    s = 0 
    q = 0
    for d in range(len(tokens)):
        maxim = 0
        for e in token_mask[d]:
            if e == '':
                continue
            if (int(e) > int(maxim)):
                maxim = int(e)
        if(s == 0):
            if(maxim != 0):
                s = 1
                q = maxim
                final_tokens.append("B_"+labels[str(maxim)])
            elif maxim == 0:
                final_tokens.append("O")
        elif(s == 1):
            if maxim == 0:
                s = 0
                q = 0
                final_tokens.append("O")
            elif maxim != q:
                s = 1
                q = maxim
                final_tokens.append("B_"+labels[str(maxim)])
            elif maxim == q:
                final_tokens.append("I_"+labels[str(maxim)])
    # print(final_tokens)
    # print(tokens)
    if(len(tokens) != len(final_tokens)):
        print("my methods are flawed")
    return ' '.join(tokens), final_tokens

# Processing and saving the train data
train_processed = {}
for entry in train_data:
    case_id = entry['id']
    text = entry['data']['text']
    annotations = entry['annotations']
    tokens, labels = bio_chunking(text, annotations)
    train_processed[case_id] = {'text': tokens, 'labels': labels}

with open('NER_train_rev1.json', 'w') as f:
    json.dump(train_processed, f, indent=4)

# Processing and saving the validation data
val_processed = {}
for entry in val_data:
    case_id = entry['id']
    text = entry['data']['text']
    annotations = entry['annotations']
    tokens, labels = bio_chunking(text, annotations)
    val_processed[case_id] = {'text': tokens, 'labels': labels}

with open('NER_val_rev1.json', 'w') as f:
    json.dump(val_processed, f, indent=4)
    
# Loading test data
with open('NER/NER_TEST_JUDGEMENT.json', 'r') as f:
    test_data = json.load(f)


# Processing and saving the test data
test_processed = {}
for entry in test_data:
    case_id = entry['id']
    text = entry['data']['text']
    annotations = entry['annotations']
    tokens, labels = bio_chunking(text, annotations)
    test_processed[case_id] = {'text': tokens, 'labels': labels}

with open('NER_test_rev1.json', 'w') as f:
    json.dump(test_processed, f, indent=4)
    
