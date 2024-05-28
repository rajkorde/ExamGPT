# from examgpt.ai.models.openai import OpenAIConfig
from pathlib import Path

from loguru import logger

from examgpt.core.config import ApplicationSettings
from examgpt.core.exam import Exam

# from examgpt.frontend.chatbot.chat import start_chat
from examgpt.sources.filetypes.base import Sources
from examgpt.sources.filetypes.pdf import PDFFile
from examgpt.storage.files import FileStorage

settings = ApplicationSettings()  # pyright: ignore

exam_name = "AWS Solution Architect Associate Certification"
# exam_name = "AWS Certified Solutions Architect - Associate"
pdf_file = "testdata/aws2.pdf"

# create sources

pdf = PDFFile(pdf_file)
logger.info(pdf)

sources = Sources(sources=[pdf])
exam = Exam(name=exam_name, sources=sources)
logger.info(exam)

destination_folder = str(Path(settings.temp_folder) / exam.exam_id)
storage = FileStorage(destination_folder=destination_folder)
storage.copy(sources=sources.to_list())

# create exam


# full_text = pdf.create_text()
# model = OpenAIConfig()
# token_count = model.get_token_count(full_text)
# print(f"token count: {token_count}")
# print(model.estimate_cost(token_count))

# start_chat(settings.TG_BOT_TOKEN)
