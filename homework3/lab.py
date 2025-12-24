import asyncio
import aiohttp
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from datasets import load_dataset

async def translate_text(session, text, source='en', target='ro'):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": source, "tl": target, "dt": "t", "q": text}
    async with session.get(url, params=params) as response:
        data = await response.json()
        return ''.join([t[0] for t in data[0]])

async def main():
    dataset = load_dataset('squad', split='train', cache_dir='./data')
    squad = pd.DataFrame(dataset)
    cols = ["text", "question", "answer"]
    comp_list = []
    for _, row in squad.iterrows():
        comp_list.append([row["context"], row["question"], row["answers"]["text"][0]])
    new_df = pd.DataFrame(comp_list, columns=cols)
    new_df.to_csv("SquAD_data.csv", index=False)
    data = pd.read_csv("SquAD_data.csv")

    model_name = "deepset/bert-base-cased-squad2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)

    use_random = False

    if use_random:
        random_num = np.random.randint(0, len(data))
        text = data["text"][random_num]
        question = data["question"][random_num]
    else:
        text = """New York (CNN) -- More than 80 Michael Jackson collectibles -- including the late pop star's famous rhinestone-studded glove from a 1983 performance -- were auctioned off Saturday, reaping a total $2 million. Profits from the auction at the Hard Rock Cafe in New York's Times Square crushed pre-sale expectations of only $120,000 in sales. The highly prized memorabilia, which included items spanning the many stages of Jackson's career, came from more than 30 fans, associates and family members, who contacted Julien's Auctions to sell their gifts and mementos of the singer. Jackson's flashy glove was the big-ticket item of the night, fetching $420,000 from a buyer in Hong Kong, China. Jackson wore the glove at a 1983 performance during "Motown 25," an NBC special where he debuted his revolutionary moonwalk. Fellow Motown star Walter "Clyde" Orange of the Commodores, who also performed in the special 26 years ago, said he asked for Jackson's autograph at the time, but Jackson gave him the glove instead. "The legacy that [Jackson] left behind is bigger than life for me," Orange said. "I hope that through that glove people can see what he was trying to say in his music and what he said in his music." Orange said he plans to give a portion of the proceeds to charity. Hoffman Ma, who bought the glove on behalf of Ponte 16 Resort in Macau, paid a 25 percent buyer's premium, which was tacked onto all final sales over $50,000. Winners of items less than $50,000 paid a 20 percent premium."""
        question = "Where was the auction held?"

    def question_answer(question, text):
        inputs = tokenizer.encode_plus(question, text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        start_idx = torch.argmax(outputs.start_logits)
        end_idx = torch.argmax(outputs.end_logits) + 1
        answer_tokens = inputs["input_ids"][0][start_idx:end_idx]
        answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
        return answer

    answer = question_answer(question, text)
    if not answer:
        print("I am unable to find the answer to this question.")
        return

    print(f"\nQuestion:\n{question}")
    print(f"\nAnswer:\n{answer}")

    async with aiohttp.ClientSession() as session:
        trans_q, trans_a = await asyncio.gather(
            translate_text(session, question, source='en', target='ro'),
            translate_text(session, answer, source='en', target='ro')
        )
        print(f"\nÎntrebare (tradusă):\n{trans_q.capitalize()}")
        print(f"\nRăspuns (tradus):\n{trans_a.capitalize()}")

    matching_row = data.loc[data["question"] == question]
    if not matching_row.empty:
        print("\nOriginal answer from dataset:\n", matching_row["answer"].values[0])
    else:
        print("\nNo matching question found in the dataset (this is a custom question with a custom context).")

if __name__ == "__main__":
    asyncio.run(main())
