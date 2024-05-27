# from dotenv import load_dotenv

# from examgpt.ai.models.openai import OpenAIConfig
# from examgpt.sources.filetypes.pdf import PDFFile
from examgpt.core.config import settings
from examgpt.frontend.chatbot.chat import start_chat

# assert load_dotenv("./.env")

pdf_file = "testdata/aws2.pdf"


# pdf = PDFFile(pdf_file)
# print(pdf)

# full_text = pdf.create_text()
# model = OpenAIConfig()
# token_count = model.get_token_count(full_text)
# print(f"token count: {token_count}")
# print(model.estimate_cost(token_count))

start_chat(settings.TG_BOT_TOKEN)
