import re
import json
import string
from collections import Counter 

class TextProcessor:
    def __init__(self, file_path, output_json):
        """ Initialize variables """
        self.file_path = file_path
        self.output_json = output_json
        # Add a list of stop words in Persian (students can expand it)
        self.stop_words = set([
            "و", "در", "به", "از", "که", "این", "را", "با", "است", "برای",
            "آن", "یک", "هم", "تا", "نیز", "اما", "یا", "بر", "اگر", "هر",
            "چون", "باید", "می", "شد", "کند", "کرد", "شده", "دیگر", "همه"
        ])

    def read_file(self):
        """ Read content from the text file """
        # Student should complete: Open and read the file
        self.file = open(self.file_path, 'r', encoding='utf-8')
        self.file_content = self.file.read()
        self.close_file()  # call the close file function
        return self.file_content

    def clean_text(self, text):
        """ Clean the text: remove emails, URLs, and punctuation """
        # Student should complete: Use regex to remove URLs and emails
        # Example for URLs: r"https?://\S+|www\.\S+"
        url_pattern = r"https?://\S+|www\.\S+"
        text = re.sub(url_pattern, "", text)
        # Example for emails: r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        text = re.sub(email_pattern, "", text)
        # Remove punctuation as well
        text = re.sub(r"[^\w\s]", "", text)  # removes everything except from characters, digits, whitespaces, underscore
        return text

    def remove_stopwords(self, words):
        """ Remove common stop words """
        # Student should complete: Remove stop words from the list
        text_without_stopwords_list = [word for word in words if word not in self.stop_words]
        text_without_stopwords_str = " ".join(text_without_stopwords_list)
        return text_without_stopwords_list

    def count_word_frequencies(self, words):
        """ Count the frequency of each word """
        # Student should complete: Count word frequencies using Counter
        word_counts = Counter(words)
        word_dict = dict(word_counts)
        return word_dict
        

    def save_to_json(self, word_counts):
        """ Save the word frequencies to a JSON file """
        # Student should complete: Write the word counts dictionary to a JSON file
        with open('word_frequencies.json', 'w', encoding="utf-8") as file:
            json.dump(word_counts, file, ensure_ascii=False, indent=4)

    def close_file(self):
        self.file.close()

    def process(self):
        """ Process the text through all the stages """
        text = self.read_file()  # Step 1: Read the file
        cleaned_text = self.clean_text(text)  # Step 2: Clean the text
        words = cleaned_text.split()  # Step 3: Tokenize into words
        filtered_words = self.remove_stopwords(words)  # Step 4: Remove stopwords
        word_counts = self.count_word_frequencies(filtered_words)  # Step 5: Count frequencies
        self.save_to_json(word_counts)  # Step 6: Save the results
        print(f"Processing complete! Output saved to {self.output_json}")

# Example usage
processor = TextProcessor("input.txt", "word_frequencies.json")
processor.process()
