from unstructured.partition.pdf import partition_pdf
from unstructured.partition.text import partition_text
from rag_modules.conversational_bot import Conversational_Bot
from tqdm import tqdm
import unstructured, os

def data_extracter(data, file_type, bot: Conversational_Bot = None):
    try:
        if file_type == 'pdf':
            if bot is None: ValueError("No bot provided.") 
            texts, tables, images = [], [], []
            
            for chunk in data:
                if isinstance(chunk, unstructured.documents.elements.Table):
                    tables.append(chunk)
                if isinstance(chunk, unstructured.documents.elements.CompositeElement):
                    texts.append(str(chunk))
                    chunk_elements = chunk.metadata.orig_elements
                    for element in chunk_elements:
                        if isinstance(element, unstructured.documents.elements.Image):
                            images.append(element.metadata.image_base64)
                            
            print(f"Total Texts: {len(texts)} Total Images: {len(images)} Total Tables: {len(tables)}")
            
            print("Processing Images...")
            image_summaries = [bot.summarize_image(images[i]) for i in tqdm(range(len(images)))]
            
            print("Processing Tables...")
            table_summaries = [bot.summarize_table(tables[i].metadata.text_as_html) for i in tqdm(range(len(tables)))]
            
            return texts, image_summaries, table_summaries
        elif file_type == 'text':
            texts = []
            
            for chunk in data:
                if isinstance(chunk, unstructured.documents.elements.CompositeElement):
                    texts.append(chunk)
                            
            print(f"Total Texts: {len(texts)}")
            return texts
        elif file_type == 'image':
            image_summary = bot.summarize_image(data)
            return image_summary
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None
    
def extract_pdf_data(file_path=None, file=None, bot: Conversational_Bot = None):
    try:
        if bot is None: ValueError("No bot provided.") 
        if file_path:
            print(f'File path provided: {file_path}')
            if not os.path.exists(file_path): raise Exception("File does not exist: {file_path}")
            chunks = partition_pdf(
                filename=file_path,
                infer_table_structure=True,
                strategy="hi_res",
                extract_image_block_types=["Image"],
                extract_image_block_to_payload=True,
                chunking_strategy="by_title",
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000
                )
        elif file:
            print(f'File provided')
            chunks = partition_pdf(
                file=file,
                infer_table_structure=True,
                strategy="hi_res",
                extract_image_block_types=["Image"],
                extract_image_block_to_payload=True,
                chunking_strategy="by_title",
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000
                )
        else:
            raise ValueError("No file path / file provided.")
        
        extracted_data = data_extracter(data=chunks, file_type='pdf', bot=bot)
        
        if extracted_data: texts, image_summaries, table_summaries = extracted_data
        else: raise Exception("Failed to extract data.")
        
        return texts, image_summaries, table_summaries
    except Exception as e:
        print(f"Error extracting PDF data: {e}")
        return None
    
def extract_txt_data(file_path=None, file=None):
    try:
        if file_path:
            print(f'File path provided: {file_path}')
            if not os.path.exists(file_path): raise Exception("File does not exist: {file_path}")
            chunks = partition_text(
                filename=file_path,
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000
                )
        elif file:
            print(f'File provided')
            chunks = partition_text(
                file=file,
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000
                )
        else:
            raise ValueError("No file path / file provided.")
        
        extracted_data = data_extracter(data=chunks, file_type='text')
        
        if extracted_data: texts = extracted_data
        else: raise Exception("Failed to extract data.")
        
        return texts
    except Exception as e:
        print(f"Error extracting text data: {e}")
        return None
    
def extract_image_data(file_path=None, file=None, bot: Conversational_Bot = None):
    try:
        if bot is None: ValueError("No bot provided.") 
        
        if file_path:
            print(f'File path provided: {file_path}')
            if not os.path.exists(file_path): raise Exception("File does not exist: {file_path}")
            extracted_data = data_extracter(data=file_path, file_type='image', bot=bot)
        elif file:
            extracted_data = data_extracter(data=file, file_type='image', bot=bot)
        else:
            raise ValueError("No file path / file provided.")

        if extracted_data: image_summary = extracted_data
        else: raise Exception("Failed to extract data.")
        
        return image_summary
    except Exception as e:
        print(f"Error extracting image data: {e}")
        return None
    
if __name__ == '__main__':
    bot = Conversational_Bot()
    extracted_data = extract_pdf_data(file_path='pdf_file.pdf', bot=bot)
    if extracted_data:
        texts, images, tables = extracted_data
        print(f"texts: {texts[0] if texts and len(texts) else []}")
        print(f"images: {images[0] if images and len(images) else []}")
        print(f"tables: {tables[0] if tables and len(tables) else []}")
    else:
        print("Failed to display extract data.")
        
    extracted_data = extract_txt_data(file_path='text_file.txt')
    if extracted_data:
        texts = extracted_data
        print(f"texts: {texts[0] if texts and len(texts) else []}")
    else:
        print("Failed to display extract data.")
        
    extracted_data = extract_image_data(file_path='image.jpg', bot=bot)
    if extracted_data:
        print(extracted_data)
    else:
        print("Failed to display extract data.")
        