import re
import json
import string

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
        pass

    def clean_text(self, text):
        """ Clean the text: remove emails, URLs, and punctuation """
        # Student should complete: Use regex to remove URLs and emails
        # Example for URLs: r"https?://\S+|www\.\S+"
        # Example for emails: r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        # Remove punctuation as well
        pass

    def remove_stopwords(self, words):
        """ Remove common stop words """
        # Student should complete: Remove stop words from the list
        pass

    def count_word_frequencies(self, words):
        """ Count the frequency of each word """
        # Student should complete: Count word frequencies using Counter
        pass

    def save_to_json(self, word_counts):
        """ Save the word frequencies to a JSON file """
        # Student should complete: Write the word counts dictionary to a JSON file
        pass

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
