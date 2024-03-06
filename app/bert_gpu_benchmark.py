from transformers import BertTokenizer, BertForQuestionAnswering
import torch
import time
import math

# Define model name and tokenizer
model_name = "bert-base-uncased"
task = "question-answering"
# Load tokenizer and model
tokenizer = BertTokenizer.from_pretrained(model_name)
# Load model and move to GPU
model = BertForQuestionAnswering.from_pretrained(model_name).cuda()

# Define benchmark parameters
n_runs = 1000

# Define sample question and context
question = "What is the capital of France?"
context = "France is a country located in Western Europe. Its capital is Paris."
context = "The French Republic is a country located in Western Europe; the capital city of its republic is Paris, which is located in the heart of the French Republic. France is considered to be a developed country and has the fifth-largest economy in the world. It is also a member of the G20 and a founding member of the European Union. France is also a member of the United Nations, NATO, and other international organizations."
context = "The French Republic is a country located in Western Europe; the capital city of its republic is Paris, which is located in the heart of the French Republic. France is considered to be a developed country and has the fifth-largest economy in the world. It is also a member of the G20 and a founding member of the European Union. France is also a member of the United Nations, NATO, and other international organizations. France is a popular tourist destination and is home to some of the world's most famous landmarks. French cuisine is also renowned for its excellence and sophistication. France is also renowned for its wine and fashion industries. French culture and art are also highly respected around the world. French citizens are also known for their strong sense of patriotism and loyalty to their country. France is also a leader in scientific research and technology. France is also a founding member of the European Union and the United Nations. France is also a founding member of the Francophonie, an organization of Francophone countries. All in all, France is a country renowned for its culture, people, and accomplishments."
context = "The French Republic is a country located in Western Europe; the capital city of its republic is Paris, which is located in the heart of the French Republic. France is considered to be a developed country and has the fifth-largest economy in the world. It is also a member of the G20 and a founding member of the European Union. France is also a member of the United Nations, NATO, and other international organizations. France is a popular tourist destination and is home to some of the world's most famous landmarks. French cuisine is also renowned for its excellence and sophistication. France is also renowned for its wine and fashion industries. French culture and art are also highly respected around the world. French citizens are also known for their strong sense of patriotism and loyalty to their country. France is also a leader in scientific research and technology. France is also a founding member of the European Union and the United Nations. France is also a founding member of the Francophonie, an organization of Francophone countries. All in all, France is a country renowned for its culture, people, and accomplishments. France is also known for its rich history, with many iconic landmarks and monuments that attract millions of tourists every year. France is also a country renowned for its cuisine, with a wide range of traditional dishes that are enjoyed around the world. All in all, France is a country that is rightfully proud of its past, present, and future. However, France is also a country with a lot of problems. France has a high unemployment rate, and the French government is struggling to find ways to create jobs. France also has a high level of public debt, and the French government is struggling to find ways to pay off its debt."
context = "The French Republic is a country located in Western Europe; the capital city of its republic is Paris, which is located in the heart of the French Republic. France is considered to be a developed country and has the fifth-largest economy in the world. It is also a member of the G20 and a founding member of the European Union. France is also a member of the United Nations, NATO, and other international organizations. France is a popular tourist destination and is home to some of the world's most famous landmarks. French cuisine is also renowned for its excellence and sophistication. France is also renowned for its wine and fashion industries. French culture and art are also highly respected around the world. French citizens are also known for their strong sense of patriotism and loyalty to their country. France is also a leader in scientific research and technology. France is also a founding member of the European Union and the United Nations. France is also a founding member of the Francophonie, an organization of Francophone countries. All in all, France is a country renowned for its culture, people, and accomplishments. France is also known for its rich history, with many iconic landmarks and monuments that attract millions of tourists every year. France is also a country renowned for its cuisine, with a wide range of traditional dishes that are enjoyed around the world. All in all, France is a country that is rightfully proud of its past, present, and future. However, France is also a country with a lot of problems. France has a high unemployment rate, and the French government is struggling to find ways to create jobs. France also has a high level of public debt, and the French government is struggling to find ways to pay off its debt. France is also facing a wave of terrorist attacks, and the French government is struggling to keep its citizens safe. Despite all of these problems, France remains a strong nation, with a proud history, a strong economy, and a strong sense of national identity. France is also a country that is unified in its resolve to address its problems, and is taking steps to do so. The government is also working to create jobs, reduce poverty, and improve public services. It is also committed to protecting the environment and promoting renewable energy sources. France is a nation that is determined to overcome its challenges and build a brighter future for its citizens."
# Generate random input data
inputs = tokenizer(question, context, return_tensors="pt").to(model.device)

# Benchmark method
def benchmark(n_runs, test_name, model, model_inputs):
    warmup_run = model(**model_inputs)
    latency_collector = LatencyCollector()

    for _ in range(n_runs):
        latency_collector.pre_hook()
        res = model(**model_inputs)
        #print(f'res={res}')
        latency_collector.hook()

    p0_latency_ms = latency_collector.percentile(0) * 1000
    p50_latency_ms = latency_collector.percentile(50) * 1000
    p90_latency_ms = latency_collector.percentile(90) * 1000
    p95_latency_ms = latency_collector.percentile(95) * 1000
    p99_latency_ms = latency_collector.percentile(99) * 1000
    p100_latency_ms = latency_collector.percentile(100) * 1000

    report_dict = dict()
    report_dict["Latency P0"] = f'{p0_latency_ms:.1f}'
    report_dict["P50"]=f'{p50_latency_ms:.1f}'
    report_dict["P90"]=f'{p90_latency_ms:.1f}'
    report_dict["P95"]=f'{p95_latency_ms:.1f}'
    report_dict["P99"]=f'{p99_latency_ms:.1f}'
    report_dict["P100"]=f'{p100_latency_ms:.1f}'

    report = f'RESULT FOR {test_name}; n_runs {n_runs}:'
    for key, value in report_dict.items():
        report += f' {key}={value}'
    print(report)

class LatencyCollector:
    def __init__(self):
        self.start = None
        self.latency_list = []

    def pre_hook(self, *args):
        self.start = time.time()

    def hook(self, *args):
        self.latency_list.append(time.time() - self.start)

    def percentile(self, percent):
        latency_list = self.latency_list
        pos_float = len(latency_list) * percent / 100
        max_pos = len(latency_list) - 1
        pos_floor = min(math.floor(pos_float), max_pos)
        pos_ceil = min(math.ceil(pos_float), max_pos)
        latency_list = sorted(latency_list)
        return latency_list[pos_ceil] if pos_float - pos_floor > 0.5 else latency_list[pos_floor]

benchmark(n_runs,model_name,model,inputs)
