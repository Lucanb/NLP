import pandas as pd
import numpy as np
import torch
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer

from datasets import load_dataset
dataset = load_dataset('squad', split='train', cache_dir='/media/data_files/github/website_tutorials/data')

squad = pd.DataFrame(dataset)
print(squad.columns)

cols = ["text","question","answer"]

comp_list = []

for index, row in squad.iterrows():
    temp_list = [row["context"], row["question"], row["answers"]["text"][0]]
    comp_list.append(temp_list)

new_df = pd.DataFrame(comp_list, columns=cols)
new_df.to_csv("SquAD_data.csv", index=False)


data = pd.read_csv("SquAD_data.csv")
data.head()

print("Number of question and answers: ", len(data))

model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')


random_num = np.random.randint(0,len(data))
question = data["question"][random_num]
text = data["text"][random_num]

input_ids = tokenizer.encode(question, text)
print("The input has a total of {} tokens.".format(len(input_ids)))

tokens = tokenizer.convert_ids_to_tokens(input_ids)

for token, id in zip(tokens, input_ids):
    print('{:8}{:8,}'.format(token,id))

#first occurence of [SEP] token
sep_idx = input_ids.index(tokenizer.sep_token_id)
print("SEP token index: ", sep_idx)


#number of tokens in segment A (question) - this will be one more than the sep_idx as the index in Python starts from 0
num_seg_a = sep_idx+1
print("Number of tokens in segment A: ", num_seg_a)
#number of tokens in segment B (text)
num_seg_b = len(input_ids) - num_seg_a
print("Number of tokens in segment B: ", num_seg_b)
#creating the segment ids
segment_ids = [0]*num_seg_a + [1]*num_seg_b
#making sure that every input token has a segment id
assert len(segment_ids) == len(input_ids)


#token input_ids to represent the input and token segment_ids to differentiate our segments - question and text
output = model(torch.tensor([input_ids]),  token_type_ids=torch.tensor([segment_ids]))


answer_start = torch.argmax(output.start_logits)
answer_end = torch.argmax(output.end_logits)

if answer_end >= answer_start:
    answer = " ".join(tokens[answer_start:answer_end+1])
    print("\nQuestion:\n{}".format(question.capitalize()))
    print("\nAnswer:\n{}.".format(answer.capitalize()))
else:
    print("I am unable to find the answer to this question. Can you please ask another question?")
#schimbat contextul - ce intrebare vreau eu - aleg input ; si la la final de adaugat cum schimba contextul - mesaj si traducerea.