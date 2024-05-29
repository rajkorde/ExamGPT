# from examgpt.ai.models.openai import OpenAIConfig
from pathlib import Path

from loguru import logger

from examgpt.core.config import ApplicationSettings
from examgpt.core.exam import Exam

# from examgpt.frontend.chatbot.chat import start_chat
from examgpt.sources.chunkers.pdf_chunker import SimplePDFChunker
from examgpt.sources.filetypes.pdf import PDFFile
from examgpt.storage.files import FileStorage

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
destination_folder = str(Path(settings.temp_folder) / exam_id)
storage = FileStorage(folder=destination_folder)
storage.copy(sources=exam.sources)

# create exam


# full_text = pdf.create_text()
# model = OpenAIConfig()
# token_count = model.get_token_count(full_text)
# print(f"token count: {token_count}")
# print(model.estimate_cost(token_count))

# start_chat(settings.TG_BOT_TOKEN)
