# from examgpt.ai.models.openai import OpenAIConfig
import pickle
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from codenamize import codenamize  # type: ignore
from loguru import logger
from tenacity import retry, stop_after_attempt
from yaml import ScalarNode

from examgpt.ai.aimodel import AIModel
from examgpt.ai.model_providers.llama import LlamaProvider
from examgpt.ai.model_providers.openai import OpenAIProvider
from examgpt.core.config import ApplicationSettings, settings
from examgpt.core.exam import Exam

# from examgpt.frontend.chatbot.chat import start_chat
from examgpt.core.question import QACollection, Scenario
from examgpt.sources.chunkers.base import TextChunk
from examgpt.sources.chunkers.pdf_chunker import SimplePDFChunker
from examgpt.sources.filetypes.base import Source
from examgpt.sources.filetypes.pdf import PDFFile
from examgpt.storage.files import FileStorage
from examgpt.utils.checkpoint import CheckpointService

# settings = ApplicationSettings()  # pyright: ignore

exam_name = "AWS Solution Architect Associate Certification"
# # exam_name = "AWS Certified Solutions Architect - Associate"
pdf_file = "testdata/aws2.pdf"


# create sources
chunker = SimplePDFChunker(chunk_size=2500)

pdf = PDFFile(location=pdf_file, chunker=chunker)
logger.info(pdf.to_dict())

exam = Exam(name=exam_name, sources=[pdf], exam_id="innocent-few")
logger.info(exam)

exam_id = exam.exam_id
logger.info(exam_id)

destination_folder = str(Path(settings.temp_folder) / exam_id)
storage = FileStorage(folder=destination_folder)
storage.copy(sources=exam.sources)

# updated location after copying
logger.info(pdf.to_dict())

chunks = pdf.chunk()
storage.save_to_json(data=exam.to_dict(), filename="chunks.json")
# logger.info(f"Length of whole document: {pdf.full_text} characters")

## Create an exam object

folder = str(Path(settings.temp_folder) / exam_id)
storage = FileStorage(folder=folder)
# CheckpointService(folder=folder)
exam = storage.get_exam(location="chunks.json")
exam_name = exam.name
source = exam.sources[0]
# source.limit_chunks(6)  # for testing

model = AIModel(model_provider=OpenAIProvider())


# class Model:
#     def get_answer(self, chunk: TextChunk):
#         return f"Processed_{chunk.id}"


# @dataclass
# class ChunkProcessor:
#     chunks: list[TextChunk]
#     model: Model

#     def process_chunks_lf(self):
#         for i, chunk in enumerate(self.chunks):
#             logger.info(f"Processing {i}: {chunk.id}")
#             result = self.get_answer(
#                 id=chunk.id,
#                 chunk=chunk,
#                 model=self.model,
#                 scenario=Scenario.LONGFORM.value,
#             )
#             print(f"Result: {result}")

#     def process_chunks_mc(self):
#         for i, chunk in enumerate(self.chunks):
#             logger.info(f"Processing {i}: {chunk.id}")
#             result = self.get_answer(
#                 id=chunk.id,
#                 chunk=chunk,
#                 model=self.model,
#                 scenario=Scenario.MULTIPLECHOICE.value,
#             )
#             print(f"Result: {result}")

#     @CheckpointService.checkpoint
#     def get_answer(self, id: str, chunk: TextChunk, model: Model, scenario: str):
#         time.sleep(1)
#         return model.get_answer(chunk)


# model = Model()
# CheckpointService.init(destination_folder)
# chunk_processor = ChunkProcessor(source.chunks, model)
# chunk_processor.process_chunks_lf()
# chunk_processor.process_chunks_mc()
# CheckpointService.delete_checkpoint()


# chunk = source.chunks[3]
# response = model.generate_longform_qa(chunk=chunk, exam_name=exam_name)
# response = model.generate_multiplechoice_qa(chunk=chunk, exam_name=exam_name)
# response = model._context_check(chunk=chunk.text, exam_name=exam_name)
# print(response)


# CheckpointService.init(destination_folder)
# qa_collection = source.get_qa_collection(exam_id, exam_name, model)
# # TODO: remove empty QA after done.
# CheckpointService.delete_checkpoint()


@retry(stop=stop_after_attempt(10))
def get_qa_collection(exam_id: str, exam_name: str, model: AIModel):
    qa_collection = source.get_qa_collection(exam_id, exam_name, model)
    return qa_collection


CheckpointService.init(destination_folder)
qa_collection = get_qa_collection(exam_id, exam_name, model)
CheckpointService.delete_checkpoint()
print(qa_collection)
storage.save_to_json(data=qa_collection.to_dict(), filename="answers.json")

# qac = storage.get_qa_collection("answers.json")

# create exam


# full_text = pdf.create_text()
# model = OpenAIConfig()
# token_count = model.get_token_count(full_text)
# print(f"token count: {token_count}")
# print(model.estimate_cost(token_count))

# start_chat(settings.TG_BOT_TOKEN)

# codenamize test

print(codenamize(str(uuid4())))
