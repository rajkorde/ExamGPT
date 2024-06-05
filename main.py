# from examgpt.ai.models.openai import OpenAIConfig
import pickle
from pathlib import Path

from loguru import logger
from tenacity import retry, stop_after_attempt

from examgpt.ai.aimodel import AIModel
from examgpt.ai.model_providers.llama import LlamaProvider
from examgpt.ai.model_providers.openai import OpenAIProvider
from examgpt.core.config import ApplicationSettings
from examgpt.core.exam import Exam

# from examgpt.frontend.chatbot.chat import start_chat
from examgpt.core.question import QACollection
from examgpt.sources.chunkers.pdf_chunker import SimplePDFChunker
from examgpt.sources.filetypes.pdf import PDFFile
from examgpt.storage.files import FileStorage
from examgpt.utils.checkpoint import CheckpointService

settings = ApplicationSettings()  # pyright: ignore

# exam_name = "AWS Solution Architect Associate Certification"
# # exam_name = "AWS Certified Solutions Architect - Associate"
# pdf_file = "testdata/aws2.pdf"


# # create sources
# chunker = SimplePDFChunker(chunk_size=2500)

# pdf = PDFFile(location=pdf_file, chunker=chunker)
# logger.info(pdf)

# exam = Exam(name=exam_name, sources=[pdf])
# logger.info(exam)

# destination_folder = str(Path(settings.temp_folder) / exam.exam_id)
# storage = FileStorage(folder=destination_folder)
# storage.copy(sources=exam.sources)

# # updated location after copying
# logger.info(pdf)

# chunks = pdf.chunk()

# storage.save_to_json(data=exam.to_dict(), filename="chunks.json")
# logger.info(f"Length of whole document: {pdf.full_text} characters")

## Create an exam object

exam_id = "0329ee78-f01a-4617-8796-914e44b47ad1"
folder = str(Path(settings.temp_folder) / exam_id)
storage = FileStorage(folder=folder)
CheckpointService(folder=folder)
exam = storage.get_exam(location="chunks.json")
exam_name = exam.name
source = exam.sources[0]
# source.limit_chunks()

model = AIModel(model_provider=OpenAIProvider())


# chunk = source.chunks[14]
# response = model.generate_longform_qa(chunk=chunk.text, exam_name=exam_name)
# response = model.generate_multiplechoice_qa(chunk=chunk, exam_name=exam_name)
# response = model._context_check(chunk=chunk.text, exam_name=exam_name)
# print(response)


# qa_collection = source.get_qa_collection(exam_id, exam_name, model)
@retry(stop=stop_after_attempt(10))
def get_qa_collection(exam_id: str, exam_name: str, model: AIModel):
    qa_collection = source.get_qa_collection(exam_id, exam_name, model)
    return qa_collection


qa_collection = get_qa_collection(exam_id, exam_name, model)
print(qa_collection)


d = pickle.load(
    Path("temp/0329ee78-f01a-4617-8796-914e44b47ad1/checkpoints/checkpoint.pkl").open(
        "rb"
    )
)

storage.save_to_json(data=qa_collection.to_dict(), filename="answers.json")


# create exam


# full_text = pdf.create_text()
# model = OpenAIConfig()
# token_count = model.get_token_count(full_text)
# print(f"token count: {token_count}")
# print(model.estimate_cost(token_count))

# start_chat(settings.TG_BOT_TOKEN)
