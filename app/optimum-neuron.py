from transformers import AutoTokenizer
from optimum.neuron import NeuronModelForSequenceClassification

model = NeuronModelForSequenceClassification.from_pretrained("distilbert_base_uncased_finetuned_sst2_english_neuron")

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
inputs = tokenizer("Hamilton is considered to be the best musical of past years.", return_tensors="pt")
logits = model(**inputs).logits
print(model.config.id2label[logits.argmax().item()])
