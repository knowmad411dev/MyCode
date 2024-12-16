import os
import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def format_text(text):
    # Split the text into lines
    lines = text.split('\n')
    formatted_text = []
    
    for line in lines:
        # Remove any leading or trailing whitespace
        line = line.strip()
        if line:
            # Split the line into words and levels (e.g., n.C1, adj.B2)
            parts = line.split()
            if len(parts) > 0:
                # Only take the first part (the word)
                word = parts[0]
                formatted_text.append(word)
    
    return '\n'.join(formatted_text)

def main():
    # Define the input and output file paths
    input_folder = r'c:\Users\toddk\Documents'
    input_pdf_path = os.path.join(input_folder, 'The_Oxford_5000.pdf')
    output_txt_path = os.path.join(input_folder, 'The_Oxford_5000_cleaned.txt')
    
    # Extract text from the PDF
    text = extract_text_from_pdf(input_pdf_path)
    
    # Format the text by removing levels (e.g., v.C1, n.B2)
    formatted_text = format_text(text)
    
    # Save the formatted text to the output file
    with open(output_txt_path, 'w') as output_file:
        output_file.write(formatted_text)
    
    print(f"Text extraction and formatting complete. Output saved to '{output_txt_path}'.")

if __name__ == "__main__":
    main()